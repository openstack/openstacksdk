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
from openstack.container_infrastructure_management.v1 import _proxy
from openstack.container_infrastructure_management.v1 import cluster
from openstack.container_infrastructure_management.v1 import cluster_template
from openstack.container_infrastructure_management.v1 import service
from openstack.tests.unit import test_proxy_base


class TestMagnumProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)


class TestCluster(TestMagnumProxy):
    def test_cluster_get(self):
        self.verify_get(self.proxy.get_cluster, cluster.Cluster)

    def test_cluster_find(self):
        self.verify_find(
            self.proxy.find_cluster,
            cluster.Cluster,
            method_kwargs={},
            expected_kwargs={},
        )

    def test_clusters(self):
        self.verify_list(
            self.proxy.clusters,
            cluster.Cluster,
            method_kwargs={"query": 1},
            expected_kwargs={"query": 1},
        )

    def test_cluster_create_attrs(self):
        self.verify_create(self.proxy.create_cluster, cluster.Cluster)

    def test_cluster_delete(self):
        self.verify_delete(self.proxy.delete_cluster, cluster.Cluster, False)

    def test_cluster_delete_ignore(self):
        self.verify_delete(self.proxy.delete_cluster, cluster.Cluster, True)


class TestClusterCertificate(TestMagnumProxy):
    def test_cluster_certificate_get(self):
        self.verify_get(
            self.proxy.get_cluster_certificate,
            cluster_certificate.ClusterCertificate,
        )

    def test_cluster_certificate_create_attrs(self):
        self.verify_create(
            self.proxy.create_cluster_certificate,
            cluster_certificate.ClusterCertificate,
        )


class TestClusterTemplate(TestMagnumProxy):
    def test_cluster_template_get(self):
        self.verify_get(
            self.proxy.get_cluster_template, cluster_template.ClusterTemplate
        )

    def test_cluster_template_find(self):
        self.verify_find(
            self.proxy.find_cluster_template,
            cluster_template.ClusterTemplate,
            method_kwargs={},
            expected_kwargs={},
        )

    def test_cluster_templates(self):
        self.verify_list(
            self.proxy.cluster_templates,
            cluster_template.ClusterTemplate,
            method_kwargs={"query": 1},
            expected_kwargs={"query": 1},
        )

    def test_cluster_template_create_attrs(self):
        self.verify_create(
            self.proxy.create_cluster_template,
            cluster_template.ClusterTemplate,
        )

    def test_cluster_template_delete(self):
        self.verify_delete(
            self.proxy.delete_cluster_template,
            cluster_template.ClusterTemplate,
            False,
        )

    def test_cluster_template_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_cluster_template,
            cluster_template.ClusterTemplate,
            True,
        )


class TestService(TestMagnumProxy):
    def test_services(self):
        self.verify_list(
            self.proxy.services,
            service.Service,
            method_kwargs={},
            expected_kwargs={},
        )
