# -*- coding: utf-8 -*-

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
test_baymodels
----------------------------------

Functional tests for `shade` baymodel methods.
"""

from testtools import content

from shade.tests.functional import base

import os
import subprocess


class TestBaymodel(base.BaseFunctionalTestCase):

    def setUp(self):
        super(TestBaymodel, self).setUp()
        if not self.demo_cloud.has_service('container'):
            self.skipTest('Container service not supported by cloud')
        self.baymodel = None

    def test_baymodels(self):
        '''Test baymodels functionality'''
        name = 'fake-baymodel'
        server_type = 'vm'
        public = False
        image_id = 'fedora-atomic-f23-dib'
        tls_disabled = False
        registry_enabled = False
        coe = 'kubernetes'
        keypair_id = 'testkey'

        self.addDetail('baymodel', content.text_content(name))
        self.addCleanup(self.cleanup, name)

        # generate a keypair to add to nova
        ssh_directory = '/tmp/.ssh'
        if not os.path.isdir(ssh_directory):
            os.mkdir(ssh_directory)
        subprocess.call(
            ['ssh-keygen', '-t', 'rsa', '-N', '', '-f',
             '%s/id_rsa_shade' % ssh_directory])

        # add keypair to nova
        with open('%s/id_rsa_shade.pub' % ssh_directory) as f:
            key_content = f.read()
            self.demo_cloud.create_keypair('testkey', key_content)

        # Test we can create a baymodel and we get it returned
        self.baymodel = self.demo_cloud.create_baymodel(
            name=name, image_id=image_id,
            keypair_id=keypair_id, coe=coe)
        self.assertEquals(self.baymodel['name'], name)
        self.assertEquals(self.baymodel['image_id'], image_id)
        self.assertEquals(self.baymodel['keypair_id'], keypair_id)
        self.assertEquals(self.baymodel['coe'], coe)
        self.assertEquals(self.baymodel['registry_enabled'], registry_enabled)
        self.assertEquals(self.baymodel['tls_disabled'], tls_disabled)
        self.assertEquals(self.baymodel['public'], public)
        self.assertEquals(self.baymodel['server_type'], server_type)

        # Test that we can list baymodels
        baymodels = self.demo_cloud.list_baymodels()
        self.assertIsNotNone(baymodels)

        # Test we get the same baymodel with the get_baymodel method
        baymodel_get = self.demo_cloud.get_baymodel(self.baymodel['uuid'])
        self.assertEquals(baymodel_get['uuid'], self.baymodel['uuid'])

        # Test the get method also works by name
        baymodel_get = self.demo_cloud.get_baymodel(name)
        self.assertEquals(baymodel_get['name'], self.baymodel['name'])

        # Test we can update a field on the baymodel and only that field
        # is updated
        baymodel_update = self.demo_cloud.update_baymodel(
            self.baymodel['uuid'], 'replace', tls_disabled=True)
        self.assertEquals(baymodel_update['uuid'],
                          self.baymodel['uuid'])
        self.assertEquals(baymodel_update['tls_disabled'], True)

        # Test we can delete and get True returned
        baymodel_delete = self.demo_cloud.delete_baymodel(
            self.baymodel['uuid'])
        self.assertTrue(baymodel_delete)

    def cleanup(self, name):
        if self.baymodel:
            try:
                self.demo_cloud.delete_baymodel(self.baymodel['name'])
            except:
                pass

        # delete keypair
        self.demo_cloud.delete_keypair('testkey')
        os.unlink('/tmp/.ssh/id_rsa_shade')
        os.unlink('/tmp/.ssh/id_rsa_shade.pub')
