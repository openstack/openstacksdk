# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack.tests.functional.image.v2 import base


class TestTask(base.BaseImageTest):
    def test_tasks(self):
        tasks = list(self.operator_cloud.image.tasks())
        # NOTE(stephenfin): Yes, this is a dumb test. Basically all that we're
        # checking is that the API endpoint is correct. It would be nice to
        # have a proper check here that includes creation of tasks but we don't
        # currently have the ability to do this and I'm not even sure if tasks
        # are still really a supported thing. A potential future work item,
        # perhaps.
        self.assertIsInstance(tasks, list)
