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


class UserPasswordUpdate(task_manager.Task):
    def main(self, client):
        return client.keystone_client.users.update_password(**self.args)


class UserGet(task_manager.Task):
    def main(self, client):
        return client.keystone_client.users.get(**self.args)


class UserAddToGroup(task_manager.Task):
    def main(self, client):
        return client.keystone_client.users.add_to_group(**self.args)


class UserCheckInGroup(task_manager.Task):
    def main(self, client):
        return client.keystone_client.users.check_in_group(**self.args)


class UserRemoveFromGroup(task_manager.Task):
    def main(self, client):
        return client.keystone_client.users.remove_from_group(**self.args)


class ProjectList(task_manager.Task):
    def main(self, client):
        return client._project_manager.list(**self.args)


class ProjectCreate(task_manager.Task):
    def main(self, client):
        return client._project_manager.create(**self.args)


class ProjectDelete(task_manager.Task):
    def main(self, client):
        return client._project_manager.delete(**self.args)


class ProjectUpdate(task_manager.Task):
    def main(self, client):
        return client._project_manager.update(**self.args)


class ServerList(task_manager.Task):
    def main(self, client):
        return client.nova_client.servers.list(**self.args)


class ServerListSecurityGroups(task_manager.Task):
    def main(self, client):
        return client.nova_client.servers.list_security_group(**self.args)


class ServerConsoleGet(task_manager.Task):
    def main(self, client):
        return client.nova_client.servers.get_console_output(**self.args)


class ServerGet(task_manager.Task):
    def main(self, client):
        return client.nova_client.servers.get(**self.args)


class ServerCreate(task_manager.Task):
    def main(self, client):
        return client.nova_client.servers.create(**self.args)


class ServerDelete(task_manager.Task):
    def main(self, client):
        return client.nova_client.servers.delete(**self.args)


class ServerUpdate(task_manager.Task):
    def main(self, client):
        return client.nova_client.servers.update(**self.args)


class ServerRebuild(task_manager.Task):
    def main(self, client):
        return client.nova_client.servers.rebuild(**self.args)


class ServerSetMetadata(task_manager.Task):
    def main(self, client):
        return client.nova_client.servers.set_meta(**self.args)


class ServerDeleteMetadata(task_manager.Task):
    def main(self, client):
        return client.nova_client.servers.delete_meta(**self.args)


class ServerGroupList(task_manager.Task):
    def main(self, client):
        return client.nova_client.server_groups.list(**self.args)


class ServerGroupGet(task_manager.Task):
    def main(self, client):
        return client.nova_client.server_groups.get(**self.args)


class ServerGroupCreate(task_manager.Task):
    def main(self, client):
        return client.nova_client.server_groups.create(**self.args)


class ServerGroupDelete(task_manager.Task):
    def main(self, client):
        return client.nova_client.server_groups.delete(**self.args)


class HypervisorList(task_manager.Task):
    def main(self, client):
        return client.nova_client.hypervisors.list(**self.args)


class AggregateList(task_manager.Task):
    def main(self, client):
        return client.nova_client.aggregates.list(**self.args)


class AggregateCreate(task_manager.Task):
    def main(self, client):
        return client.nova_client.aggregates.create(**self.args)


class AggregateUpdate(task_manager.Task):
    def main(self, client):
        return client.nova_client.aggregates.update(**self.args)


class AggregateDelete(task_manager.Task):
    def main(self, client):
        return client.nova_client.aggregates.delete(**self.args)


class AggregateAddHost(task_manager.Task):
    def main(self, client):
        return client.nova_client.aggregates.add_host(**self.args)


class AggregateRemoveHost(task_manager.Task):
    def main(self, client):
        return client.nova_client.aggregates.remove_host(**self.args)


class AggregateSetMetadata(task_manager.Task):
    def main(self, client):
        return client.nova_client.aggregates.set_metadata(**self.args)


class KeypairList(task_manager.Task):
    def main(self, client):
        return client.nova_client.keypairs.list()


class KeypairCreate(task_manager.Task):
    def main(self, client):
        return client.nova_client.keypairs.create(**self.args)


class KeypairDelete(task_manager.Task):
    def main(self, client):
        return client.nova_client.keypairs.delete(**self.args)


class NetworkList(task_manager.Task):
    def main(self, client):
        return client.neutron_client.list_networks(**self.args)


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
        return client.neutron_client.delete_router(**self.args)


class RouterAddInterface(task_manager.Task):
    def main(self, client):
        return client.neutron_client.add_interface_router(**self.args)


class RouterRemoveInterface(task_manager.Task):
    def main(self, client):
        client.neutron_client.remove_interface_router(**self.args)


class NovaImageList(task_manager.Task):
    def main(self, client):
        return client.nova_client.images.list()


class ImageSnapshotCreate(task_manager.Task):
    def main(self, client):
        return client.nova_client.servers.create_image(**self.args)


class VolumeTypeList(task_manager.Task):
    def main(self, client):
        return client.cinder_client.volume_types.list()


class VolumeTypeAccessList(task_manager.Task):
    def main(self, client):
        return client.cinder_client.volume_type_access.list(**self.args)


class VolumeTypeAccessAdd(task_manager.Task):
    def main(self, client):
        return client.cinder_client.volume_type_access.add_project_access(
            **self.args)


class VolumeTypeAccessRemove(task_manager.Task):
    def main(self, client):
        return client.cinder_client.volume_type_access.remove_project_access(
            **self.args)


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
        return client.nova_client.volumes.create_server_volume(**self.args)


class VolumeSnapshotCreate(task_manager.Task):
    def main(self, client):
        return client.cinder_client.volume_snapshots.create(**self.args)


class VolumeSnapshotGet(task_manager.Task):
    def main(self, client):
        return client.cinder_client.volume_snapshots.get(**self.args)


class VolumeSnapshotList(task_manager.Task):
    def main(self, client):
        return client.cinder_client.volume_snapshots.list(**self.args)


class VolumeBackupList(task_manager.Task):
    def main(self, client):
        return client.cinder_client.backups.list(**self.args)


class VolumeBackupCreate(task_manager.Task):
    def main(self, client):
        return client.cinder_client.backups.create(**self.args)


class VolumeBackupDelete(task_manager.Task):
    def main(self, client):
        return client.cinder_client.backups.delete(**self.args)


class VolumeSnapshotDelete(task_manager.Task):
    def main(self, client):
        return client.cinder_client.volume_snapshots.delete(**self.args)


class NeutronSecurityGroupList(task_manager.Task):
    def main(self, client):
        return client.neutron_client.list_security_groups(**self.args)


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
        return client.nova_client.security_groups.list(**self.args)


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


class ServiceUpdate(task_manager.Task):
    def main(self, client):
        return client.keystone_client.services.update(**self.args)


class ServiceDelete(task_manager.Task):
    def main(self, client):
        return client.keystone_client.services.delete(**self.args)


class EndpointCreate(task_manager.Task):
    def main(self, client):
        return client.keystone_client.endpoints.create(**self.args)


class EndpointUpdate(task_manager.Task):
    def main(self, client):
        return client.keystone_client.endpoints.update(**self.args)


class EndpointList(task_manager.Task):
    def main(self, client):
        return client.keystone_client.endpoints.list()


class EndpointDelete(task_manager.Task):
    def main(self, client):
        return client.keystone_client.endpoints.delete(**self.args)


class DomainCreate(task_manager.Task):
    def main(self, client):
        return client.keystone_client.domains.create(**self.args)


class DomainList(task_manager.Task):
    def main(self, client):
        return client.keystone_client.domains.list(**self.args)


class DomainGet(task_manager.Task):
    def main(self, client):
        return client.keystone_client.domains.get(**self.args)


class DomainUpdate(task_manager.Task):
    def main(self, client):
        return client.keystone_client.domains.update(**self.args)


class DomainDelete(task_manager.Task):
    def main(self, client):
        return client.keystone_client.domains.delete(**self.args)


class GroupList(task_manager.Task):
    def main(self, client):
        return client.keystone_client.groups.list()


class GroupCreate(task_manager.Task):
    def main(self, client):
        return client.keystone_client.groups.create(**self.args)


class GroupDelete(task_manager.Task):
    def main(self, client):
        return client.keystone_client.groups.delete(**self.args)


class GroupUpdate(task_manager.Task):
    def main(self, client):
        return client.keystone_client.groups.update(**self.args)


class RoleList(task_manager.Task):
    def main(self, client):
        return client.keystone_client.roles.list()


class RoleCreate(task_manager.Task):
    def main(self, client):
        return client.keystone_client.roles.create(**self.args)


class RoleDelete(task_manager.Task):
    def main(self, client):
        return client.keystone_client.roles.delete(**self.args)


class RoleAddUser(task_manager.Task):
    def main(self, client):
        return client.keystone_client.roles.add_user_role(**self.args)


class RoleGrantUser(task_manager.Task):
    def main(self, client):
        return client.keystone_client.roles.grant(**self.args)


class RoleRemoveUser(task_manager.Task):
    def main(self, client):
        return client.keystone_client.roles.remove_user_role(**self.args)


class RoleRevokeUser(task_manager.Task):
    def main(self, client):
        return client.keystone_client.roles.revoke(**self.args)


class RoleAssignmentList(task_manager.Task):
    def main(self, client):
        return client.keystone_client.role_assignments.list(**self.args)


class RolesForUser(task_manager.Task):
    def main(self, client):
        return client.keystone_client.roles.roles_for_user(**self.args)


class StackList(task_manager.Task):
    def main(self, client):
        return client.heat_client.stacks.list()


class StackCreate(task_manager.Task):
    def main(self, client):
        return client.heat_client.stacks.create(**self.args)


class StackUpdate(task_manager.Task):
    def main(self, client):
        return client.heat_client.stacks.update(**self.args)


class StackDelete(task_manager.Task):
    def main(self, client):
        return client.heat_client.stacks.delete(self.args['id'])


class StackGet(task_manager.Task):
    def main(self, client):
        return client.heat_client.stacks.get(**self.args)


class ZoneList(task_manager.Task):
    def main(self, client):
        return client.designate_client.zones.list()


class ZoneCreate(task_manager.Task):
    def main(self, client):
        return client.designate_client.zones.create(**self.args)


class ZoneUpdate(task_manager.Task):
    def main(self, client):
        return client.designate_client.zones.update(**self.args)


class ZoneDelete(task_manager.Task):
    def main(self, client):
        return client.designate_client.zones.delete(**self.args)


class RecordSetList(task_manager.Task):
    def main(self, client):
        return client.designate_client.recordsets.list(**self.args)


class RecordSetGet(task_manager.Task):
    def main(self, client):
        return client.designate_client.recordsets.get(**self.args)


class RecordSetCreate(task_manager.Task):
    def main(self, client):
        return client.designate_client.recordsets.create(**self.args)


class RecordSetUpdate(task_manager.Task):
    def main(self, client):
        return client.designate_client.recordsets.update(**self.args)


class RecordSetDelete(task_manager.Task):
    def main(self, client):
        return client.designate_client.recordsets.delete(**self.args)


class NovaQuotasSet(task_manager.Task):
    def main(self, client):
        return client.nova_client.quotas.update(**self.args)


class NovaQuotasGet(task_manager.Task):
    def main(self, client):
        return client.nova_client.quotas.get(**self.args)


class NovaQuotasDelete(task_manager.Task):
    def main(self, client):
        return client.nova_client.quotas.delete(**self.args)


class NovaUsageGet(task_manager.Task):
    def main(self, client):
        return client.nova_client.usage.get(**self.args)


class CinderQuotasSet(task_manager.Task):
    def main(self, client):
        return client.cinder_client.quotas.update(**self.args)


class CinderQuotasGet(task_manager.Task):
    def main(self, client):
        return client.cinder_client.quotas.get(**self.args)


class CinderQuotasDelete(task_manager.Task):
    def main(self, client):
        return client.cinder_client.quotas.delete(**self.args)


class NeutronQuotasSet(task_manager.Task):
    def main(self, client):
        return client.neutron_client.update_quota(**self.args)


class NeutronQuotasGet(task_manager.Task):
    def main(self, client):
        return client.neutron_client.show_quota(**self.args)['quota']


class NeutronQuotasDelete(task_manager.Task):
    def main(self, client):
        return client.neutron_client.delete_quota(**self.args)


class ClusterTemplateList(task_manager.Task):
    def main(self, client):
        return client.magnum_client.baymodels.list(**self.args)


class ClusterTemplateCreate(task_manager.Task):
    def main(self, client):
        return client.magnum_client.baymodels.create(**self.args)


class ClusterTemplateDelete(task_manager.Task):
    def main(self, client):
        return client.magnum_client.baymodels.delete(self.args['id'])


class ClusterTemplateUpdate(task_manager.Task):
    def main(self, client):
        return client.magnum_client.baymodels.update(
            self.args['id'], self.args['patch'])


class MagnumServicesList(task_manager.Task):
    def main(self, client):
        return client.magnum_client.mservices.list(detail=False)


class NovaLimitsGet(task_manager.Task):
    def main(self, client):
        return client.nova_client.limits.get(**self.args).to_dict()
