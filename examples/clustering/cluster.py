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
Managing policies in the Cluster service.

For a full guide see
https://developer.openstack.org/sdks/python/openstacksdk/user/guides/cluster.html
"""

CLUSTER_NAME = "Test_Cluster"
CLUSTER_ID = "47d808e5-ce75-4a1e-bfd2-4ed4639e8640"
PROFILE_ID = "b0e3a680-e270-4eb8-9361-e5c9503fba0a"
NODE_ID = "dd803d4a-015d-4223-b15f-db29bad3146c"
POLICY_ID = "c0e3a680-e270-4eb8-9361-e5c9503fba00"


def list_cluster(conn):
    print("List clusters:")

    for cluster in conn.clustering.clusters():
        print(cluster.to_dict())

    for cluster in conn.clustering.clusters(sort='name:asc'):
        print(cluster.to_dict())


def create_cluster(conn):
    print("Create cluster:")

    spec = {
        "name": CLUSTER_NAME,
        "profile_id": PROFILE_ID,
        "min_size": 0,
        "max_size": -1,
        "desired_capacity": 1,
    }

    cluster = conn.clustering.create_cluster(**spec)
    print(cluster.to_dict())


def get_cluster(conn):
    print("Get cluster:")

    cluster = conn.clustering.get_cluster(CLUSTER_ID)
    print(cluster.to_dict())


def find_cluster(conn):
    print("Find cluster:")

    cluster = conn.clustering.find_cluster(CLUSTER_ID)
    print(cluster.to_dict())


def update_cluster(conn):
    print("Update cluster:")

    spec = {
        "name": "Test_Cluster001",
        "profile_id": "c0e3a680-e270-4eb8-9361-e5c9503fba0a",
        "profile_only": True,
    }
    cluster = conn.clustering.update_cluster(CLUSTER_ID, **spec)
    print(cluster.to_dict())


def delete_cluster(conn):
    print("Delete cluster:")

    conn.clustering.delete_cluster(CLUSTER_ID)
    print("Cluster deleted.")

    # cluster support force delete
    conn.clustering.delete_cluster(CLUSTER_ID, False, True)
    print("Cluster deleted")


def cluster_add_nodes(conn):
    print("Add nodes to cluster:")

    node_ids = [NODE_ID]
    res = conn.clustering.cluster_add_nodes(CLUSTER_ID, node_ids)
    print(res.to_dict())


def cluster_del_nodes(conn):
    print("Remove nodes from a cluster:")

    node_ids = [NODE_ID]
    res = conn.clustering.cluster_del_nodes(CLUSTER_ID, node_ids)
    print(res.to_dict())


def cluster_replace_nodes(conn):
    print("Replace the nodes in a cluster with specified nodes:")

    old_node = NODE_ID
    new_node = "cd803d4a-015d-4223-b15f-db29bad3146c"
    spec = {
        old_node: new_node
    }
    res = conn.clustering.cluster_replace_nodes(CLUSTER_ID, **spec)
    print(res.to_dict())


def cluster_scale_out(conn):
    print("Inflate the size of a cluster:")

    res = conn.clustering.cluster_scale_out(CLUSTER_ID, 1)
    print(res.to_dict())


def cluster_scale_in(conn):
    print("Shrink the size of a cluster:")

    res = conn.clustering.cluster_scale_in(CLUSTER_ID, 1)
    print(res.to_dict())


def cluster_resize(conn):
    print("Resize of cluster:")

    spec = {
        'min_size': 1,
        'max_size': 6,
        'adjustment_type': 'EXACT_CAPACITY',
        'number': 2
    }
    res = conn.clustering.cluster_resize(CLUSTER_ID, **spec)
    print(res.to_dict())


def cluster_attach_policy(conn):
    print("Attach policy to a cluster:")

    spec = {'enabled': True}
    res = conn.clustering.cluster_attach_policy(CLUSTER_ID, POLICY_ID,
                                                **spec)
    print(res.to_dict())


def cluster_detach_policy(conn):
    print("Detach a policy from a cluster:")

    res = conn.clustering.cluster_detach_policy(CLUSTER_ID, POLICY_ID)
    print(res.to_dict())


def check_cluster(conn):
    print("Check cluster:")

    res = conn.clustering.check_cluster(CLUSTER_ID)
    print(res.to_dict())


def recover_cluster(conn):
    print("Recover cluster:")

    spec = {'check': True}
    res = conn.clustering.recover_cluster(CLUSTER_ID, **spec)
    print(res.to_dict())
