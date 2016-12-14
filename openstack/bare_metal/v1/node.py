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

from openstack.bare_metal import bare_metal_service
from openstack import resource2 as resource


class Node(resource.Resource):

    resources_key = 'nodes'
    base_path = '/nodes'
    service = bare_metal_service.BareMetalService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True
    patch_update = True

    _query_mapping = resource.QueryParameters(
        'associated', 'driver', 'fields', 'provision_state', 'resource_class',
        instance_id='instance_uuid',
        is_maintenance='maintenance',
    )

    # Properties
    #: The UUID of the chassis associated wit this node. Can be empty or None.
    chassis_id = resource.Body("chassis_uuid")
    #: The current clean step.
    clean_step = resource.Body("clean_step")
    #: Timestamp at which the node was last updated.
    created_at = resource.Body("created_at")
    #: The name of the driver.
    driver = resource.Body("driver")
    #: All the metadata required by the driver to manage this node. List of
    #: fields varies between drivers, and can be retrieved from the
    #: :class:`openstack.bare_metal.v1.driver.Driver` resource.
    driver_info = resource.Body("driver_info", type=dict)
    #: Internal metadata set and stored by node's driver. This is read-only.
    driver_internal_info = resource.Body("driver_internal_info", type=dict)
    #: A set of one or more arbitrary metadata key and value pairs.
    extra = resource.Body("extra")
    #: The UUID of the node resource.
    id = resource.Body("uuid", alternate_id=True)
    #: Information used to customize the deployed image, e.g. size of root
    #: partition, config drive in the form of base64 encoded string and other
    #: metadata.
    instance_info = resource.Body("instance_info")
    #: UUID of the nova instance associated with this node.
    instance_id = resource.Body("instance_uuid")
    #: Whether console access is enabled on this node.
    is_console_enabled = resource.Body("console_enabled", type=bool)
    #: Whether node is currently in "maintenance mode". Nodes put into
    #: maintenance mode are removed from the available resource pool.
    is_maintenance = resource.Body("maintenance", type=bool)
    #: Any error from the most recent transaction that started but failed to
    #: finish.
    last_error = resource.Body("last_error")
    #: A list of relative links, including self and bookmark links.
    links = resource.Body("links", type=list)
    #: user settable description of the reason why the node was placed into
    #: maintenance mode.
    maintenance_reason = resource.Body("maintenance_reason")
    #: Human readable identifier for the node. May be undefined. Certain words
    #: are reserved. Added in API microversion 1.5
    name = resource.Body("name")
    #: Network interface provider to use when plumbing the network connections
    #: for this node. Introduced in API microversion 1.20.
    network_interface = resource.Body("network_interface")
    #: Links to the collection of ports on this node.
    ports = resource.Body("ports", type=list)
    #: Links to the collection of portgroups on this node. Available since
    #: API microversion 1.24.
    port_groups = resource.Body("portgroups", type=list)
    #: The current power state. Usually "power on" or "power off", but may be
    #: "None" if service is unable to determine the power state.
    power_state = resource.Body("power_state")
    #: Physical characteristics of the node. Content populated by the service
    #: during inspection.
    properties = resource.Body("properties", type=dict)
    #: The current provisioning state of the node.
    provision_state = resource.Body("provision_state")
    #: The current RAID configuration of the node.
    raid_config = resource.Body("raid_config")
    #: The name of an service conductor host which is holding a lock on this
    #: node, if a lock is held.
    reservation = resource.Body("reservation")
    #: A string to be used by external schedulers to identify this node as a
    #: unit of a specific type of resource. Added in API microversion 1.21.
    resource_class = resource.Body("resource_class")
    #: Links to the collection of states.
    states = resource.Body("states", type=list)
    #: The requested state if a provisioning action has been requested. For
    #: example, ``AVAILABLE``, ``DEPLOYING``, ``DEPLOYWAIT``, ``DEPLOYING``,
    #: ``ACTIVE`` etc.
    target_provision_state = resource.Body("target_provision_state")
    #: The requested state during a state transition.
    target_power_state = resource.Body("target_power_state")
    #: The requested RAID configration of the node which will be applied when
    #: the node next transitions through the CLEANING state.
    target_raid_config = resource.Body("target_raid_config")
    #: Timestamp at which the node was last updated.
    updated_at = resource.Body("updated_at")


class NodeDetail(Node):

    base_path = '/nodes/detail'

    # capabilities
    allow_create = False
    allow_get = False
    allow_update = False
    allow_delete = False
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'associated', 'driver', 'fields', 'provision_state', 'resource_class',
        instance_id='instance_uuid',
        is_maintenance='maintenance',
    )

    #: The UUID of the node resource.
    id = resource.Body("uuid", alternate_id=True)
