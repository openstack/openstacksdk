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

from openstack.telemetry.v2 import sample
from openstack.tests.functional import base


@unittest.skipUnless(base.service_exists(service_type="metering"),
                     "Metering service does not exist")
class TestSample(base.BaseFunctionalTest):

    meter = None
    sample = None

    @classmethod
    def setUpClass(cls):
        super(TestSample, cls).setUpClass()
        cls.meter = next(cls.conn.telemetry.meters())
        resource = next(cls.conn.telemetry.resources())
        sot = cls.conn.telemetry.create_sample(
            counter_name=cls.meter.name,
            meter=cls.meter.name,
            counter_type='gauge',
            counter_unit='instance',
            counter_volume=1.0,
            resource_id=resource.id,
        )
        assert isinstance(sot, sample.Sample)
        cls.sample = sot

    def test_list(self):
        ids = [o.id for o in self.conn.telemetry.samples(self.meter)]
        self.assertIn(self.sample.id, ids)
