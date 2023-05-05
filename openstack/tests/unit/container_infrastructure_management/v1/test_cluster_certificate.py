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

from openstack.container_infrastructure_management.v1 import (
    cluster_certificate,
)
from openstack.tests.unit import base

EXAMPLE = {
    "cluster_uuid": "0b4b766f-1500-44b3-9804-5a6e12fe6df4",
    "pem": "-----BEGIN CERTIFICATE-----\nMIICzDCCAbSgAwIBAgIQOOkVcEN7TNa9E80G",
    "bay_uuid": "0b4b766f-1500-44b3-9804-5a6e12fe6df4",
    "csr": "-----BEGIN CERTIFICATE REQUEST-----\nMIIEfzCCAmcCAQAwFDESMBAGA1UE",
}


class TestClusterCertificate(base.TestCase):
    def test_basic(self):
        sot = cluster_certificate.ClusterCertificate()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('/certificates', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertFalse(sot.allow_list)

    def test_make_it(self):
        sot = cluster_certificate.ClusterCertificate(**EXAMPLE)

        self.assertEqual(EXAMPLE['cluster_uuid'], sot.cluster_uuid)
        self.assertEqual(EXAMPLE['bay_uuid'], sot.bay_uuid)
        self.assertEqual(EXAMPLE['csr'], sot.csr)
        self.assertEqual(EXAMPLE['pem'], sot.pem)
