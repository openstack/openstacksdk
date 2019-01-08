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

import mock

from openstack.clustering.v1 import _proxy
from openstack.clustering.v1 import action
from openstack.clustering.v1 import build_info
from openstack.clustering.v1 import cluster
from openstack.clustering.v1 import cluster_attr
from openstack.clustering.v1 import cluster_policy
from openstack.clustering.v1 import event
from openstack.clustering.v1 import node
from openstack.clustering.v1 import policy
from openstack.clustering.v1 import policy_type
from openstack.clustering.v1 import profile
from openstack.clustering.v1 import profile_type
from openstack.clustering.v1 import receiver
from openstack.clustering.v1 import service
from openstack import proxy as proxy_base
from openstack.tests.unit import test_proxy_base


class TestClusterProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestClusterProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_build_info_get(self):
        self.verify_get(self.proxy.get_build_info, build_info.BuildInfo,
                        ignore_value=True,
                        expected_kwargs={'requires_id': False})

    def test_profile_types(self):
        self.verify_list(self.proxy.profile_types,
                         profile_type.ProfileType)

    def test_profile_type_get(self):
        self.verify_get(self.proxy.get_profile_type,
                        profile_type.ProfileType)

    def test_policy_types(self):
        self.verify_list(self.proxy.policy_types, policy_type.PolicyType)

    def test_policy_type_get(self):
        self.verify_get(self.proxy.get_policy_type, policy_type.PolicyType)

    def test_profile_create(self):
        self.verify_create(self.proxy.create_profile, profile.Profile)

    def test_profile_validate(self):
        self.verify_create(self.proxy.validate_profile,
                           profile.ProfileValidate)

    def test_profile_delete(self):
        self.verify_delete(self.proxy.delete_profile, profile.Profile, False)

    def test_profile_delete_ignore(self):
        self.verify_delete(self.proxy.delete_profile, profile.Profile, True)

    def test_profile_find(self):
        self.verify_find(self.proxy.find_profile, profile.Profile)

    def test_profile_get(self):
        self.verify_get(self.proxy.get_profile, profile.Profile)

    def test_profiles(self):
        self.verify_list(self.proxy.profiles, profile.Profile,
                         method_kwargs={'limit': 2},
                         expected_kwargs={'limit': 2})

    def test_profile_update(self):
        self.verify_update(self.proxy.update_profile, profile.Profile)

    def test_cluster_create(self):
        self.verify_create(self.proxy.create_cluster, cluster.Cluster)

    def test_cluster_delete(self):
        self.verify_delete(self.proxy.delete_cluster, cluster.Cluster, False)

    def test_cluster_delete_ignore(self):
        self.verify_delete(self.proxy.delete_cluster, cluster.Cluster, True)

    def test_cluster_force_delete(self):
        self._verify("openstack.clustering.v1.cluster.Cluster.force_delete",
                     self.proxy.delete_cluster,
                     method_args=["value", False, True])

    def test_cluster_find(self):
        self.verify_find(self.proxy.find_cluster, cluster.Cluster)

    def test_cluster_get(self):
        self.verify_get(self.proxy.get_cluster, cluster.Cluster)

    def test_clusters(self):
        self.verify_list(self.proxy.clusters, cluster.Cluster,
                         method_kwargs={'limit': 2},
                         expected_kwargs={'limit': 2})

    def test_cluster_update(self):
        self.verify_update(self.proxy.update_cluster, cluster.Cluster)

    def test_services(self):
        self.verify_list(self.proxy.services,
                         service.Service)

    @mock.patch.object(proxy_base.Proxy, '_find')
    def test_resize_cluster(self, mock_find):
        mock_cluster = cluster.Cluster.new(id='FAKE_CLUSTER')
        mock_find.return_value = mock_cluster
        self._verify("openstack.clustering.v1.cluster.Cluster.resize",
                     self.proxy.resize_cluster,
                     method_args=["FAKE_CLUSTER"],
                     method_kwargs={'k1': 'v1', 'k2': 'v2'},
                     expected_kwargs={'k1': 'v1', 'k2': 'v2'})
        mock_find.assert_called_once_with(cluster.Cluster, "FAKE_CLUSTER",
                                          ignore_missing=False)

    def test_resize_cluster_with_obj(self):
        mock_cluster = cluster.Cluster.new(id='FAKE_CLUSTER')
        self._verify("openstack.clustering.v1.cluster.Cluster.resize",
                     self.proxy.resize_cluster,
                     method_args=[mock_cluster],
                     method_kwargs={'k1': 'v1', 'k2': 'v2'},
                     expected_kwargs={'k1': 'v1', 'k2': 'v2'})

    def test_collect_cluster_attrs(self):
        self.verify_list(self.proxy.collect_cluster_attrs,
                         cluster_attr.ClusterAttr,
                         method_args=['FAKE_ID', 'path.to.attr'],
                         expected_kwargs={'cluster_id': 'FAKE_ID',
                                          'path': 'path.to.attr'})

    @mock.patch.object(proxy_base.Proxy, '_get_resource')
    def test_cluster_check(self, mock_get):
        mock_cluster = cluster.Cluster.new(id='FAKE_CLUSTER')
        mock_get.return_value = mock_cluster
        self._verify("openstack.clustering.v1.cluster.Cluster.check",
                     self.proxy.check_cluster,
                     method_args=["FAKE_CLUSTER"])
        mock_get.assert_called_once_with(cluster.Cluster, "FAKE_CLUSTER")

    @mock.patch.object(proxy_base.Proxy, '_get_resource')
    def test_cluster_recover(self, mock_get):
        mock_cluster = cluster.Cluster.new(id='FAKE_CLUSTER')
        mock_get.return_value = mock_cluster
        self._verify("openstack.clustering.v1.cluster.Cluster.recover",
                     self.proxy.recover_cluster,
                     method_args=["FAKE_CLUSTER"])
        mock_get.assert_called_once_with(cluster.Cluster, "FAKE_CLUSTER")

    def test_node_create(self):
        self.verify_create(self.proxy.create_node, node.Node)

    def test_node_delete(self):
        self.verify_delete(self.proxy.delete_node, node.Node, False)

    def test_node_delete_ignore(self):
        self.verify_delete(self.proxy.delete_node, node.Node, True)

    def test_node_force_delete(self):
        self._verify("openstack.clustering.v1.node.Node.force_delete",
                     self.proxy.delete_node,
                     method_args=["value", False, True])

    def test_node_find(self):
        self.verify_find(self.proxy.find_node, node.Node)

    def test_node_get(self):
        self.verify_get(self.proxy.get_node, node.Node)

    def test_node_get_with_details(self):
        self._verify2('openstack.proxy.Proxy._get',
                      self.proxy.get_node,
                      method_args=['NODE_ID'],
                      method_kwargs={'details': True},
                      expected_args=[node.NodeDetail],
                      expected_kwargs={'node_id': 'NODE_ID',
                                       'requires_id': False})

    def test_nodes(self):
        self.verify_list(self.proxy.nodes, node.Node,
                         method_kwargs={'limit': 2},
                         expected_kwargs={'limit': 2})

    def test_node_update(self):
        self.verify_update(self.proxy.update_node, node.Node)

    @mock.patch.object(proxy_base.Proxy, '_get_resource')
    def test_node_check(self, mock_get):
        mock_node = node.Node.new(id='FAKE_NODE')
        mock_get.return_value = mock_node
        self._verify("openstack.clustering.v1.node.Node.check",
                     self.proxy.check_node,
                     method_args=["FAKE_NODE"])
        mock_get.assert_called_once_with(node.Node, "FAKE_NODE")

    @mock.patch.object(proxy_base.Proxy, '_get_resource')
    def test_node_recover(self, mock_get):
        mock_node = node.Node.new(id='FAKE_NODE')
        mock_get.return_value = mock_node
        self._verify("openstack.clustering.v1.node.Node.recover",
                     self.proxy.recover_node,
                     method_args=["FAKE_NODE"])
        mock_get.assert_called_once_with(node.Node, "FAKE_NODE")

    @mock.patch.object(proxy_base.Proxy, '_get_resource')
    def test_node_adopt(self, mock_get):
        mock_node = node.Node.new()
        mock_get.return_value = mock_node
        self._verify("openstack.clustering.v1.node.Node.adopt",
                     self.proxy.adopt_node,
                     method_kwargs={"preview": False, "foo": "bar"},
                     expected_kwargs={"preview": False, "foo": "bar"})

        mock_get.assert_called_once_with(node.Node, None)

    @mock.patch.object(proxy_base.Proxy, '_get_resource')
    def test_node_adopt_preview(self, mock_get):
        mock_node = node.Node.new()
        mock_get.return_value = mock_node
        self._verify("openstack.clustering.v1.node.Node.adopt",
                     self.proxy.adopt_node,
                     method_kwargs={"preview": True, "foo": "bar"},
                     expected_kwargs={"preview": True, "foo": "bar"})

        mock_get.assert_called_once_with(node.Node, None)

    def test_policy_create(self):
        self.verify_create(self.proxy.create_policy, policy.Policy)

    def test_policy_validate(self):
        self.verify_create(self.proxy.validate_policy, policy.PolicyValidate)

    def test_policy_delete(self):
        self.verify_delete(self.proxy.delete_policy, policy.Policy, False)

    def test_policy_delete_ignore(self):
        self.verify_delete(self.proxy.delete_policy, policy.Policy, True)

    def test_policy_find(self):
        self.verify_find(self.proxy.find_policy, policy.Policy)

    def test_policy_get(self):
        self.verify_get(self.proxy.get_policy, policy.Policy)

    def test_policies(self):
        self.verify_list(self.proxy.policies, policy.Policy,
                         method_kwargs={'limit': 2},
                         expected_kwargs={'limit': 2})

    def test_policy_update(self):
        self.verify_update(self.proxy.update_policy, policy.Policy)

    def test_cluster_policies(self):
        self.verify_list(self.proxy.cluster_policies,
                         cluster_policy.ClusterPolicy,
                         method_args=["FAKE_CLUSTER"],
                         expected_kwargs={"cluster_id": "FAKE_CLUSTER"})

    def test_get_cluster_policy(self):
        fake_policy = cluster_policy.ClusterPolicy.new(id="FAKE_POLICY")
        fake_cluster = cluster.Cluster.new(id='FAKE_CLUSTER')

        # ClusterPolicy object as input
        self._verify2('openstack.proxy.Proxy._get',
                      self.proxy.get_cluster_policy,
                      method_args=[fake_policy, "FAKE_CLUSTER"],
                      expected_args=[cluster_policy.ClusterPolicy,
                                     fake_policy],
                      expected_kwargs={'cluster_id': 'FAKE_CLUSTER'},
                      expected_result=fake_policy)

        # Policy ID as input
        self._verify2('openstack.proxy.Proxy._get',
                      self.proxy.get_cluster_policy,
                      method_args=["FAKE_POLICY", "FAKE_CLUSTER"],
                      expected_args=[cluster_policy.ClusterPolicy,
                                     "FAKE_POLICY"],
                      expected_kwargs={"cluster_id": "FAKE_CLUSTER"})

        # Cluster object as input
        self._verify2('openstack.proxy.Proxy._get',
                      self.proxy.get_cluster_policy,
                      method_args=["FAKE_POLICY", fake_cluster],
                      expected_args=[cluster_policy.ClusterPolicy,
                                     "FAKE_POLICY"],
                      expected_kwargs={"cluster_id": fake_cluster})

    def test_receiver_create(self):
        self.verify_create(self.proxy.create_receiver, receiver.Receiver)

    def test_receiver_update(self):
        self.verify_update(self.proxy.update_receiver, receiver.Receiver)

    def test_receiver_delete(self):
        self.verify_delete(self.proxy.delete_receiver, receiver.Receiver,
                           False)

    def test_receiver_delete_ignore(self):
        self.verify_delete(self.proxy.delete_receiver, receiver.Receiver, True)

    def test_receiver_find(self):
        self.verify_find(self.proxy.find_receiver, receiver.Receiver)

    def test_receiver_get(self):
        self.verify_get(self.proxy.get_receiver, receiver.Receiver)

    def test_receivers(self):
        self.verify_list(self.proxy.receivers, receiver.Receiver,
                         method_kwargs={'limit': 2},
                         expected_kwargs={'limit': 2})

    def test_action_get(self):
        self.verify_get(self.proxy.get_action, action.Action)

    def test_actions(self):
        self.verify_list(self.proxy.actions, action.Action,
                         method_kwargs={'limit': 2},
                         expected_kwargs={'limit': 2})

    def test_event_get(self):
        self.verify_get(self.proxy.get_event, event.Event)

    def test_events(self):
        self.verify_list(self.proxy.events, event.Event,
                         method_kwargs={'limit': 2},
                         expected_kwargs={'limit': 2})

    @mock.patch("openstack.resource.wait_for_status")
    def test_wait_for(self, mock_wait):
        mock_resource = mock.Mock()
        mock_wait.return_value = mock_resource

        self.proxy.wait_for_status(mock_resource, 'ACTIVE')

        mock_wait.assert_called_once_with(self.proxy, mock_resource,
                                          'ACTIVE', [], 2, 120)

    @mock.patch("openstack.resource.wait_for_status")
    def test_wait_for_params(self, mock_wait):
        mock_resource = mock.Mock()
        mock_wait.return_value = mock_resource

        self.proxy.wait_for_status(mock_resource, 'ACTIVE', ['ERROR'], 1, 2)

        mock_wait.assert_called_once_with(self.proxy, mock_resource,
                                          'ACTIVE', ['ERROR'], 1, 2)

    @mock.patch("openstack.resource.wait_for_delete")
    def test_wait_for_delete(self, mock_wait):
        mock_resource = mock.Mock()
        mock_wait.return_value = mock_resource

        self.proxy.wait_for_delete(mock_resource)

        mock_wait.assert_called_once_with(self.proxy, mock_resource, 2, 120)

    @mock.patch("openstack.resource.wait_for_delete")
    def test_wait_for_delete_params(self, mock_wait):
        mock_resource = mock.Mock()
        mock_wait.return_value = mock_resource

        self.proxy.wait_for_delete(mock_resource, 1, 2)

        mock_wait.assert_called_once_with(self.proxy, mock_resource, 1, 2)
