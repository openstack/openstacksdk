# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack.cluster import cluster_service
from openstack import resource2 as resource


class Profile(resource.Resource):
    resource_key = 'profile'
    resources_key = 'profiles'
    base_path = '/profiles'
    service = cluster_service.ClusterService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True

    patch_update = True

    _query_mapping = resource.QueryParameters(
        'sort', 'global_project', 'type', 'name')

    # Bodyerties
    #: The name of the profile
    name = resource.Body('name')
    #: The type of the profile.
    type = resource.Body('type')
    #: The ID of the project this profile belongs to.
    project_id = resource.Body('project')
    #: The ID of the user who created this profile.
    user_id = resource.Body('user')
    #: The spec of the profile.
    spec = resource.Body('spec', type=dict)
    #: A collection of key-value pairs that are attached to the profile.
    metadata = resource.Body('metadata', type=dict)
    #: Timestamp of when the profile was created.
    created_at = resource.Body('created_at')
    #: Timestamp of when the profile was last updated.
    updated_at = resource.Body('updated_at')


class ProfileValidate(Profile):
    base_path = '/profiles/validate'
    allow_create = True
    allow_get = False
    allow_update = False
    allow_delete = False
    allow_list = False

    patch_update = False
