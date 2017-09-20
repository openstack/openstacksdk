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
