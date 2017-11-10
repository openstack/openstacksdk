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

from openstack.object_store.v1 import container as _container
from openstack.tests.functional import base


class TestContainer(base.BaseFunctionalTest):

    def setUp(self):
        super(TestContainer, self).setUp()
        self.require_service('object-store')

        self.NAME = self.getUniqueString()
        container = self.conn.object_store.create_container(name=self.NAME)
        self.addEmptyCleanup(
            self.conn.object_store.delete_container,
            self.NAME, ignore_missing=False)
        assert isinstance(container, _container.Container)
        self.assertEqual(self.NAME, container.name)

    def test_list(self):
        names = [o.name for o in self.conn.object_store.containers()]
        self.assertIn(self.NAME, names)

    def test_system_metadata(self):
        # get system metadata
        container = self.conn.object_store.get_container_metadata(self.NAME)
        self.assertEqual(0, container.object_count)
        self.assertEqual(0, container.bytes_used)

        # set system metadata
        container = self.conn.object_store.get_container_metadata(self.NAME)
        self.assertIsNone(container.read_ACL)
        self.assertIsNone(container.write_ACL)
        self.conn.object_store.set_container_metadata(
            container, read_ACL='.r:*', write_ACL='demo:demo')
        container = self.conn.object_store.get_container_metadata(self.NAME)
        self.assertEqual('.r:*', container.read_ACL)
        self.assertEqual('demo:demo', container.write_ACL)

        # update system metadata
        self.conn.object_store.set_container_metadata(
            container, read_ACL='.r:demo')
        container = self.conn.object_store.get_container_metadata(self.NAME)
        self.assertEqual('.r:demo', container.read_ACL)
        self.assertEqual('demo:demo', container.write_ACL)

        # set system metadata and custom metadata
        self.conn.object_store.set_container_metadata(
            container, k0='v0', sync_key='1234')
        container = self.conn.object_store.get_container_metadata(self.NAME)
        self.assertTrue(container.metadata)
        self.assertIn('k0', container.metadata)
        self.assertEqual('v0', container.metadata['k0'])
        self.assertEqual('.r:demo', container.read_ACL)
        self.assertEqual('demo:demo', container.write_ACL)
        self.assertEqual('1234', container.sync_key)

        # unset system metadata
        self.conn.object_store.delete_container_metadata(container,
                                                         ['sync_key'])
        container = self.conn.object_store.get_container_metadata(self.NAME)
        self.assertTrue(container.metadata)
        self.assertIn('k0', container.metadata)
        self.assertEqual('v0', container.metadata['k0'])
        self.assertEqual('.r:demo', container.read_ACL)
        self.assertEqual('demo:demo', container.write_ACL)
        self.assertIsNone(container.sync_key)

    def test_custom_metadata(self):
        # get custom metadata
        container = self.conn.object_store.get_container_metadata(self.NAME)
        self.assertFalse(container.metadata)

        # set no custom metadata
        self.conn.object_store.set_container_metadata(container)
        container = self.conn.object_store.get_container_metadata(container)
        self.assertFalse(container.metadata)

        # set empty custom metadata
        self.conn.object_store.set_container_metadata(container, k0='')
        container = self.conn.object_store.get_container_metadata(container)
        self.assertFalse(container.metadata)

        # set custom metadata
        self.conn.object_store.set_container_metadata(container, k1='v1')
        container = self.conn.object_store.get_container_metadata(container)
        self.assertTrue(container.metadata)
        self.assertEqual(1, len(container.metadata))
        self.assertIn('k1', container.metadata)
        self.assertEqual('v1', container.metadata['k1'])

        # set more custom metadata by named container
        self.conn.object_store.set_container_metadata(self.NAME, k2='v2')
        container = self.conn.object_store.get_container_metadata(container)
        self.assertTrue(container.metadata)
        self.assertEqual(2, len(container.metadata))
        self.assertIn('k1', container.metadata)
        self.assertEqual('v1', container.metadata['k1'])
        self.assertIn('k2', container.metadata)
        self.assertEqual('v2', container.metadata['k2'])

        # update metadata
        self.conn.object_store.set_container_metadata(container, k1='v1.1')
        container = self.conn.object_store.get_container_metadata(self.NAME)
        self.assertTrue(container.metadata)
        self.assertEqual(2, len(container.metadata))
        self.assertIn('k1', container.metadata)
        self.assertEqual('v1.1', container.metadata['k1'])
        self.assertIn('k2', container.metadata)
        self.assertEqual('v2', container.metadata['k2'])

        # delete metadata
        self.conn.object_store.delete_container_metadata(container, ['k1'])
        container = self.conn.object_store.get_container_metadata(self.NAME)
        self.assertTrue(container.metadata)
        self.assertEqual(1, len(container.metadata))
        self.assertIn('k2', container.metadata)
        self.assertEqual('v2', container.metadata['k2'])
