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

    def test_alarm(self):
        self.verify_create('openstack.telemetry.v2.alarm.Alarm.create',
                           self.proxy.create_alarm)
        self.verify_delete('openstack.telemetry.v2.alarm.Alarm.delete',
                           self.proxy.delete_alarm)
        self.verify_find('openstack.telemetry.v2.alarm.Alarm.find',
                         self.proxy.find_alarm)
        self.verify_get('openstack.telemetry.v2.alarm.Alarm.get',
                        self.proxy.get_alarm)
        self.verify_list('openstack.telemetry.v2.alarm.Alarm.list',
                         self.proxy.list_alarm)
        self.verify_update('openstack.telemetry.v2.alarm.Alarm.update',
                           self.proxy.update_alarm)

    def test_alarm_change(self):
        self.verify_find(
            'openstack.telemetry.v2.alarm_change.AlarmChange.find',
            self.proxy.find_alarm_change
        )
        self.verify_list(
            'openstack.telemetry.v2.alarm_change.AlarmChange.list',
            self.proxy.list_alarm_change
        )

    def test_capability(self):
        self.verify_find('openstack.telemetry.v2.capability.Capability.find',
                         self.proxy.find_capability)
        self.verify_list('openstack.telemetry.v2.capability.Capability.list',
                         self.proxy.list_capability)

    def test_meter(self):
        self.verify_find('openstack.telemetry.v2.meter.Meter.find',
                         self.proxy.find_meter)
        self.verify_list('openstack.telemetry.v2.meter.Meter.list',
                         self.proxy.list_meter)

    def test_resource(self):
        self.verify_find('openstack.telemetry.v2.resource.Resource.find',
                         self.proxy.find_resource)
        self.verify_get('openstack.telemetry.v2.resource.Resource.get',
                        self.proxy.get_resource)
        self.verify_list('openstack.telemetry.v2.resource.Resource.list',
                         self.proxy.list_resource)

    def test_sample(self):
        self.verify_create('openstack.telemetry.v2.sample.Sample.create',
                           self.proxy.create_sample)
        self.verify_find('openstack.telemetry.v2.sample.Sample.find',
                         self.proxy.find_sample)
        self.verify_list('openstack.telemetry.v2.sample.Sample.list',
                         self.proxy.list_sample)

    def test_statistics(self):
        self.verify_find('openstack.telemetry.v2.statistics.Statistics.find',
                         self.proxy.find_statistics)
        self.verify_list('openstack.telemetry.v2.statistics.Statistics.list',
                         self.proxy.list_statistics)
