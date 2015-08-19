# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.

from shade import task_manager


class UserList(task_manager.Task):
    def main(self, client):
        return client.keystone_client.users.list()


class UserCreate(task_manager.Task):
    def main(self, client):
        return client.keystone_client.users.create(**self.args)


class UserDelete(task_manager.Task):
    def main(self, client):
        return client.keystone_client.users.delete(**self.args)


class UserUpdate(task_manager.Task):
    def main(self, client):
        return client.keystone_client.users.update(**self.args)


class FlavorList(task_manager.Task):
    def main(self, client):
        return client.nova_client.flavors.list(**self.args)


class FlavorCreate(task_manager.Task):
    def main(self, client):
        return client.nova_client.flavors.create(**self.args)


class FlavorDelete(task_manager.Task):
    def main(self, client):
        return client.nova_client.flavors.delete(**self.args)


class FlavorGet(task_manager.Task):
    def main(self, client):
        return client.nova_client.flavors.get(**self.args)


class FlavorAddAccess(task_manager.Task):
    def main(self, client):
        return client.nova_client.flavor_access.add_tenant_access(
            **self.args
        )


class FlavorRemoveAccess(task_manager.Task):
    def main(self, client):
        return client.nova_client.flavor_access.remove_tenant_access(
            **self.args
        )


class ServerList(task_manager.Task):
    def main(self, client):
        return client.nova_client.servers.list(**self.args)


class ServerGet(task_manager.Task):
    def main(self, client):
        return client.nova_client.servers.get(**self.args)


class ServerCreate(task_manager.Task):
    def main(self, client):
        return client.nova_client.servers.create(**self.args)


class ServerDelete(task_manager.Task):
    def main(self, client):
        return client.nova_client.servers.delete(**self.args)


class ServerRebuild(task_manager.Task):
    def main(self, client):
        return client.nova_client.servers.rebuild(**self.args)


class KeypairList(task_manager.Task):
    def main(self, client):
        return client.nova_client.keypairs.list()


class KeypairCreate(task_manager.Task):
    def main(self, client):
        return client.nova_client.keypairs.create(**self.args)


class KeypairDelete(task_manager.Task):
    def main(self, client):
        return client.nova_client.keypairs.delete(**self.args)


class NovaUrlGet(task_manager.Task):
    def main(self, client):
        return client.nova_client.client.get(**self.args)


class NetworkList(task_manager.Task):
    def main(self, client):
        return client.neutron_client.list_networks()


class NetworkCreate(task_manager.Task):
    def main(self, client):
        return client.neutron_client.create_network(**self.args)


class NetworkDelete(task_manager.Task):
    def main(self, client):
        return client.neutron_client.delete_network(**self.args)


class RouterList(task_manager.Task):
    def main(self, client):
        return client.neutron_client.list_routers()


class RouterCreate(task_manager.Task):
    def main(self, client):
        return client.neutron_client.create_router(**self.args)


class RouterUpdate(task_manager.Task):
    def main(self, client):
        return client.neutron_client.update_router(**self.args)


class RouterDelete(task_manager.Task):
    def main(self, client):
        client.neutron_client.delete_router(**self.args)


class GlanceImageList(task_manager.Task):
    def main(self, client):
        return [image for image in self.args['image_gen']]


class NovaImageList(task_manager.Task):
    def main(self, client):
        return client.nova_client.images.list()


class ImageSnapshotCreate(task_manager.Task):
    def main(self, client):
        return client.nova_client.servers.create_image(**self.args)


class ImageCreate(task_manager.Task):
    def main(self, client):
        return client.glance_client.images.create(**self.args)


class ImageDelete(task_manager.Task):
    def main(self, client):
        return client.glance_client.images.delete(**self.args)


class ImageTaskCreate(task_manager.Task):
    def main(self, client):
        return client.glance_client.tasks.create(**self.args)


class ImageTaskGet(task_manager.Task):
    def main(self, client):
        return client.glance_client.tasks.get(**self.args)


class ImageUpdate(task_manager.Task):
    def main(self, client):
        client.glance_client.images.update(**self.args)


class ImageUpload(task_manager.Task):
    def main(self, client):
        client.glance_client.images.upload(**self.args)


class VolumeCreate(task_manager.Task):
    def main(self, client):
        return client.cinder_client.volumes.create(**self.args)


class VolumeDelete(task_manager.Task):
    def main(self, client):
        client.cinder_client.volumes.delete(**self.args)


class VolumeList(task_manager.Task):
    def main(self, client):
        return client.cinder_client.volumes.list()


class VolumeDetach(task_manager.Task):
    def main(self, client):
        client.nova_client.volumes.delete_server_volume(**self.args)


class VolumeAttach(task_manager.Task):
    def main(self, client):
        client.nova_client.volumes.create_server_volume(**self.args)


class NeutronSecurityGroupList(task_manager.Task):
    def main(self, client):
        return client.neutron_client.list_security_groups()


class NeutronSecurityGroupCreate(task_manager.Task):
    def main(self, client):
        return client.neutron_client.create_security_group(**self.args)


class NeutronSecurityGroupDelete(task_manager.Task):
    def main(self, client):
        return client.neutron_client.delete_security_group(**self.args)


class NeutronSecurityGroupUpdate(task_manager.Task):
    def main(self, client):
        return client.neutron_client.update_security_group(**self.args)


class NeutronSecurityGroupRuleCreate(task_manager.Task):
    def main(self, client):
        return client.neutron_client.create_security_group_rule(**self.args)


class NeutronSecurityGroupRuleDelete(task_manager.Task):
    def main(self, client):
        return client.neutron_client.delete_security_group_rule(**self.args)


class NovaSecurityGroupList(task_manager.Task):
    def main(self, client):
        return client.nova_client.security_groups.list()


class NovaSecurityGroupCreate(task_manager.Task):
    def main(self, client):
        return client.nova_client.security_groups.create(**self.args)


class NovaSecurityGroupDelete(task_manager.Task):
    def main(self, client):
        return client.nova_client.security_groups.delete(**self.args)


class NovaSecurityGroupUpdate(task_manager.Task):
    def main(self, client):
        return client.nova_client.security_groups.update(**self.args)


class NovaSecurityGroupRuleCreate(task_manager.Task):
    def main(self, client):
        return client.nova_client.security_group_rules.create(**self.args)


class NovaSecurityGroupRuleDelete(task_manager.Task):
    def main(self, client):
        return client.nova_client.security_group_rules.delete(**self.args)


class NeutronFloatingIPList(task_manager.Task):
    def main(self, client):
        return client.neutron_client.list_floatingips(**self.args)


class NovaFloatingIPList(task_manager.Task):
    def main(self, client):
        return client.nova_client.floating_ips.list()


class NeutronFloatingIPCreate(task_manager.Task):
    def main(self, client):
        return client.neutron_client.create_floatingip(**self.args)


class NovaFloatingIPCreate(task_manager.Task):
    def main(self, client):
        return client.nova_client.floating_ips.create(**self.args)


class NeutronFloatingIPDelete(task_manager.Task):
    def main(self, client):
        return client.neutron_client.delete_floatingip(**self.args)


class NovaFloatingIPDelete(task_manager.Task):
    def main(self, client):
        return client.nova_client.floating_ips.delete(**self.args)


class NovaFloatingIPAttach(task_manager.Task):
    def main(self, client):
        return client.nova_client.servers.add_floating_ip(**self.args)


class NovaFloatingIPDetach(task_manager.Task):
    def main(self, client):
        return client.nova_client.servers.remove_floating_ip(**self.args)


class NeutronFloatingIPUpdate(task_manager.Task):
    def main(self, client):
        return client.neutron_client.update_floatingip(**self.args)


class FloatingIPPoolList(task_manager.Task):
    def main(self, client):
        return client.nova_client.floating_ip_pools.list()


class ContainerGet(task_manager.Task):
    def main(self, client):
        return client.swift_client.head_container(**self.args)


class ContainerCreate(task_manager.Task):
    def main(self, client):
        client.swift_client.put_container(**self.args)


class ContainerDelete(task_manager.Task):
    def main(self, client):
        client.swift_client.delete_container(**self.args)


class ContainerUpdate(task_manager.Task):
    def main(self, client):
        client.swift_client.post_container(**self.args)


class ObjectCapabilities(task_manager.Task):
    def main(self, client):
        return client.swift_client.get_capabilities(**self.args)


class ObjectDelete(task_manager.Task):
    def main(self, client):
        return client.swift_client.delete_object(**self.args)


class ObjectCreate(task_manager.Task):
    def main(self, client):
        return client.swift_service.upload(**self.args)


class ObjectUpdate(task_manager.Task):
    def main(self, client):
        client.swift_client.post_object(**self.args)


class ObjectMetadata(task_manager.Task):
    def main(self, client):
        return client.swift_client.head_object(**self.args)


class SubnetCreate(task_manager.Task):
    def main(self, client):
        return client.neutron_client.create_subnet(**self.args)


class SubnetList(task_manager.Task):
    def main(self, client):
        return client.neutron_client.list_subnets()


class SubnetDelete(task_manager.Task):
    def main(self, client):
        client.neutron_client.delete_subnet(**self.args)


class SubnetUpdate(task_manager.Task):
    def main(self, client):
        return client.neutron_client.update_subnet(**self.args)


class PortList(task_manager.Task):
    def main(self, client):
        return client.neutron_client.list_ports(**self.args)


class PortCreate(task_manager.Task):
    def main(self, client):
        return client.neutron_client.create_port(**self.args)


class PortUpdate(task_manager.Task):
    def main(self, client):
        return client.neutron_client.update_port(**self.args)


class PortDelete(task_manager.Task):
    def main(self, client):
        return client.neutron_client.delete_port(**self.args)


class MachineCreate(task_manager.Task):
    def main(self, client):
        return client.ironic_client.node.create(**self.args)


class MachineDelete(task_manager.Task):
    def main(self, client):
        return client.ironic_client.node.delete(**self.args)


class MachinePatch(task_manager.Task):
    def main(self, client):
        return client.ironic_client.node.update(**self.args)


class MachinePortGet(task_manager.Task):
    def main(self, client):
        return client.ironic_client.port.get(**self.args)


class MachinePortGetByAddress(task_manager.Task):
    def main(self, client):
        return client.ironic_client.port.get_by_address(**self.args)


class MachinePortCreate(task_manager.Task):
    def main(self, client):
        return client.ironic_client.port.create(**self.args)


class MachinePortDelete(task_manager.Task):
    def main(self, client):
        return client.ironic_client.port.delete(**self.args)


class MachinePortList(task_manager.Task):
    def main(self, client):
        return client.ironic_client.port.list()


class MachineNodeGet(task_manager.Task):
    def main(self, client):
        return client.ironic_client.node.get(**self.args)


class MachineNodeList(task_manager.Task):
    def main(self, client):
        return client.ironic_client.node.list(**self.args)


class MachineNodePortList(task_manager.Task):
    def main(self, client):
        return client.ironic_client.node.list_ports(**self.args)


class MachineNodeUpdate(task_manager.Task):
    def main(self, client):
        return client.ironic_client.node.update(**self.args)


class MachineNodeValidate(task_manager.Task):
    def main(self, client):
        return client.ironic_client.node.validate(**self.args)


class MachineSetMaintenance(task_manager.Task):
    def main(self, client):
        return client.ironic_client.node.set_maintenance(**self.args)


class MachineSetPower(task_manager.Task):
    def main(self, client):
        return client.ironic_client.node.set_power_state(**self.args)


class MachineSetProvision(task_manager.Task):
    def main(self, client):
        return client.ironic_client.node.set_provision_state(**self.args)


class ServiceCreate(task_manager.Task):
    def main(self, client):
        return client.keystone_client.services.create(**self.args)


class ServiceList(task_manager.Task):
    def main(self, client):
        return client.keystone_client.services.list()


class ServiceDelete(task_manager.Task):
    def main(self, client):
        return client.keystone_client.services.delete(**self.args)


class EndpointCreate(task_manager.Task):
    def main(self, client):
        return client.keystone_client.endpoints.create(**self.args)


class EndpointList(task_manager.Task):
    def main(self, client):
        return client.keystone_client.endpoints.list()


class EndpointDelete(task_manager.Task):
    def main(self, client):
        return client.keystone_client.endpoints.delete(**self.args)


# IdentityDomain and not Domain because Domain is a DNS concept
class IdentityDomainCreate(task_manager.Task):
    def main(self, client):
        return client.keystone_client.domains.create(**self.args)


# IdentityDomain and not Domain because Domain is a DNS concept
class IdentityDomainList(task_manager.Task):
    def main(self, client):
        return client.keystone_client.domains.list()


# IdentityDomain and not Domain because Domain is a DNS concept
class IdentityDomainGet(task_manager.Task):
    def main(self, client):
        return client.keystone_client.domains.get(**self.args)


# IdentityDomain and not Domain because Domain is a DNS concept
class IdentityDomainUpdate(task_manager.Task):
    def main(self, client):
        return client.keystone_client.domains.update(**self.args)


# IdentityDomain and not Domain because Domain is a DNS concept
class IdentityDomainDelete(task_manager.Task):
    def main(self, client):
        return client.keystone_client.domains.delete(**self.args)


class DomainList(task_manager.Task):
    def main(self, client):
        return client.designate_client.domains.list()


class DomainGet(task_manager.Task):
    def main(self, client):
        return client.designate_client.domains.get(**self.args)


class RecordList(task_manager.Task):
    def main(self, client):
        return client.designate_client.records.list(**self.args)


class RecordGet(task_manager.Task):
    def main(self, client):
        return client.designate_client.records.get(**self.args)
