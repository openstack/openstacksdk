#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#
from openstack.cloud_eye import cloud_eye_service
from openstack import resource2 as resource
from openstack.resource2 import QueryParameters


class MetricData(resource.Resource):
    """CloudEye metric data resource"""
    base_path = '/metric-data'
    service = cloud_eye_service.CloudEyeService()

    # capabilities
    allow_create = True

    #: Properties
    #: Metric Namespace
    namespace = resource.Body('namespace')
    #: Metric Name
    metric_name = resource.Body('metric_name')
    #: Dimensions
    dimensions = resource.Body('dimensions', type=list)
    #: ttl, metric data TTL, max value is: 604800
    ttl = resource.Body('ttl', type=int)
    #: collect time
    collect_time = resource.Body('collect_time', type=long)
    #: value
    value = resource.Body('value')
    #: value type, valid values includes: ``int``, ``float``
    value_type = resource.Body('type')
    #: unit
    unit = resource.Body('unit')


class MetricAggregation(resource.Resource):
    """CloudEye metric data aggregation resource"""
    resource_key = 'datapoints'
    resources_key = 'datapoints'
    base_path = '/metric-data'
    service = cloud_eye_service.CloudEyeService()

    # capabilities
    allow_list = True

    #: Mapping of accepted query parameter names.
    _query_mapping = QueryParameters('namespace', 'metric_name', 'from', 'to',
                                     'period', 'filter', 'dim.0', 'dim.1',
                                     'dim.2')

    #: Properties
    #: Metric Data average
    average = resource.Body('average')
    #: Metric Data variance
    variance = resource.Body('variance')
    #: Metric Data min
    min = resource.Body('min')
    #: Metric Data max
    max = resource.Body('max')
    #: Metric Data collect timestamp
    timestamp = resource.Body('timestamp')
    #: Metric Data Unit
    unit = resource.Body('unit')
