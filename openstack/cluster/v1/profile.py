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
from openstack import format
from openstack import resource


class Profile(resource.Resource):
    resource_key = 'profile'
    resources_key = 'profiles'
    base_path = '/profiles'
    service = cluster_service.ClusterService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    patch_update = True

    # properties
    #: The name of the profile
    name = resource.prop('name')
    #: The type of the profile.
    type_name = resource.prop('type')
    #: The spec of the profile.
    spec = resource.prop('spec', type=dict)
    #: A collection of key-value pairs that are attached to the profile.
    metadata = resource.prop('metadata', type=dict)
    #: Timestamp of when the profile was created.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    created_at = resource.prop('created_at', type=format.ISO8601)
    #: Timestamp of when the profile was last updated.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    updated_at = resource.prop('updated_at', type=format.ISO8601)
