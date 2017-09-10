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

from openstack import task_manager


class IronicTask(task_manager.Task):

    def __init__(self, client, **kwargs):
        super(IronicTask, self).__init__(**kwargs)
        self.client = client


class MachineCreate(IronicTask):
    def main(self):
        return self.client.ironic_client.node.create(*self.args, **self.kwargs)


class MachineDelete(IronicTask):
    def main(self):
        return self.client.ironic_client.node.delete(*self.args, **self.kwargs)


class MachinePatch(IronicTask):
    def main(self):
        return self.client.ironic_client.node.update(*self.args, **self.kwargs)


class MachinePortGet(IronicTask):
    def main(self):
        return self.client.ironic_client.port.get(*self.args, **self.kwargs)


class MachinePortGetByAddress(IronicTask):
    def main(self):
        return self.client.ironic_client.port.get_by_address(
            *self.args, **self.kwargs)


class MachinePortCreate(IronicTask):
    def main(self):
        return self.client.ironic_client.port.create(*self.args, **self.kwargs)


class MachinePortDelete(IronicTask):
    def main(self):
        return self.client.ironic_client.port.delete(*self.args, **self.kwargs)


class MachinePortList(IronicTask):
    def main(self):
        return self.client.ironic_client.port.list()


class MachineNodeGet(IronicTask):
    def main(self):
        return self.client.ironic_client.node.get(*self.args, **self.kwargs)


class MachineNodeList(IronicTask):
    def main(self):
        return self.client.ironic_client.node.list(*self.args, **self.kwargs)


class MachineNodePortList(IronicTask):
    def main(self):
        return self.client.ironic_client.node.list_ports(
            *self.args, **self.kwargs)


class MachineNodeUpdate(IronicTask):
    def main(self):
        return self.client.ironic_client.node.update(*self.args, **self.kwargs)


class MachineNodeValidate(IronicTask):
    def main(self):
        return self.client.ironic_client.node.validate(
            *self.args, **self.kwargs)


class MachineSetMaintenance(IronicTask):
    def main(self):
        return self.client.ironic_client.node.set_maintenance(
            *self.args, **self.kwargs)


class MachineSetPower(IronicTask):
    def main(self):
        return self.client.ironic_client.node.set_power_state(
            *self.args, **self.kwargs)


class MachineSetProvision(IronicTask):
    def main(self):
        return self.client.ironic_client.node.set_provision_state(
            *self.args, **self.kwargs)
