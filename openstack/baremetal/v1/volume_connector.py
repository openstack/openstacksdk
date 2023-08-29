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

from openstack.baremetal.v1 import _common
from openstack import resource


class VolumeConnector(resource.Resource):
    resources_key = 'connectors'
    base_path = '/volume/connectors'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    allow_patch = True
    commit_method = 'PATCH'
    commit_jsonpatch = True

    _query_mapping = resource.QueryParameters(
        'node',
        'detail',
        fields={'type': _common.fields_type},
    )

    # Volume Connectors is available since 1.32
    _max_microversion = '1.32'

    #: The identifier of Volume connector and this field depends on the "type"
    # of the volume_connector
    connector_id = resource.Body('connector_id')
    #: Timestamp at which the port was created.
    created_at = resource.Body('created_at')
    #: A set of one or more arbitrary metadata key and value pairs.
    extra = resource.Body('extra')
    #: A list of relative links, including the self and bookmark links.
    links = resource.Body('links', type=list)
    #: The UUID of node this port belongs to
    node_id = resource.Body('node_uuid')
    #: The types of Volume connector
    type = resource.Body('type')
    #: Timestamp at which the port was last updated.
    updated_at = resource.Body('updated_at')
    #: The UUID of the port
    id = resource.Body('uuid', alternate_id=True)
