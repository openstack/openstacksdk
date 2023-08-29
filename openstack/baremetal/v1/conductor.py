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


class Conductor(resource.Resource):
    resources_key = 'conductors'
    base_path = '/conductors'

    # capabilities
    allow_create = False
    allow_fetch = True
    allow_commit = False
    allow_delete = False
    allow_list = True
    allow_patch = False

    _query_mapping = resource.QueryParameters(
        'detail',
        fields={'type': _common.fields_type},
    )

    _max_microversion = '1.49'
    created_at = resource.Body('created_at')
    updated_at = resource.Body('updated_at')
    hostname = resource.Body('hostname')
    conductor_group = resource.Body('conductor_group')
    alive = resource.Body('alive', type=bool)
    links = resource.Body('links', type=list)
    drivers = resource.Body('drivers', type=list)
