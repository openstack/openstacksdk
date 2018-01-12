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

from openstack.clustering import clustering_service
from openstack import resource


class ProfileType(resource.Resource):
    resource_key = 'profile_type'
    resources_key = 'profile_types'
    base_path = '/profile-types'
    service = clustering_service.ClusteringService()

    # Capabilities
    allow_list = True
    allow_get = True

    # Properties
    #: Name of the profile type.
    name = resource.Body('name', alternate_id=True)
    #: The schema of the profile type.
    schema = resource.Body('schema')
    #: The support status of the profile type
    support_status = resource.Body('support_status')
