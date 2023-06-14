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

from openstack import resource


class TapMirror(resource.Resource):
    """Tap Mirror"""

    resource_key = 'tap_mirror'
    resources_key = 'tap_mirrors'
    base_path = '/taas/tap_mirrors'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _allow_unknown_attrs_in_body = True

    _query_mapping = resource.QueryParameters(
        "sort_key", "sort_dir", 'name', 'project_id'
    )

    # Properties
    #: The ID of the Tap Mirror.
    id = resource.Body('id')
    #: The Tap Mirror name.
    name = resource.Body('name')
    #: The Tap Mirror description.
    description = resource.Body('description')
    #: The ID of the project that owns the Tap Mirror.
    project_id = resource.Body('project_id', alias='tenant_id')
    #: Tenant_id (deprecated attribute).
    tenant_id = resource.Body('tenant_id', deprecated=True)
    #: The id of the port the Tap Mirror is associated with
    port_id = resource.Body('port_id')
    #: The status for the tap service.
    directions = resource.Body('directions')
    #: The destination IP address of the Tap Mirror
    remote_ip = resource.Body('remote_ip')
    #: The type of the Tap Mirror, it can be gre or erspanv1
    mirror_type = resource.Body('mirror_type')
