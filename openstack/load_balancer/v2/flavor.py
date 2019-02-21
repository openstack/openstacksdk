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


class Flavor(resource.Resource):
    resource_key = 'flavor'
    resources_key = 'flavors'
    base_path = '/lbaas/flavors'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'id', 'name', 'description', 'flavor_profile_id', is_enabled='enabled'
    )

    # Properties
    #: The ID of the flavor.
    id = resource.Body('id')
    #: The name of the flavor.
    name = resource.Body('name')
    #: The flavor description.
    description = resource.Body('description')
    #: The associated flavor profile ID
    flavor_profile_id = resource.Body('flavor_profile_id')
    #: Whether the flavor is enabled for use or not.
    is_enabled = resource.Body('enabled')
