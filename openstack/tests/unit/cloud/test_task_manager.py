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

from openstack import task_manager
from openstack.tests.unit import base


class TestException(Exception):
    pass


class TaskTest(task_manager.Task):
    def main(self):
        raise TestException("This is a test exception")


class TaskTestGenerator(task_manager.Task):
    def main(self):
        yield 1


class TaskTestInt(task_manager.Task):
    def main(self):
        return int(1)


class TaskTestFloat(task_manager.Task):
    def main(self):
        return float(2.0)


class TaskTestStr(task_manager.Task):
    def main(self):
        return "test"


class TaskTestBool(task_manager.Task):
    def main(self):
        return True


class TaskTestSet(task_manager.Task):
    def main(self):
        return set([1, 2])


class TaskTestAsync(task_manager.Task):
    def __init__(self):
        super(TaskTestAsync, self).__init__(run_async=True)

    def main(self):
        pass


class TestTaskManager(base.TestCase):

    def setUp(self):
        super(TestTaskManager, self).setUp()
        self.manager = task_manager.TaskManager(name='test')

    def test_wait_re_raise(self):
        """Test that Exceptions thrown in a Task is reraised correctly

        This test is aimed to six.reraise(), called in Task::wait().
        Specifically, we test if we get the same behaviour with all the
        configured interpreters (e.g. py27, p35, ...)
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
