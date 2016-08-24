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
from openstack.telemetry.alarm.v2 import alarm as _alarm
from openstack.telemetry.alarm.v2 import alarm_change as _alarm_change


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
        # TODO(Qiming): Check the alarm service API docs/code to verify if
        #               the parameters need a change.
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
        # TODO(Qiming): Check the alarm service API docs/code to verify if
        #               the parameters need a change.
        alarm_id = _alarm.Alarm.from_id(alarm).id
        return self._list(_alarm_change.AlarmChange, paginated=False,
                          path_args={'alarm_id': alarm_id}, **query)
