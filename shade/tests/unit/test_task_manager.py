# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
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
import mock

from shade import task_manager
from shade.tests.unit import base


class TestException(Exception):
    pass


class TaskTest(task_manager.Task):
    def main(self, client):
        raise TestException("This is a test exception")


class TaskTestGenerator(task_manager.Task):
    def main(self, client):
        yield 1


class TaskTestInt(task_manager.Task):
    def main(self, client):
        return int(1)


class TaskTestFloat(task_manager.Task):
    def main(self, client):
        return float(2.0)


class TaskTestStr(task_manager.Task):
    def main(self, client):
        return "test"


class TaskTestBool(task_manager.Task):
    def main(self, client):
        return True


class TaskTestSet(task_manager.Task):
    def main(self, client):
        return set([1, 2])


class TaskTestAsync(task_manager.Task):
    def __init__(self):
        super(task_manager.Task, self).__init__()
        self.run_async = True

    def main(self, client):
        pass


class TestTaskManager(base.TestCase):

    def setUp(self):
        super(TestTaskManager, self).setUp()
        self.manager = task_manager.TaskManager(name='test', client=self)

    def test_wait_re_raise(self):
        """Test that Exceptions thrown in a Task is reraised correctly

        This test is aimed to six.reraise(), called in Task::wait().
        Specifically, we test if we get the same behaviour with all the
        configured interpreters (e.g. py27, p34, pypy, ...)
        """
        self.assertRaises(TestException, self.manager.submit_task, TaskTest())

    def test_dont_munchify_int(self):
        ret = self.manager.submit_task(TaskTestInt())
        self.assertIsInstance(ret, int)

    def test_dont_munchify_float(self):
        ret = self.manager.submit_task(TaskTestFloat())
        self.assertIsInstance(ret, float)

    def test_dont_munchify_str(self):
        ret = self.manager.submit_task(TaskTestStr())
        self.assertIsInstance(ret, str)

    def test_dont_munchify_bool(self):
        ret = self.manager.submit_task(TaskTestBool())
        self.assertIsInstance(ret, bool)

    def test_dont_munchify_set(self):
        ret = self.manager.submit_task(TaskTestSet())
        self.assertIsInstance(ret, set)

    @mock.patch.object(concurrent.futures.ThreadPoolExecutor, 'submit')
    def test_async(self, mock_submit):
        self.manager.submit_task(TaskTestAsync())
        self.assertTrue(mock_submit.called)
