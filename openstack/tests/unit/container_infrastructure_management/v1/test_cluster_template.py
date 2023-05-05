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

from openstack.container_infrastructure_management.v1 import cluster_template
from openstack.tests.unit import base

EXAMPLE = {
    "insecure_registry": None,
    "http_proxy": "http://10.164.177.169:8080",
    "updated_at": None,
    "floating_ip_enabled": True,
    "fixed_subnet": None,
    "master_flavor_id": None,
    "uuid": "085e1c4d-4f68-4bfd-8462-74b9e14e4f39",
    "no_proxy": "10.0.0.0/8,172.0.0.0/8,192.0.0.0/8,localhost",
    "https_proxy": "http://10.164.177.169:8080",
    "tls_disabled": False,
    "keypair_id": "kp",
    "public": False,
    "labels": {},
    "docker_volume_size": 3,
    "server_type": "vm",
    "external_network_id": "public",
    "cluster_distro": "fedora-atomic",
    "image_id": "fedora-atomic-latest",
    "volume_driver": "cinder",
    "registry_enabled": False,
    "docker_storage_driver": "devicemapper",
    "apiserver_port": None,
    "name": "k8s-bm2",
    "created_at": "2016-08-29T02:08:08+00:00",
    "network_driver": "flannel",
    "fixed_network": None,
    "coe": "kubernetes",
    "flavor_id": "m1.small",
    "master_lb_enabled": True,
    "dns_nameserver": "8.8.8.8",
    "hidden": True,
}


class TestClusterTemplate(base.TestCase):
    def test_basic(self):
        sot = cluster_template.ClusterTemplate()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('clustertemplates', sot.resources_key)
        self.assertEqual('/clustertemplates', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = cluster_template.ClusterTemplate(**EXAMPLE)

        self.assertEqual(EXAMPLE['apiserver_port'], sot.apiserver_port)
        self.assertEqual(EXAMPLE['cluster_distro'], sot.cluster_distro)
        self.assertEqual(EXAMPLE['coe'], sot.coe)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(
            EXAMPLE['docker_storage_driver'], sot.docker_storage_driver
        )
        self.assertEqual(EXAMPLE['docker_volume_size'], sot.docker_volume_size)
        self.assertEqual(EXAMPLE['dns_nameserver'], sot.dns_nameserver)
        self.assertEqual(
            EXAMPLE['external_network_id'], sot.external_network_id
        )
        self.assertEqual(EXAMPLE['fixed_network'], sot.fixed_network)
        self.assertEqual(EXAMPLE['fixed_subnet'], sot.fixed_subnet)
        self.assertEqual(EXAMPLE['flavor_id'], sot.flavor_id)
        self.assertEqual(EXAMPLE['http_proxy'], sot.http_proxy)
        self.assertEqual(EXAMPLE['https_proxy'], sot.https_proxy)
        self.assertEqual(EXAMPLE['image_id'], sot.image_id)
        self.assertEqual(EXAMPLE['insecure_registry'], sot.insecure_registry)
        self.assertEqual(
            EXAMPLE['floating_ip_enabled'], sot.is_floating_ip_enabled
        )
        self.assertEqual(EXAMPLE['hidden'], sot.is_hidden)
        self.assertEqual(
            EXAMPLE['master_lb_enabled'], sot.is_master_lb_enabled
        )
        self.assertEqual(EXAMPLE['tls_disabled'], sot.is_tls_disabled)
        self.assertEqual(EXAMPLE['public'], sot.is_public)
        self.assertEqual(EXAMPLE['registry_enabled'], sot.is_registry_enabled)
        self.assertEqual(EXAMPLE['keypair_id'], sot.keypair_id)
        self.assertEqual(EXAMPLE['master_flavor_id'], sot.master_flavor_id)
        self.assertEqual(EXAMPLE['network_driver'], sot.network_driver)
        self.assertEqual(EXAMPLE['no_proxy'], sot.no_proxy)
        self.assertEqual(EXAMPLE['server_type'], sot.server_type)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)
        self.assertEqual(EXAMPLE['uuid'], sot.uuid)
        self.assertEqual(EXAMPLE['volume_driver'], sot.volume_driver)
