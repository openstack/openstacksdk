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

from openstack import proxy2
from openstack.telemetry.v2 import capability
from openstack.telemetry.v2 import meter as _meter
from openstack.telemetry.v2 import resource as _resource
from openstack.telemetry.v2 import sample
from openstack.telemetry.v2 import statistics


class Proxy(proxy2.BaseProxy):
    """.. caution:: This API is a work in progress and is subject to change."""

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
        return self._list(sample.Sample, paginated=False,
                          counter_name=meter, **query)

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
        return self._list(statistics.Statistics, paginated=False,
                          meter_name=meter, **query)
