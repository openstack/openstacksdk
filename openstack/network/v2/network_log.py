# Copyright 2026 Openinfra Foundation
#
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

from openstack.network.v2 import _base
from openstack import resource


class Log(_base.NetworkResource):
    resource_key = 'log'
    resources_key = 'logs'
    base_path = '/log/logs'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'id',
        'name',
        'project_id',
        'event',
        'resource_type',
        'resource_id',
        'target_id',
        'enabled',
        'revision_number',
        'sort_dir',
        'sort_key',
    )

    # Properties
    #: Timestamp when the log resource was created.
    created_at = resource.Body('created_at')
    #: The log resource description.
    description = resource.Body('description')
    #: Indicates whether this log object is enabled or disabled.
    #: Default is ``True``. *Type: bool*
    enabled = resource.Body('enabled', type=bool)
    #: Type of security events to log. One of ``ACCEPT``, ``DROP`` or ``ALL``.
    #: Default is ``ALL``.
    event = resource.Body('event')
    #: The log resource name.
    name = resource.Body('name')
    #: The ID of the project this log resource is associated with.
    project_id = resource.Body('project_id', alias='tenant_id')
    #: The ID of the resource to log (e.g. a security group ID).
    resource_id = resource.Body('resource_id')
    #: The resource log type, such as ``security_group``.
    resource_type = resource.Body('resource_type')
    #: The ID of the resource target to log, such as a port ID.
    target_id = resource.Body('target_id')
    #: Timestamp when the log resource was last updated.
    updated_at = resource.Body('updated_at')


class LoggableResource(resource.Resource):
    resource_key = 'loggable_resource'
    resources_key = 'loggable_resources'
    base_path = '/log/loggable-resources'

    # capabilities
    allow_create = False
    allow_fetch = False
    allow_commit = False
    allow_delete = False
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'type',
    )

    # Properties
    #: The resource log type, such as ``security_group``.
    type = resource.Body('type')
