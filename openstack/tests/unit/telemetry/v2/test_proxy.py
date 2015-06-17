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
from openstack.telemetry.v2 import alarm
from openstack.telemetry.v2 import alarm_change
from openstack.telemetry.v2 import capability
from openstack.telemetry.v2 import meter
from openstack.telemetry.v2 import resource
from openstack.telemetry.v2 import sample
from openstack.telemetry.v2 import statistics
from openstack.tests.unit import test_proxy_base


class TestTelemetryProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestTelemetryProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_alarm_change_find(self):
        self.verify_find(
            'openstack.telemetry.v2.alarm_change.AlarmChange.find',
            self.proxy.find_alarm_change)

    def test_alarm_changes(self):
        self.verify_list(self.proxy.alarm_changes, alarm_change.AlarmChange,
                         paginated=False)

    def test_alarm_create_attrs(self):
        self.verify_create(self.proxy.create_alarm, alarm.Alarm)

    def test_alarm_delete(self):
        self.verify_delete(self.proxy.delete_alarm, alarm.Alarm, False)

    def test_alarm_delete_ignore(self):
        self.verify_delete(self.proxy.delete_alarm, alarm.Alarm, True)

    def test_alarm_find(self):
        self.verify_find('openstack.telemetry.v2.alarm.Alarm.find',
                         self.proxy.find_alarm)

    def test_alarm_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_alarm,
                         method_args=["resource_or_id"],
                         expected_args=[alarm.Alarm, "resource_or_id"])

    def test_alarms(self):
        self.verify_list(self.proxy.alarms, alarm.Alarm, paginated=False)

    def test_alarm_update(self):
        self.verify_update(self.proxy.update_alarm, alarm.Alarm)

    def test_capability_find(self):
        self.verify_find('openstack.telemetry.v2.capability.Capability.find',
                         self.proxy.find_capability)

    def test_capabilities(self):
        self.verify_list(self.proxy.capabilities, capability.Capability,
                         paginated=False)

    def test_meter_find(self):
        self.verify_find('openstack.telemetry.v2.meter.Meter.find',
                         self.proxy.find_meter)

    def test_meters(self):
        self.verify_list(self.proxy.meters, meter.Meter, paginated=False)

    def test_resource_find(self):
        self.verify_find('openstack.telemetry.v2.resource.Resource.find',
                         self.proxy.find_resource)

    def test_resource_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_resource,
                         method_args=["resource_or_id"],
                         expected_args=[resource.Resource, "resource_or_id"])

    def test_resources(self):
        self.verify_list(self.proxy.resources, resource.Resource,
                         paginated=False)

    def test_sample_create_attrs(self):
        self.verify_create(self.proxy.create_sample, sample.Sample)

    def test_sample_find(self):
        self.verify_find('openstack.telemetry.v2.sample.Sample.find',
                         self.proxy.find_sample)

    def test_samples(self):
        self.verify_list(self.proxy.samples, sample.Sample, paginated=False)

    def test_statistics_find(self):
        self.verify_find('openstack.telemetry.v2.statistics.Statistics.find',
                         self.proxy.find_statistics)

    def test_statistics(self):
        self.verify_list(self.proxy.statistics, statistics.Statistics,
                         paginated=False)
