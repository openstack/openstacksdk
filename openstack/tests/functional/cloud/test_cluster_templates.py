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

"""
test_cluster_templates
----------------------------------

Functional tests for `openstack.cloud` cluster_template methods.
"""

import subprocess

import fixtures
from testtools import content

from openstack.tests.functional import base


class TestClusterTemplate(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        if not self.user_cloud.has_service(
            'container-infrastructure-management'
        ):
            self.skipTest('Container service not supported by cloud')
        self.ct = None
        self.ssh_directory = self.useFixture(fixtures.TempDir()).path

    def test_cluster_templates(self):
        '''Test cluster_templates functionality'''
        name = 'fake-cluster_template'
        server_type = 'vm'
        public = False
        image_id = 'fedora-atomic-f23-dib'
        tls_disabled = False
        registry_enabled = False
        coe = 'kubernetes'
        keypair_id = 'testkey'

        self.addDetail('cluster_template', content.text_content(name))
        self.addCleanup(self.cleanup, name)

        # generate a keypair to add to nova
        subprocess.call(
            [
                'ssh-keygen',
                '-t',
                'rsa',
                '-N',
                '',
                '-f',
                f'{self.ssh_directory}/id_rsa_sdk',
            ]
        )

        # add keypair to nova
        with open(f'{self.ssh_directory}/id_rsa_sdk.pub') as f:
            key_content = f.read()
            self.user_cloud.create_keypair('testkey', key_content)

        # Test we can create a cluster_template and we get it returned
        self.ct = self.user_cloud.create_cluster_template(
            name=name, image_id=image_id, keypair_id=keypair_id, coe=coe
        )
        self.assertEqual(self.ct['name'], name)
        self.assertEqual(self.ct['image_id'], image_id)
        self.assertEqual(self.ct['keypair_id'], keypair_id)
        self.assertEqual(self.ct['coe'], coe)
        self.assertEqual(self.ct['registry_enabled'], registry_enabled)
        self.assertEqual(self.ct['tls_disabled'], tls_disabled)
        self.assertEqual(self.ct['public'], public)
        self.assertEqual(self.ct['server_type'], server_type)

        # Test that we can list cluster_templates
        cluster_templates = self.user_cloud.list_cluster_templates()
        self.assertIsNotNone(cluster_templates)

        # Test we get the same cluster_template with the
        # get_cluster_template method
        cluster_template_get = self.user_cloud.get_cluster_template(
            self.ct['uuid']
        )
        self.assertEqual(cluster_template_get['uuid'], self.ct['uuid'])

        # Test the get method also works by name
        cluster_template_get = self.user_cloud.get_cluster_template(name)
        self.assertEqual(cluster_template_get['name'], self.ct['name'])

        # Test we can update a field on the cluster_template and only that
        # field is updated
        cluster_template_update = self.user_cloud.update_cluster_template(
            self.ct, tls_disabled=True
        )
        self.assertEqual(cluster_template_update['uuid'], self.ct['uuid'])
        self.assertTrue(cluster_template_update['tls_disabled'])

        # Test we can delete and get True returned
        cluster_template_delete = self.user_cloud.delete_cluster_template(
            self.ct['uuid']
        )
        self.assertTrue(cluster_template_delete)

    def cleanup(self, name):
        if self.ct:
            try:
                self.user_cloud.delete_cluster_template(self.ct['name'])
            except Exception:
                pass

        # delete keypair
        self.user_cloud.delete_keypair('testkey')
