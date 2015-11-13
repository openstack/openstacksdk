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


import mock
import types

import shade
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

    @mock.patch.object(shade.meta, 'obj_to_dict')
    @mock.patch.object(shade.meta, 'obj_list_to_dict')
    def test_dont_munchify_generators(self, mock_ol2d, mock_o2d):
        ret = self.manager.submitTask(TestTaskGenerator())
        self.assertEqual(types.GeneratorType, type(ret))
        self.assertFalse(mock_o2d.called)
        self.assertFalse(mock_ol2d.called)
