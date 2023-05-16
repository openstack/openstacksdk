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


class Attribute(resource.Resource):
    resource_key = 'attribute'
    resources_key = 'attributes'
    base_path = '/attributes'
    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = False
    allow_delete = True
    allow_list = True

    #: The timestamp when this attribute was created.
    created_at = resource.Body('created_at')
    #: The deployable_id of the attribute
    deployable_id = resource.Body('deployable_id')
    #: The key of the attribute
    key = resource.Body('key')
    #: The value of the attribute
    value = resource.Body('value')
    #: The timestamp when this attribute was updated.
    updated_at = resource.Body('updated_at')
    #: The uuid of the attribute
    uuid = resource.Body('uuid', alternate_id=True)
