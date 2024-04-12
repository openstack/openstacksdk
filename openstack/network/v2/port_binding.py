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

from openstack import exceptions
from openstack import resource
from openstack import utils


class PortBinding(resource.Resource):
    name_attribute = "bindings"
    resource_name = "binding"
    resource_key = 'binding'
    resources_key = 'bindings'
    base_path = '/ports/%(port_id)s/bindings'

    _allow_unknown_attrs_in_body = True

    # capabilities
    allow_create = True
    allow_fetch = False
    allow_commit = True
    allow_delete = True
    allow_list = True

    requires_id = False

    # Properties
    #: The port ID of the binding
    port_id = resource.URI('port_id')
    #: The hostname of the system the agent is running on.
    host = resource.Body('host')
    #: A dictionary that enables the application running on
    #  the specific host to pass and receive vif port information
    #  specific to the networking back-end.
    profile = resource.Body('profile', type=dict)
    #: A dictionary which contains additional information on the
    #  port. The following fields are defined: port_filter and
    #  ovs_hybrid_plug, both are booleans.
    vif_details = resource.Body('vif_details', type=dict)
    #: The type of which mechanism is used for the port.
    #  Currently the following values are supported: ovs, bridge,
    #  macvtap, hw_veb, hostdev_physical, vhostuser, distributed and
    #  other.
    vif_type = resource.Body('vif_type')
    #: The type of vNIC which this port should be attached to.
    #  The valid values are normal, macvtap, direct, baremetal,
    #  direct-physical, virtio-forwarder, smart-nic and remote-managed.
    vnic_type = resource.Body('vnic_type')

    def activate_port_binding(self, session, **attrs):
        host = attrs['host']
        url = utils.urljoin(
            '/ports', self.port_id, 'bindings', host, 'activate'
        )
        resp = session.put(url, json={'binding': attrs})
        exceptions.raise_from_response(resp)
        self._body.attributes.update(resp.json())
        return self

    def delete_port_binding(self, session, host):
        url = utils.urljoin('/ports', self.port_id, 'bindings', host)
        resp = session.delete(url)
        exceptions.raise_from_response(resp)
