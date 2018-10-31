# Copyright (C) 2011-2013 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import concurrent.futures
import functools
import sys
import threading
import time

import keystoneauth1.exceptions
import six
from six.moves import queue

import openstack._log
from openstack import exceptions

_log = openstack._log.setup_logging('openstack.task_manager')


class Task(object):
    """Represent a remote task to be performed on an OpenStack Cloud.

    Some consumers need to inject things like rate-limiting or auditing
    around each external REST interaction. Task provides an interface
    to encapsulate each such interaction. Also, although shade itself
    operates normally in a single-threaded direct action manner, consuming
    programs may provide a multi-threaded TaskManager themselves. For that
    reason, Task uses threading events to ensure appropriate wait conditions.
    These should be a no-op in single-threaded applications.

    A consumer is expected to overload the main method.

    :param dict kw: Any args that are expected to be passed to something in
                    the main payload at execution time.
    """

    def __init__(
            self, main=None, name=None, run_async=False,
            tag=None, *args, **kwargs):
        self._exception = None
        self._traceback = None
        self._result = None
        self._response = None
        self._finished = threading.Event()
        self._main = main
        self._run_async = run_async
        self.args = args
        self.kwargs = kwargs
        self.name = name or type(self).__name__
        self.tag = tag

    def main(self):
        return self._main(*self.args, **self.kwargs)

    @property
    def run_async(self):
        return self._run_async

    def done(self, result):
        self._result = result
        self._finished.set()

    def exception(self, e, tb):
        self._exception = e
        self._traceback = tb
        self._finished.set()

    def wait(self, raw=False):
        self._finished.wait()

        if self._exception:
            six.reraise(type(self._exception), self._exception,
                        self._traceback)

        return self._result

    def run(self):
        try:
            # Retry one time if we get a retriable connection failure
            try:
                self.done(self.main())
            except keystoneauth1.exceptions.RetriableConnectionFailure:
                self.done(self.main())
        except Exception as e:
            self.exception(e, sys.exc_info()[2])


class TaskManager(object):

    def __init__(self, name, rate=None, log=_log, workers=5, **kwargs):
        self.name = name
        self._executor = None
        self._log = log
        self._workers = workers
        self.daemon = True
        self.queue = queue.Queue()
        self._running = True
        if isinstance(rate, dict):
            self._waits = {}
            for (k, v) in rate.items():
                if v:
                    self._waits[k] = 1.0 / v
        else:
            if rate:
                self._waits = {None: 1.0 / rate}
            else:
                self._waits = {}
        self._thread = threading.Thread(name=name, target=self.run)
        self._thread.daemon = True

    def _get_wait(self, tag):
        return self._waits.get(tag, self._waits.get(None))

    @property
    def executor(self):
        if not self._executor:
            self._executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=self._workers)
        return self._executor

    def start(self):
        self._thread.start()

    def stop(self):
        self._running = False
        self.queue.put(None)
        if self._executor:
            self._executor.shutdown()

    def join(self):
        self._thread.join()

    def run(self):
        last_ts_dict = {}
        try:
            while True:
                task = self.queue.get()
                if not task:
                    if not self._running:
                        break
                    continue
                wait = self._get_wait(task.tag)
                if wait:
                    last_ts = last_ts_dict.get(task.tag, 0)
                    while True:
                        delta = time.time() - last_ts
                        if delta >= wait:
                            break
                        time.sleep(wait - delta)
                    last_ts_dict[task.tag] = time.time()
                self._log.debug(
                    "TaskManager {name} queue size: {size})".format(
                        name=self.name,
                        size=self.queue.qsize()))
                self.run_task(task)
                self.queue.task_done()
        except Exception:
            self._log.exception("TaskManager died")
            raise

    def submit_task(self, task):
        """Submit and execute the given task.

        :param task: The task to execute.
        :param bool raw: If True, return the raw result as received from the
            underlying client call.

        This method calls task.wait() so that it only returns when the
        task is complete.
        """
        if not self._running:
            raise exceptions.TaskManagerStopped(
                "TaskManager {name} is no longer running".format(
                    name=self.name))
        self.pre_run_task(task)
        start = time.time()
        self.queue.put(task)
        ret = task.wait()
        end = time.time()
        dt = end - start
        self.post_run_task(dt, task)
        return ret

    def submit_function(
            self, method, name=None, run_async=False, tag=None,
            *args, **kwargs):
        """ Allows submitting an arbitrary method for work.

        :param method: Callable to run in the TaskManager.
        :param str name: Name to use for the generated Task object.
        :param bool run_async: Whether to run this task async or not.
        :param str tag: Named rate-limiting context for the task.
        :param args: positional arguments to pass to the method when it runs.
        :param kwargs: keyword arguments to pass to the method when it runs.
        """
        if run_async:
            payload = functools.partial(
                self.executor.submit, method, *args, **kwargs)
            task = Task(
                main=payload, name=name,
                run_async=run_async,
                tag=tag)
        else:
            task = Task(
                main=method, name=name,
                tag=tag,
                *args, **kwargs)
        return self.submit_task(task)

    def submit_function_async(self, method, name=None, *args, **kwargs):
        """ Allows submitting an arbitrary method for async work scheduling.

        :param method: Callable to run in the TaskManager.
        :param str name: Name to use for the generated Task object.
        :param args: positional arguments to pass to the method when it runs.
        :param kwargs: keyword arguments to pass to the method when it runs.
        """
        return self.submit_function(
            method, name=name, run_async=True, *args, **kwargs)

    def pre_run_task(self, task):
        '''Callback when task enters the task queue

        :param task: the task

        Intended to be overridden by child classes to track task
        progress.
        '''
        self._log.debug(
            "Manager %s running task %s", self.name, task.name)

    def run_task(self, task):
        # Never call task.wait() in the run_task call stack because we
        # might be running in another thread.  The exception-shifting
        # code is designed so that caller of submit_task (which may be
        # in a different thread than this run_task) gets the
        # exception.
        #
        # Note all threads go through the threadpool, so this is an
        # async call.  submit_task will wait() for the final result.
        task.run()

    def post_run_task(self, elapsed_time, task):
        '''Callback at task completion

        :param float elapsed_time: time in seconds between task entering
            queue and finishing
        :param task: the task

        This function is intended to be overridden by child classes to
        monitor task runtimes.
        '''
        self._log.debug(
            "Manager %s ran task %s in %ss",
            self.name, task.name, elapsed_time)


def wait_for_futures(futures, raise_on_error=True, log=_log):
    '''Collect results or failures from a list of running future tasks.'''

    results = []
    retries = []

    # Check on each result as its thread finishes
    for completed in concurrent.futures.as_completed(futures):
        try:
            result = completed.result()
            exceptions.raise_from_response(result)
            results.append(result)
        except (keystoneauth1.exceptions.RetriableConnectionFailure,
                exceptions.HttpException) as e:
            log.exception(
                "Exception processing async task: {e}".format(e=str(e)))
            if raise_on_error:
                raise
            # If we get an exception, put the result into a list so we
            # can try again
            retries.append(completed.result())
    return results, retries
