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

from openstack import resource


class Limit(resource.Resource):
    resources_key = "limits"
    base_path = "/limits"

    # capabilities
    allow_create = False
    allow_fetch = False
    allow_commit = False
    allow_delete = False
    allow_list = True
    allow_head = False

    #: Properties
    #: The maximum number of replica gigabytes that are allowed
    #: in a project.
    maxTotalReplicaGigabytes = resource.Body(
        "maxTotalReplicaGigabytes", type=int
    )
    #: The total maximum number of shares that are allowed in a project.
    maxTotalShares = resource.Body("maxTotalShares", type=int)
    #: The total maximum number of share gigabytes that are allowed in a
    #: project.
    maxTotalShareGigabytes = resource.Body("maxTotalShareGigabytes", type=int)
    #: The total maximum number of share-networks that are allowed in a
    #: project.
    maxTotalShareNetworks = resource.Body("maxTotalShareNetworks", type=int)
    #: The total maximum number of share snapshots that are allowed in a
    #: project.
    maxTotalShareSnapshots = resource.Body("maxTotalShareSnapshots", type=int)
    #: The maximum number of share replicas that is allowed.
    maxTotalShareReplicas = resource.Body("maxTotalShareReplicas", type=int)
    #: The total maximum number of snapshot gigabytes that are allowed
    #: in a project.
    maxTotalSnapshotGigabytes = resource.Body(
        "maxTotalSnapshotGigabytes", type=int
    )
    #: The total number of replica gigabytes used in a project by
    #: share replicas.
    totalReplicaGigabytesUsed = resource.Body(
        "totalReplicaGigabytesUsed", type=int
    )
    #: The total number of gigabytes used in a project by shares.
    totalShareGigabytesUsed = resource.Body(
        "totalShareGigabytesUsed", type=int
    )
    #: The total number of created shares in a project.
    totalSharesUsed = resource.Body("totalSharesUsed", type=int)
    #: The total number of created share-networks in a project.
    totalShareNetworksUsed = resource.Body("totalShareNetworksUsed", type=int)
    #: The total number of created share snapshots in a project.
    totalShareSnapshotsUsed = resource.Body(
        "totalShareSnapshotsUsed", type=int
    )
    #: The total number of gigabytes used in a project by snapshots.
    totalSnapshotGigabytesUsed = resource.Body(
        "totalSnapshotGigabytesUsed", type=int
    )
    #: The total number of created share replicas in a project.
    totalShareReplicasUsed = resource.Body("totalShareReplicasUsed", type=int)
