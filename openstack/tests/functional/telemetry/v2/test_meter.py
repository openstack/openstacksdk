# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import unittest
import uuid

from openstack.tests.functional import base


@unittest.skipUnless(base.service_exists(service_type="metering"),
                     "Metering service does not exist")
class TestMeter(base.BaseFunctionalTest):

    def test_list(self):
        # TODO(thowe): Remove this in favor of create_meter call.
        # Since we do not have a create meter method at the moment
        # make sure there is some data in there
        name = uuid.uuid4().hex
        tainer = self.conn.object_store.create_container(name=name)
        self.conn.object_store.delete_container(tainer)

        names = set([o.name for o in self.conn.telemetry.meters()])
        self.assertIn('storage.objects.incoming.bytes', names)
