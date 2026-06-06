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
from openstack.common import quota_set
from openstack import resource


class QuotaSet(quota_set.QuotaSet):
    resource_key = "quota_set"
    resources_key = "quota_sets"
    base_path = "/quota-sets/%(project_id)s"

    # capabilities
    allow_create = False
    allow_list = False

    #: Properties
    #: The number of gigabytes allowed for each project.
    gigabytes = resource.Body("gigabytes", type=int)
    #: The number of snapshots allowed for each project.
    snapshots = resource.Body("snapshots", type=int)
    #: The number of shares allowed for each project.
    shares = resource.Body("shares", type=int)
    #: The number of gigabytes for the snapshots allowed for each project.
    snapshot_gigabytes = resource.Body("snapshot_gigabytes", type=int)
    #: The number of share groups allowed for each project or user.
    share_groups = resource.Body("share_groups", type=int)
    #: The number of share group snapshots allowed for each project or user.
    share_group_snapshots = resource.Body("share_group_snapshots", type=int)
    #: The number of share networks allowed for each project.
    share_networks = resource.Body("share_networks", type=int)
    #: The number of share replicas allowed for each project.
    share_replicas = resource.Body("share_replicas", type=int)
    #: The number of gigabytes for the share replicas allowed for each project.
    replica_gigabytes = resource.Body("replica_gigabytes", type=int)
    #: The number of gigabytes per share allowed for each project
    per_share_gigabytes = resource.Body("per_share_gigabytes", type=int)
    #: The number of backups allowed for each project.
    backups = resource.Body("backups", type=int)
    #: The number of gigabytes for the backups allowed for each project.
    backup_gigabytes = resource.Body("backup_gigabytes", type=int)
