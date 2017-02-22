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

from openstack.telemetry.v2 import _proxy
from openstack.telemetry.v2 import capability
from openstack.telemetry.v2 import meter
from openstack.telemetry.v2 import resource
from openstack.telemetry.v2 import sample
from openstack.telemetry.v2 import statistics
from openstack.tests.unit import test_proxy_base2


class TestTelemetryProxy(test_proxy_base2.TestProxyBase):
    def setUp(self):
        super(TestTelemetryProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_capability_find(self):
        self.verify_find(self.proxy.find_capability, capability.Capability)

    def test_capabilities(self):
        self.verify_list(self.proxy.capabilities, capability.Capability,
                         paginated=False)

    def test_meter_find(self):
        self.verify_find(self.proxy.find_meter, meter.Meter)

    def test_meters(self):
        self.verify_list(self.proxy.meters, meter.Meter, paginated=False)

    def test_resource_find(self):
        self.verify_find(self.proxy.find_resource, resource.Resource)

    def test_resource_get(self):
        self.verify_get(self.proxy.get_resource, resource.Resource)

    def test_resources(self):
        self.verify_list(self.proxy.resources, resource.Resource,
                         paginated=False)

    def test_sample_find(self):
        self.verify_find(self.proxy.find_sample, sample.Sample)

    def test_samples(self):
        expected_kwargs = {'counter_name': 'meterone'}
        self.verify_list(self.proxy.samples, sample.Sample,
                         method_args=['meterone'],
                         paginated=False, expected_kwargs=expected_kwargs)

    def test_statistics_find(self):
        self.verify_find(self.proxy.find_statistics, statistics.Statistics)

    def test_statistics(self):
        expected_kwargs = {'meter_name': 'meterone'}
        self.verify_list(self.proxy.statistics, statistics.Statistics,
                         method_args=['meterone'],
                         paginated=False, expected_kwargs=expected_kwargs)
