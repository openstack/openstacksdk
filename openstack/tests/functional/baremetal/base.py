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

import typing as ty

from openstack.tests.functional import base


class BaseBaremetalTest(base.BaseFunctionalTest):
    min_microversion: ty.Optional[str] = None
    node_id: str

    def setUp(self):
        super().setUp()
        self.require_service(
            'baremetal', min_microversion=self.min_microversion
        )

    def create_allocation(self, **kwargs):
        allocation = self.operator_cloud.baremetal.create_allocation(**kwargs)
        self.addCleanup(
            lambda: self.operator_cloud.baremetal.delete_allocation(
                allocation.id, ignore_missing=True
            )
        )
        return allocation

    def create_chassis(self, **kwargs):
        chassis = self.operator_cloud.baremetal.create_chassis(**kwargs)
        self.addCleanup(
            lambda: self.operator_cloud.baremetal.delete_chassis(
                chassis.id, ignore_missing=True
            )
        )
        return chassis

    def create_node(self, driver='fake-hardware', **kwargs):
        node = self.operator_cloud.baremetal.create_node(
            driver=driver, **kwargs
        )
        self.node_id = node.id
        self.addCleanup(
            lambda: self.operator_cloud.baremetal.delete_node(
                self.node_id, ignore_missing=True
            )
        )
        self.assertIsNotNone(self.node_id)
        return node

    def create_port(self, node_id=None, **kwargs):
        node_id = node_id or self.node_id
        port = self.operator_cloud.baremetal.create_port(
            node_uuid=node_id, **kwargs
        )
        self.addCleanup(
            lambda: self.operator_cloud.baremetal.delete_port(
                port.id, ignore_missing=True
            )
        )
        return port

    def create_port_group(self, node_id=None, **kwargs):
        node_id = node_id or self.node_id
        port_group = self.operator_cloud.baremetal.create_port_group(
            node_uuid=node_id, **kwargs
        )
        self.addCleanup(
            lambda: self.operator_cloud.baremetal.delete_port_group(
                port_group.id, ignore_missing=True
            )
        )
        return port_group

    def create_volume_connector(self, node_id=None, **kwargs):
        node_id = node_id or self.node_id
        volume_connector = (
            self.operator_cloud.baremetal.create_volume_connector(
                node_uuid=node_id, **kwargs
            )
        )

        self.addCleanup(
            lambda: self.operator_cloud.baremetal.delete_volume_connector(
                volume_connector.id, ignore_missing=True
            )
        )
        return volume_connector

    def create_volume_target(self, node_id=None, **kwargs):
        node_id = node_id or self.node_id
        volume_target = self.operator_cloud.baremetal.create_volume_target(
            node_uuid=node_id, **kwargs
        )

        self.addCleanup(
            lambda: self.operator_cloud.baremetal.delete_volume_target(
                volume_target.id, ignore_missing=True
            )
        )
        return volume_target

    def create_deploy_template(self, **kwargs):
        """Create a new deploy_template from attributes."""

        deploy_template = self.operator_cloud.baremetal.create_deploy_template(
            **kwargs
        )

        self.addCleanup(
            lambda: self.operator_cloud.baremetal.delete_deploy_template(
                deploy_template.id, ignore_missing=True
            )
        )
        return deploy_template
