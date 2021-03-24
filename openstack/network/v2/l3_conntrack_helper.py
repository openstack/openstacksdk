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


class ConntrackHelper(resource.Resource):
    resource_key = 'conntrack_helper'
    resources_key = 'conntrack_helpers'
    base_path = '/routers/%(router_id)s/conntrack_helpers'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The ID of the Router who owns helper.
    router_id = resource.URI('router_id')
    #: The netfilter conntrack helper module.
    helper = resource.Body('helper')
    #: The network protocol for the netfilter conntrack target rule.
    protocol = resource.Body('protocol')
    #: The network port for the netfilter conntrack target rule.
    port = resource.Body('port')
