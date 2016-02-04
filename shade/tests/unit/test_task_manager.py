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


from shade import task_manager
from shade.tests.unit import base


class TestException(Exception):
    pass


class TestTask(task_manager.Task):
    def main(self, client):
        raise TestException("This is a test exception")


class TestTaskGenerator(task_manager.Task):
    def main(self, client):
        yield 1


class TestTaskInt(task_manager.Task):
    def main(self, client):
        return int(1)


class TestTaskFloat(task_manager.Task):
    def main(self, client):
        return float(2.0)


class TestTaskStr(task_manager.Task):
    def main(self, client):
        return "test"


class TestTaskBool(task_manager.Task):
    def main(self, client):
        return True


class TestTaskSet(task_manager.Task):
    def main(self, client):
        return set([1, 2])


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
        self.assertRaises(TestException, self.manager.submitTask, TestTask())

    def test_dont_munchify_int(self):
        ret = self.manager.submitTask(TestTaskInt())
        self.assertIsInstance(ret, int)

    def test_dont_munchify_float(self):
        ret = self.manager.submitTask(TestTaskFloat())
        self.assertIsInstance(ret, float)

    def test_dont_munchify_str(self):
        ret = self.manager.submitTask(TestTaskStr())
        self.assertIsInstance(ret, str)

    def test_dont_munchify_bool(self):
        ret = self.manager.submitTask(TestTaskBool())
        self.assertIsInstance(ret, bool)

    def test_dont_munchify_set(self):
        ret = self.manager.submitTask(TestTaskSet())
        self.assertIsInstance(ret, set)
