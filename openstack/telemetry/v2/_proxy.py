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

from openstack import proxy
from openstack.telemetry.v2 import alarm
from openstack.telemetry.v2 import alarm_change
from openstack.telemetry.v2 import capability
from openstack.telemetry.v2 import meter
from openstack.telemetry.v2 import resource
from openstack.telemetry.v2 import sample
from openstack.telemetry.v2 import statistics


class Proxy(proxy.BaseProxy):

    def create_alarm(self, **attrs):
        """Create a new alarm from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.telemetry.v2.alarm.Alarm`,
                           comprised of the properties on the Alarm class.

        :returns: The results of alarm creation
        :rtype: :class:`~openstack.telemetry.v2.alarm.Alarm`
        """
        return self._create(alarm.Alarm, **attrs)

    def delete_alarm(self, value, ignore_missing=True):
        """Delete an alarm

        :param value: The value can be either the ID of an alarm or a
                      :class:`~openstack.telemetry.v2.alarm.Alarm` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the alarm does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent alarm.

        :returns: ``None``
        """
        self._delete(alarm.Alarm, value, ignore_missing)

    def find_alarm(self, name_or_id):
        return alarm.Alarm.find(self.session, name_or_id)

    def get_alarm(self, value):
        """Get a single alarm

        :param value: The value can be the ID of an alarm or a
                      :class:`~openstack.telemetry.v2.alarm.Alarm` instance.

        :returns: One :class:`~openstack.telemetry.v2.alarm.Alarm`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(alarm.Alarm, value)

    def list_alarms(self):
        return alarm.Alarm.list(self.session)

    def update_alarm(self, value, **attrs):
        """Update a alarm

        :param value: Either the id of a alarm or a
                      :class:`~openstack.compute.v2.alarm.Alarm` instance.
        :attrs kwargs: The attributes to update on the alarm represented
                       by ``value``.

        :returns: The updated alarm
        :rtype: :class:`~openstack.compute.v2.alarm.Alarm`
        """
        return self._update(alarm.Alarm, value, **attrs)

    def find_alarm_change(self, name_or_id):
        return alarm_change.AlarmChange.find(self.session, name_or_id)

    def list_alarm_changes(self):
        return alarm_change.AlarmChange.list(self.session)

    def find_capability(self, name_or_id):
        return capability.Capability.find(self.session, name_or_id)

    def list_capabilitys(self):
        return capability.Capability.list(self.session)

    def find_meter(self, name_or_id):
        return meter.Meter.find(self.session, name_or_id)

    def list_meters(self):
        return meter.Meter.list(self.session)

    def find_resource(self, name_or_id):
        return resource.Resource.find(self.session, name_or_id)

    def get_resource(self, value):
        """Get a single resource

        :param value: The value can be the ID of a resource or a
                      :class:`~openstack.telemetry.v2.resource.Resource`
                      instance.

        :returns: One :class:`~openstack.telemetry.v2.resource.Resource`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(resource.Resource, value)

    def list_resources(self):
        return resource.Resource.list(self.session)

    def create_sample(self, **attrs):
        """Create a new sample from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.telemetry.v2.sample.Sample`,
                           comprised of the properties on the Sample class.

        :returns: The results of sample creation
        :rtype: :class:`~openstack.telemetry.v2.sample.Sample`
        """
        return self._create(sample.Sample, **attrs)

    def find_sample(self, name_or_id):
        return sample.Sample.find(self.session, name_or_id)

    def list_samples(self):
        return sample.Sample.list(self.session)

    def find_statistics(self, name_or_id):
        return statistics.Statistics.find(self.session, name_or_id)

    def list_statistics(self):
        return statistics.Statistics.list(self.session)
