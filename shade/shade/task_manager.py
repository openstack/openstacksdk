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
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.

import abc
import concurrent.futures
import sys
import threading
import time
import types

import keystoneauth1.exceptions
import simplejson
import six

from shade import _log
from shade import exc
from shade import meta


def _is_listlike(obj):
    # NOTE(Shrews): Since the client API might decide to subclass one
    # of these result types, we use isinstance() here instead of type().
    return (
        isinstance(obj, list) or
        isinstance(obj, types.GeneratorType))


def _is_objlike(obj):
    # NOTE(Shrews): Since the client API might decide to subclass one
    # of these result types, we use isinstance() here instead of type().
    return (
        not isinstance(obj, bool) and
        not isinstance(obj, int) and
        not isinstance(obj, float) and
        not isinstance(obj, six.string_types) and
        not isinstance(obj, set) and
        not isinstance(obj, tuple))


@six.add_metaclass(abc.ABCMeta)
class BaseTask(object):
    """Represent a task to be performed on an OpenStack Cloud.

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

    def __init__(self, **kw):
        self._exception = None
        self._traceback = None
        self._result = None
        self._response = None
        self._finished = threading.Event()
        self.run_async = False
        self.args = kw
        self.name = type(self).__name__

    @abc.abstractmethod
    def main(self, client):
        """ Override this method with the actual workload to be performed """

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

    def run(self, client):
        self._client = client
        try:
            # Retry one time if we get a retriable connection failure
            try:
                # Keep time for connection retrying logging
                start = time.time()
                self.done(self.main(client))
            except keystoneauth1.exceptions.RetriableConnectionFailure as e:
                end = time.time()
                dt = end - start
                if client.region_name:
                    client.log.debug(str(e))
                    client.log.debug(
                        "Connection failure on %(cloud)s:%(region)s"
                        " for %(name)s after %(secs)s seconds, retrying",
                        {'cloud': client.name,
                         'region': client.region_name,
                         'secs': dt,
                         'name': self.name})
                else:
                    client.log.debug(
                        "Connection failure on %(cloud)s for %(name)s after"
                        " %(secs)s seconds, retrying",
                        {'cloud': client.name, 'name': self.name, 'secs': dt})
                self.done(self.main(client))
            except Exception:
                raise
        except Exception as e:
            self.exception(e, sys.exc_info()[2])


class Task(BaseTask):
    """ Shade specific additions to the BaseTask Interface. """

    def wait(self, raw=False):
        super(Task, self).wait()

        if raw:
            # Do NOT convert the result.
            return self._result

        if _is_listlike(self._result):
            return meta.obj_list_to_munch(self._result)
        elif _is_objlike(self._result):
            return meta.obj_to_munch(self._result)
        else:
            return self._result


class RequestTask(BaseTask):
    """ Extensions to the Shade Tasks to handle raw requests """

    # It's totally legit for calls to not return things
    result_key = None

    # keystoneauth1 throws keystoneauth1.exceptions.http.HttpError on !200
    def done(self, result):
        self._response = result

        try:
            result_json = self._response.json()
        except (simplejson.scanner.JSONDecodeError, ValueError) as e:
            result_json = self._response.text
            self._client.log.debug(
                'Could not decode json in response: %(e)s', {'e': str(e)})
            self._client.log.debug(result_json)

        if self.result_key:
            self._result = result_json[self.result_key]
        else:
            self._result = result_json

        self._request_id = self._response.headers.get('x-openstack-request-id')
        self._finished.set()

    def wait(self, raw=False):
        super(RequestTask, self).wait()

        if raw:
            # Do NOT convert the result.
            return self._result

        if _is_listlike(self._result):
            return meta.obj_list_to_munch(
                self._result, request_id=self._request_id)
        elif _is_objlike(self._result):
            return meta.obj_to_munch(self._result, request_id=self._request_id)
        return self._result


def _result_filter_cb(result):
    return result


def generate_task_class(method, name, result_filter_cb):
    if name is None:
        if callable(method):
            name = method.__name__
        else:
            name = method

    class RunTask(Task):
        def __init__(self, **kw):
            super(RunTask, self).__init__(**kw)
            self.name = name
            self._method = method

        def wait(self, raw=False):
            super(RunTask, self).wait()

            if raw:
                # Do NOT convert the result.
                return self._result
            return result_filter_cb(self._result)

        def main(self, client):
            if callable(self._method):
                return method(**self.args)
            else:
                meth = getattr(client, self._method)
                return meth(**self.args)
    return RunTask


class TaskManager(object):
    log = _log.setup_logging('shade.task_manager')

    def __init__(
            self, client, name, result_filter_cb=None, workers=5, **kwargs):
        self.name = name
        self._client = client
        self._executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=workers)
        if not result_filter_cb:
            self._result_filter_cb = _result_filter_cb
        else:
            self._result_filter_cb = result_filter_cb

    def set_client(self, client):
        self._client = client

    def stop(self):
        """ This is a direct action passthrough TaskManager """
        self._executor.shutdown(wait=True)

    def run(self):
        """ This is a direct action passthrough TaskManager """
        pass

    def submit_task(self, task, raw=False):
        """Submit and execute the given task.

        :param task: The task to execute.
        :param bool raw: If True, return the raw result as received from the
            underlying client call.
        """
        return self.run_task(task=task, raw=raw)

    def _run_task_async(self, task, raw=False):
        self.log.debug(
            "Manager %s submitting task %s", self.name, task.name)
        return self._executor.submit(self._run_task, task, raw=raw)

    def run_task(self, task, raw=False):
        if hasattr(task, 'run_async') and task.run_async:
            return self._run_task_async(task, raw=raw)
        else:
            return self._run_task(task, raw=raw)

    def _run_task(self, task, raw=False):
        self.log.debug(
            "Manager %s running task %s", self.name, task.name)
        start = time.time()
        task.run(self._client)
        end = time.time()
        dt = end - start
        self.log.debug(
            "Manager %s ran task %s in %ss", self.name, task.name, dt)

        self.post_run_task(dt, task)

        return task.wait(raw)

    def post_run_task(self, elasped_time, task):
        pass

    # Backwards compatibility
    submitTask = submit_task

    def submit_function(
            self, method, name=None, result_filter_cb=None, **kwargs):
        """ Allows submitting an arbitrary method for work.

        :param method: Method to run in the TaskManager. Can be either the
                       name of a method to find on self.client, or a callable.
        """
        if not result_filter_cb:
            result_filter_cb = self._result_filter_cb

        task_class = generate_task_class(method, name, result_filter_cb)

        return self._executor.submit_task(task_class(**kwargs))


def wait_for_futures(futures, raise_on_error=True, log=None):
    '''Collect results or failures from a list of running future tasks.'''

    results = []
    retries = []

    # Check on each result as its thread finishes
    for completed in concurrent.futures.as_completed(futures):
        try:
            result = completed.result()
            # We have to do this here because munch_response doesn't
            # get called on async job results
            exc.raise_from_response(result)
            results.append(result)
        except (keystoneauth1.exceptions.RetriableConnectionFailure,
                exc.OpenStackCloudException) as e:
            if log:
                log.debug(
                    "Exception processing async task: {e}".format(
                        e=str(e)),
                    exc_info=True)
            # If we get an exception, put the result into a list so we
            # can try again
            if raise_on_error:
                raise
            else:
                retries.append(result)
    return results, retries
