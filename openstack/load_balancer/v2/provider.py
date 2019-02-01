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


class Provider(resource.Resource):
    resources_key = 'providers'
    base_path = '/lbaas/providers'

    # capabilities
    allow_create = False
    allow_fetch = False
    allow_commit = False
    allow_delete = False
    allow_list = True

    _query_mapping = resource.QueryParameters('description', 'name')

    # Properties
    #: The provider name.
    name = resource.Body('name')
    #: The provider description.
    description = resource.Body('description')


class ProviderFlavorCapabilities(resource.Resource):
    resources_key = 'flavor_capabilities'
    base_path = '/lbaas/providers/%(provider)s/flavor_capabilities'

    # capabilities
    allow_create = False
    allow_fetch = False
    allow_commit = False
    allow_delete = False
    allow_list = True

    _query_mapping = resource.QueryParameters('description', 'name')

    # Properties
    #: The provider name to query.
    provider = resource.URI('provider')
    #: The provider name.
    name = resource.Body('name')
    #: The provider description.
    description = resource.Body('description')
