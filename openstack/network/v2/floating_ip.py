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

from openstack.network import network_service
from openstack import resource


class FloatingIP(resource.Resource):
    id_attribute = "floating_ip_address"
    name_attribute = None
    resource_name = "floating ip"
    resource_key = 'floatingip'
    resources_key = 'floatingips'
    base_path = '/floatingips'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True
    put_update = True

    # Properties
    fixed_ip_address = resource.prop('fixed_ip_address')
    floating_ip_address = resource.prop('floating_ip_address')
    floating_network_id = resource.prop('floating_network_id')
    port_id = resource.prop('port_id')
    project_id = resource.prop('tenant_id')
    router_id = resource.prop('router_id')

    @classmethod
    def find_available(cls, session):
        args = {
            'port_id': '',
            'fields': cls.id_attribute,
        }
        info = cls.list(session, **args)
        try:
            return next(info)
        except StopIteration:
            return None
