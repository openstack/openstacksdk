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

from openstack.cloud_eye import cloud_eye_service
from openstack.cloud_eye.v1 import alarm as _alarm
from openstack.cloud_eye.v1 import metric as _metric
from openstack.cloud_eye.v1 import metric_data as _metric_data
from openstack.cloud_eye.v1 import quota as _quota
from openstack.exceptions import InvalidRequest
from openstack import proxy2


class Proxy(proxy2.BaseProxy):
    def metrics(self, **query):
        """Retrieve a generator of metrics

        :param dict query: Optional query parameters to be sent to limit the
                      resources being returned.

            * ``namespace``:  metric namespace, ``SYS_ECS``, for example.
            * ``metric_name``: metric name, ``cpu_util``, for example.
            * ``dimensions``: metric dimension list, at most three dimensions,
                              dimension value should be key,value formatted.
                         ['instance_id,6f3c6f91-4b24-4e1b-b7d1-a94ac1cb011d',]
                         for example.
            * ``order``:  pagination order by, ``desc`` or ``asc``
            * ``marker``:  pagination marker
            * ``limit``: pagination limit

        :returns: A generator of metric
                 (:class:`~openstack.cloud_eye.v1.metric.Metric`) instances
        """
        dimensions = query.pop('dimensions', [])
        if not isinstance(dimensions, list):
            raise InvalidRequest('Attribute `dimensions` should be a '
                                 'list')
        if len(dimensions) > 3:
            raise InvalidRequest('Attribute `dimensions` at most could '
                                 'have three dimensions')

        for (idx, dimension) in enumerate(dimensions):
            if "name" not in dimension or "value" not in dimension:
                raise InvalidRequest('Item of attribute `dimensions` must'
                                     'be a dict with `name` and `value` keys')
            value = dimension['name'] + ',' + dimension['value']
            query["dim.%d" % idx] = value

        return self._list(_metric.Metric, paginated=True, **query)

    def favorite_metrics(self):
        """Retrieve a generator of favorite metrics

        :returns: A generator of favorite metric
                 (:class:`~openstack.cloud_eye.v1.metric.Metric`) instances
        """
        return self._list(_metric.FavoriteMetric, paginated=False)

    def get_alarm(self, alarm):
        """Get a single alarm

        :param alarm: The value can be the ID of a alarm
             or a :class:`~openstack.cloud_eye.v1.alarm.Alarm` instance.
        :returns: Alarm instance
        :rtype: :class:`~openstack.cloud_eye.v1.alarm.Alarm`
        """
        # Server will response a list include One Alarm, so we need to get
        # response list and fetch list[0]
        alarm = self._get_resource(_alarm.Alarm, alarm)
        request = alarm._prepare_request()
        endpoint_override = alarm.service.get_endpoint_override()
        response = self._session.get(request.uri,
                                     endpoint_filter=alarm.service,
                                     endpoint_override=endpoint_override)
        body = response.json()
        if alarm.resource_key and alarm.resource_key in body:
            body = body[alarm.resource_key]
        if isinstance(body, list) and body[0]:
            return _alarm.Alarm.new(**body[0])
        return None

    def alarms(self, **query):
        """Retrieve a generator of alarms

        :param dict query: Optional query parameters to be sent to limit the
                      resources being returned.
            * ``order``: order by rule, valid values includes: asc, desc
            * ``marker``:  pagination marker
            * ``limit``: pagination limit

        :returns: A generator of alarm
                 (:class:`~openstack.cloud_eye.v1.alarm.Alarm`) instances
        """
        return self._list(_alarm.Alarm, paginated=True, **query)

    def enable_alarm(self, alarm):
        """enable alarm

        :param alarm: The value can be the ID of a alarm
             or a :class:`~openstack.cloud_eye.v1.alarm.Alarm` instance.
        """
        alarm = self._get_resource(_alarm.Alarm, alarm)
        alarm.enable(self._session)

    def disable_alarm(self, alarm):
        """disable alarm

        :param alarm: The value can be the ID of a alarm
             or a :class:`~openstack.cloud_eye.v1.alarm.Alarm` instance.
        """
        alarm = self._get_resource(_alarm.Alarm, alarm)
        alarm.disable(self._session)

    def delete_alarm(self, alarm, ignore_missing=True):
        """Delete a alarm

        :param alarm: The value can be the ID of a alarm
             or a :class:`~openstack.cloud_eye.v1.alarm.Alarm` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the alarm does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent alarm.

        :returns: Alarm been deleted
        :rtype: :class:`~openstack.dns.v2.alarm.Alarm`
        """
        return self._delete(_alarm.Alarm, alarm, ignore_missing=ignore_missing)

    def metric_aggregations(self, **query):
        """Retrieve a generator of metric aggregations

        :param dict query: Optional query parameters to be sent to limit the
                            resources being returned.

            * ``namespace``:  metric namespace, ``SYS_ECS``, for example.
            * ``metric_name``: metric name, ``cpu_util``, for example.
            * ``from``: metric data collect start time, epoch millis
            * ``to``: metric data collect end time, epoch millis
            * ``period``: data time period, valid values:
                          1 - realtime,
                          300 - every 5 minutes
                          1200 - every 20 minutes
                          3600 - every 1 hour
                          14400 - every 4 hour
                          86400 - every day
            * ``filter``: metric data aggregation method, valid values:
                          ``verage``, ``variance``, ``min``, ``max``
            * ``dimensions``: dimensions for  metric data aggregation, at most
                              three dimensions is allowed. dimensions should be
                             a list contains dict type items, for example:
                             [{"name":"dimension", "value":"dimension-value"}]

        :returns: A generator of MetricAggregation
                 (:class:`~openstack.cloud_eye.v1.metric_data
                 .MetricAggregation`) instances
        """
        if 'dimensions' in query and isinstance(query['dimensions'], list):
            dimensions = query['dimensions']
            for (idx, dimension) in enumerate(dimensions):
                value = dimension['name'] + ',' + dimension['value']
                query["dim.%d" % idx] = value
            return self._list(_metric_data.MetricAggregation,
                              paginated=False,
                              **query)
        else:
            raise InvalidRequest('Attribute `dimensions` should be a list')

    def add_metric_data(self, data):
        """Create Metric Data from a list of attributes

        :param list data: A List of dict, the dict will be used to create
                           a :class:`~openstack.cloud_eye.v1.metric_data
                           .MetricData`, comprised of the properties on the
                           MetricData class.
                    datas sample:
                    [{
                    "metric": {
                        "namespace": "MINE.APP",
                        "dimensions": [
                            {
                                "name": "instance_id",
                                "value": "33328f02-3814-422e-b688-bfdba93d4050"
                            }
                        ],
                        "metric_name": "cpu_util"
                    },
                    "ttl": 172800,
                    "collect_time": 1463598260000,
                    "value": 60,
                    "unit": "%"
                }]

        """
        service = cloud_eye_service.CloudEyeService()
        session = self._session
        return session.post('/metric-data',
                            endpoint_filter=service,
                            endpoint_override=service.get_endpoint_override(),
                            json=data)

    def quotas(self):
        """Retrieve a generator of quotas

        Currently, only ``Alarm`` Quota is available
        :returns: A generator of quota
                 (:class:`~openstack.cloud_eye.v1.quota.Quota`) instances
        """
        return self._list(_quota.Quota, paginated=False)
