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


class VpnIkePolicy(resource.Resource):
    """VPN IKE policy extension."""

    resource_key = 'ikepolicy'
    resources_key = 'ikepolicies'
    base_path = '/vpn/ikepolicies'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'auth_algorithm',
        'description',
        'encryption_algorithm',
        'ike_version',
        'name',
        'pfs',
        'project_id',
        'phase1_negotiation_mode',
    )

    # Properties
    #: The authentication hash algorithm. Valid values are sha1,
    # sha256, sha384, sha512. The default is sha1.
    auth_algorithm = resource.Body('auth_algorithm')
    #: A human-readable description for the resource.
    # Default is an empty string.
    description = resource.Body('description')
    #: The encryption algorithm. A valid value is 3des, aes-128,
    # aes-192, aes-256, and so on. Default is aes-128.
    encryption_algorithm = resource.Body('encryption_algorithm')
    #: The IKE version. A valid value is v1 or v2. Default is v1.
    ike_version = resource.Body('ike_version')
    #: The lifetime of the security association. The lifetime consists
    # of a unit and integer value. You can omit either the unit or value
    # portion of the lifetime. Default unit is seconds and
    # default value is 3600.
    lifetime = resource.Body('lifetime', type=dict)
    #: Human-readable name of the resource. Default is an empty string.
    name = resource.Body('name')
    #: Perfect forward secrecy (PFS). A valid value is Group2,
    # Group5, Group14, and so on. Default is Group5.
    pfs = resource.Body('pfs')
    #: The ID of the project.
    project_id = resource.Body('project_id')
    #: The IKE mode. A valid value is main, which is the default.
    phase1_negotiation_mode = resource.Body('phase1_negotiation_mode')
    #: The units for the lifetime of the security association.
    # The lifetime consists of a unit and integer value.
    # You can omit either the unit or value portion of the lifetime.
    # Default unit is seconds and default value is 3600.
    units = resource.Body('units')
    #: The lifetime value, as a positive integer. The lifetime
    # consists of a unit and integer value.
    # You can omit either the unit or value portion of the lifetime.
    # Default unit is seconds and default value is 3600.
    value = resource.Body('value', type=int)
