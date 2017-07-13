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


class Metric(resource.Resource):
    """CloudEye metric resource"""
    resource_key = 'metric'
    resources_key = 'metrics'
    base_path = '/metrics'
    next_marker_path = 'meta_data.marker'
    query_marker_key = 'start'
    service = cloud_eye_service.CloudEyeService()

    # capabilities
    allow_list = True

    _query_mapping = QueryParameters('namespace', 'metric_name', 'dim.0',
                                     'dim.1', 'dim.2', 'order', 'limit',
                                     marker=query_marker_key)

    #: Properties
    #: Metric Namespace
    namespace = resource.Body('namespace')
    #: Metric Name
    metric_name = resource.Body('metric_name')
    #: Metric Dimensions
    dimensions = resource.Body('dimensions', type=list)
    #: Metric Unit
    unit = resource.Body('unit')


class FavoriteMetric(Metric):
    """CloudEye Favorite metric resource"""
    base_path = '/favorite-metrics'
