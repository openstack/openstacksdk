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
from openstack.tests.unit import test_proxy_base


class TestTelemetryProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestTelemetryProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_alarm_change_find(self):
        self.verify_find(
            'openstack.telemetry.v2.alarm_change.AlarmChange.find',
            self.proxy.find_alarm_change)

    def test_alarm_change_list(self):
        self.verify_list(
            'openstack.telemetry.v2.alarm_change.AlarmChange.list',
            self.proxy.list_alarm_changes)

    def test_alarm_create(self):
        self.verify_create('openstack.telemetry.v2.alarm.Alarm.create',
                           self.proxy.create_alarm)

    def test_alarm_delete(self):
        self.verify_delete2(alarm.Alarm, self.proxy.delete_alarm, False)

    def test_alarm_delete_ignore(self):
        self.verify_delete2(alarm.Alarm, self.proxy.delete_alarm, True)

    def test_alarm_find(self):
        self.verify_find('openstack.telemetry.v2.alarm.Alarm.find',
                         self.proxy.find_alarm)

    def test_alarm_get(self):
        self.verify_get('openstack.telemetry.v2.alarm.Alarm.get',
                        self.proxy.get_alarm)

    def test_alarm_list(self):
        self.verify_list('openstack.telemetry.v2.alarm.Alarm.list',
                         self.proxy.list_alarms)

    def test_alarm_update(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_update2('openstack.proxy.BaseProxy._update',
                            self.proxy.update_alarm,
                            method_args=["resource_or_id"],
                            method_kwargs=kwargs,
                            expected_args=[alarm.Alarm, "resource_or_id"],
                            expected_kwargs=kwargs)

    def test_capability_find(self):
        self.verify_find('openstack.telemetry.v2.capability.Capability.find',
                         self.proxy.find_capability)

    def test_capability_list(self):
        self.verify_list('openstack.telemetry.v2.capability.Capability.list',
                         self.proxy.list_capabilitys)

    def test_meter_find(self):
        self.verify_find('openstack.telemetry.v2.meter.Meter.find',
                         self.proxy.find_meter)

    def test_meter_list(self):
        self.verify_list('openstack.telemetry.v2.meter.Meter.list',
                         self.proxy.list_meters)

    def test_resource_find(self):
        self.verify_find('openstack.telemetry.v2.resource.Resource.find',
                         self.proxy.find_resource)

    def test_resource_get(self):
        self.verify_get('openstack.telemetry.v2.resource.Resource.get',
                        self.proxy.get_resource)

    def test_resource_list(self):
        self.verify_list('openstack.telemetry.v2.resource.Resource.list',
                         self.proxy.list_resources)

    def test_sample_create(self):
        self.verify_create('openstack.telemetry.v2.sample.Sample.create',
                           self.proxy.create_sample)

    def test_sample_find(self):
        self.verify_find('openstack.telemetry.v2.sample.Sample.find',
                         self.proxy.find_sample)

    def test_sample_list(self):
        self.verify_list('openstack.telemetry.v2.sample.Sample.list',
                         self.proxy.list_samples)

    def test_statistics_find(self):
        self.verify_find('openstack.telemetry.v2.statistics.Statistics.find',
                         self.proxy.find_statistics)

    def test_statistics_list(self):
        self.verify_list('openstack.telemetry.v2.statistics.Statistics.list',
                         self.proxy.list_statistics)
