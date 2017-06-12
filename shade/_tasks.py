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


class UserCreate(task_manager.Task):
    def main(self, client):
        return client.keystone_client.users.create(**self.args)


class UserUpdate(task_manager.Task):
    def main(self, client):
        return client.keystone_client.users.update(**self.args)


class UserPasswordUpdate(task_manager.Task):
    def main(self, client):
        return client.keystone_client.users.update_password(**self.args)


class UserAddToGroup(task_manager.Task):
    def main(self, client):
        return client.keystone_client.users.add_to_group(**self.args)


class UserCheckInGroup(task_manager.Task):
    def main(self, client):
        return client.keystone_client.users.check_in_group(**self.args)


class UserRemoveFromGroup(task_manager.Task):
    def main(self, client):
        return client.keystone_client.users.remove_from_group(**self.args)


class ProjectUpdate(task_manager.Task):
    def main(self, client):
        return client._project_manager.update(**self.args)


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


class NovaLimitsGet(task_manager.Task):
    def main(self, client):
        return client.nova_client.limits.get(**self.args).to_dict()
