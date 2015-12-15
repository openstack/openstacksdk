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
from openstack.telemetry.v2 import alarm as _alarm
from openstack.telemetry.v2 import alarm_change as _alarm_change
from openstack.telemetry.v2 import capability
from openstack.telemetry.v2 import meter as _meter
from openstack.telemetry.v2 import resource as _resource
from openstack.telemetry.v2 import sample
from openstack.telemetry.v2 import statistics


class Proxy(proxy.BaseProxy):
    """.. caution:: This API is a work in progress and is subject to change."""

    def create_alarm(self, **attrs):
        """Create a new alarm from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.telemetry.v2.alarm.Alarm`,
                           comprised of the properties on the Alarm class.

        :returns: The results of alarm creation
        :rtype: :class:`~openstack.telemetry.v2.alarm.Alarm`
        """
        return self._create(_alarm.Alarm, **attrs)

    def delete_alarm(self, alarm, ignore_missing=True):
        """Delete an alarm

        :param alarm: The value can be either the ID of an alarm or a
                      :class:`~openstack.telemetry.v2.alarm.Alarm` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the alarm does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent alarm.

        :returns: ``None``
        """
        self._delete(_alarm.Alarm, alarm, ignore_missing=ignore_missing)

    def find_alarm(self, name_or_id, ignore_missing=True):
        """Find a single alarm

        :param name_or_id: The name or ID of a alarm.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.telemetry.v2.alarm.Alarm` or None
        """
        return self._find(_alarm.Alarm, name_or_id,
                          ignore_missing=ignore_missing)

    def get_alarm(self, alarm):
        """Get a single alarm

        :param alarm: The value can be the ID of an alarm or a
                      :class:`~openstack.telemetry.v2.alarm.Alarm` instance.

        :returns: One :class:`~openstack.telemetry.v2.alarm.Alarm`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_alarm.Alarm, alarm)

    def alarms(self, **query):
        """Return a generator of alarms

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of alarm objects
        :rtype: :class:`~openstack.telemetry.v2.alarm.Alarm`
        """
        return self._list(_alarm.Alarm, paginated=False, **query)

    def update_alarm(self, alarm, **attrs):
        """Update a alarm

        :param alarm: Either the id of a alarm or a
                      :class:`~openstack.telemetry.v2.alarm.Alarm` instance.
        :attrs kwargs: The attributes to update on the alarm represented
                       by ``value``.

        :returns: The updated alarm
        :rtype: :class:`~openstack.telemetry.v2.alarm.Alarm`
        """
        return self._update(_alarm.Alarm, alarm, **attrs)

    def find_alarm_change(self, name_or_id, ignore_missing=True):
        """Find a single alarm change

        :param name_or_id: The name or ID of a alarm change.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.telemetry.v2.alarm_change.AlarmChange`
                  or None
        """
        return self._find(_alarm_change.AlarmChange, name_or_id,
                          ignore_missing=ignore_missing)

    def alarm_changes(self, alarm, **query):
        """Return a generator of alarm changes

        :param alarm: Alarm resource or id for alarm.
        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of alarm change objects
        :rtype: :class:`~openstack.telemetry.v2.alarm_change.AlarmChange`
        """
        alarm_id = _alarm.Alarm.from_id(alarm).id
        return self._list(_alarm_change.AlarmChange, paginated=False,
                          path_args={'alarm_id': alarm_id}, **query)

    def find_capability(self, name_or_id, ignore_missing=True):
        """Find a single capability

        :param name_or_id: The name or ID of a capability.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.telemetry.v2.capability.Capability`
                  or None
        """
        return self._find(capability.Capability, name_or_id,
                          ignore_missing=ignore_missing)

    def capabilities(self, **query):
        """Return a generator of capabilities

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of capability objects
        :rtype: :class:`~openstack.telemetry.v2.capability.Capability`
        """
        return self._list(capability.Capability, paginated=False, **query)

    def find_meter(self, name_or_id, ignore_missing=True):
        """Find a single meter

        :param name_or_id: The name or ID of a meter.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.telemetry.v2.meter.Meter` or None
        """
        return self._find(_meter.Meter, name_or_id,
                          ignore_missing=ignore_missing)

    def meters(self, **query):
        """Return a generator of meters

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of meter objects
        :rtype: :class:`~openstack.telemetry.v2.meter.Meter`
        """
        return self._list(_meter.Meter, paginated=False, **query)

    def find_resource(self, name_or_id, ignore_missing=True):
        """Find a single resource

        :param name_or_id: The name or ID of a resource.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.telemetry.v2.resource.Resource` or
                  None
        """
        return self._find(_resource.Resource, name_or_id,
                          ignore_missing=ignore_missing)

    def get_resource(self, resource):
        """Get a single resource

        :param resource: The value can be the ID of a resource or a
                         :class:`~openstack.telemetry.v2.resource.Resource`
                         instance.

        :returns: One :class:`~openstack.telemetry.v2.resource.Resource`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_resource.Resource, resource)

    def resources(self, **query):
        """Return a generator of resources

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of resource objects
        :rtype: :class:`~openstack.telemetry.v2.resource.Resource`
        """
        return self._list(_resource.Resource, paginated=False, **query)

    def create_sample(self, **attrs):
        """Create a new sample from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.telemetry.v2.sample.Sample`,
                           comprised of the properties on the Sample class.

        :returns: The results of sample creation
        :rtype: :class:`~openstack.telemetry.v2.sample.Sample`
        """
        return self._create(sample.Sample, **attrs)

    def find_sample(self, name_or_id, ignore_missing=True):
        """Find a single sample

        :param name_or_id: The name or ID of a sample.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.telemetry.v2.sample.Sample` or None
        """
        return self._find(sample.Sample, name_or_id,
                          ignore_missing=ignore_missing)

    def samples(self, meter, **query):
        """Return a generator of samples

        :param value: Meter resource or name for a meter.
        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of sample objects
        :rtype: :class:`~openstack.telemetry.v2.sample.Sample`
        """
        meter_name = _meter.Meter.from_name(meter).name
        return self._list(sample.Sample, paginated=False,
                          path_args={'counter_name': meter_name}, **query)

    def find_statistics(self, name_or_id, ignore_missing=True):
        """Find a single statistics

        :param name_or_id: The name or ID of a statistics.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.telemetry.v2.statistics.Statistics`
                  or None
        """
        return self._find(statistics.Statistics, name_or_id,
                          ignore_missing=ignore_missing)

    def statistics(self, meter, **query):
        """Return a generator of statistics

        :param meter: Meter resource or name for a meter.
        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of statistics objects
        :rtype: :class:`~openstack.telemetry.v2.statistics.Statistics`
        """
        meter_name = _meter.Meter.from_name(meter).name
        return self._list(statistics.Statistics, paginated=False,
                          path_args={'meter_name': meter_name}, **query)
