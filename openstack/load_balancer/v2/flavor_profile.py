# Copyright 2019 Rackspace, US Inc.
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

from openstack import resource


class FlavorProfile(resource.Resource):
    resource_key = 'flavorprofile'
    resources_key = 'flavorprofiles'
    base_path = '/lbaas/flavorprofiles'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'id', 'name', 'provider_name', 'flavor_data'
    )

    # Properties
    #: The ID of the flavor profile.
    id = resource.Body('id')
    #: The name of the flavor profile.
    name = resource.Body('name')
    #: The provider this flavor profile is for.
    provider_name = resource.Body('provider_name')
    #: The JSON string containing the flavor metadata.
    flavor_data = resource.Body('flavor_data')
