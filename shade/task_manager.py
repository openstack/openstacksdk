#!/usr/bin/env python

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
import sys
import threading
import time

import six

from shade import _log


@six.add_metaclass(abc.ABCMeta)
class Task(object):
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
        self._finished = threading.Event()
        self.args = kw

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

    def wait(self):
        self._finished.wait()
        if self._exception:
            six.reraise(type(self._exception), self._exception,
                        self._traceback)
        return self._result

    def run(self, client):
        try:
            self.done(self.main(client))
        except Exception as e:
            self.exception(e, sys.exc_info()[2])


class TaskManager(object):
    log = _log.setup_logging("shade.TaskManager")

    def __init__(self, client, name):
        self.name = name
        self._client = client

    def stop(self):
        """ This is a direct action passthrough TaskManager """
        pass

    def run(self):
        """ This is a direct action passthrough TaskManager """
        pass

    def submitTask(self, task):
        self.log.debug(
            "Manager %s running task %s" % (self.name, type(task).__name__))
        start = time.time()
        task.run(self._client)
        end = time.time()
        self.log.debug(
            "Manager %s ran task %s in %ss" % (self.name, task, (end - start)))
        return task.wait()
