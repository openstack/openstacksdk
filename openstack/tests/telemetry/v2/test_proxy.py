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
from openstack.tests import test_proxy_base


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
        self.verify_delete('openstack.telemetry.v2.alarm.Alarm.delete',
                           self.proxy.delete_alarm)

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
        self.verify_update('openstack.telemetry.v2.alarm.Alarm.update',
                           self.proxy.update_alarm)

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
