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


class FederationProtocol(resource.Resource):
    resource_key = 'protocol'
    resources_key = 'protocols'
    base_path = '/OS-FEDERATION/identity_providers/%(idp_id)s/protocols'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    create_exclude_id_from_body = True
    create_method = 'PUT'
    commit_method = 'PATCH'

    _query_mapping = resource.QueryParameters(
        'id',
    )

    # Properties
    #: name of the protocol (read only) *Type: string*
    name = resource.Body('id')
    #: The ID of the identity provider the protocol is attached to.
    #  *Type: string*
    idp_id = resource.URI('idp_id')
    #: The definition of the protocol
    #  *Type: dict*
    mapping_id = resource.Body('mapping_id')
