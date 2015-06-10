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

from openstack.cluster.v1 import _proxy
from openstack.cluster.v1 import cluster
from openstack.tests.unit import test_proxy_base


class TestClusterProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestClusterProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_cluster_create(self):
        self.verify_create(self.proxy.create_cluster, cluster.Cluster)

    def test_cluster_delete(self):
        self.verify_delete(self.proxy.delete_cluster, cluster.Cluster, False)

    def test_cluster_delete_ignore(self):
        self.verify_delete(self.proxy.delete_cluster, cluster.Cluster, True)

    def test_cluster_find(self):
        self.verify_find('openstack.cluster.v1.cluster.Cluster.find',
                         self.proxy.find_cluster)

    def test_cluster_get(self):
        self.verify_get(self.proxy.get_cluster, cluster.Cluster)

    def test_clusters(self):
        self.verify_list(self.proxy.clusters, cluster.Cluster,
                         paginated=True,
                         method_kwargs={'limit': 2},
                         expected_kwargs={'limit': 2})

    def test_cluster_update(self):
        self.verify_update(self.proxy.update_cluster, cluster.Cluster)
