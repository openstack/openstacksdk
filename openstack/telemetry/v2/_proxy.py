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
        self._delete(alarm.Alarm, value, ignore_missing=ignore_missing)

    def find_alarm(self, name_or_id):
        """Find a single alarm

        :param name_or_id: The name or ID of a alarm.
        :returns: One :class:`~openstack.telemetry.v2.alarm.Alarm` or None
        """
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

    def alarms(self):
        """Return a generator of alarms

        :returns: A generator of alarm objects
        :rtype: :class:`~openstack.telemetry.v2.alarm.Alarm`
        """
        return self._list(alarm.Alarm)

    def update_alarm(self, value, **attrs):
        """Update a alarm

        :param value: Either the id of a alarm or a
                      :class:`~openstack.telemetry.v2.alarm.Alarm` instance.
        :attrs kwargs: The attributes to update on the alarm represented
                       by ``value``.

        :returns: The updated alarm
        :rtype: :class:`~openstack.telemetry.v2.alarm.Alarm`
        """
        return self._update(alarm.Alarm, value, **attrs)

    def find_alarm_change(self, name_or_id):
        """Find a single alarm change

        :param name_or_id: The name or ID of a alarm change.
        :returns: One :class:`~openstack.telemetry.v2.alarm_change.AlarmChange`
                  or None
        """
        return alarm_change.AlarmChange.find(self.session, name_or_id)

    def alarm_changes(self):
        """Return a generator of alarm changes

        :returns: A generator of alarm change objects
        :rtype: :class:`~openstack.telemetry.v2.alarm_change.AlarmChange`
        """
        return self._list(alarm_change.AlarmChange)

    def find_capability(self, name_or_id):
        """Find a single capability

        :param name_or_id: The name or ID of a capability.
        :returns: One :class:`~openstack.telemetry.v2.capability.Capability`
                  or None
        """
        return capability.Capability.find(self.session, name_or_id)

    def capabilities(self):
        """Return a generator of capabilities

        :returns: A generator of capability objects
        :rtype: :class:`~openstack.telemetry.v2.capability.Capability`
        """
        return self._list(capability.Capability)

    def find_meter(self, name_or_id):
        """Find a single meter

        :param name_or_id: The name or ID of a meter.
        :returns: One :class:`~openstack.telemetry.v2.meter.Meter` or None
        """
        return meter.Meter.find(self.session, name_or_id)

    def meters(self):
        """Return a generator of meters

        :returns: A generator of meter objects
        :rtype: :class:`~openstack.telemetry.v2.meter.Meter`
        """
        return self._list(meter.Meter)

    def find_resource(self, name_or_id):
        """Find a single resource

        :param name_or_id: The name or ID of a resource.
        :returns: One :class:`~openstack.telemetry.v2.resource.Resource` or
                  None
        """
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

    def resources(self):
        """Return a generator of resources

        :returns: A generator of resource objects
        :rtype: :class:`~openstack.telemetry.v2.resource.Resource`
        """
        return self._list(resource.Resource)

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
        """Find a single sample

        :param name_or_id: The name or ID of a sample.
        :returns: One :class:`~openstack.telemetry.v2.sample.Sample` or None
        """
        return sample.Sample.find(self.session, name_or_id)

    def samples(self):
        """Return a generator of samples

        :returns: A generator of sample objects
        :rtype: :class:`~openstack.telemetry.v2.sample.Sample`
        """
        return self._list(sample.Sample)

    def find_statistics(self, name_or_id):
        """Find a single statistics

        :param name_or_id: The name or ID of a statistics.
        :returns: One :class:`~openstack.telemetry.v2.statistics.Statistics`
                  or None
        """
        return statistics.Statistics.find(self.session, name_or_id)

    def statistics(self):
        """Return a generator of statistics

        :returns: A generator of statistics objects
        :rtype: :class:`~openstack.telemetry.v2.statistics.Statistics`
        """
        return self._list(statistics.Statistics)
