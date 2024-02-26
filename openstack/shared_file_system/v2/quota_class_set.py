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


class QuotaClassSet(resource.Resource):
    base_path = '/quota-class-sets'
    resource_key = 'quota_class_set'

    allow_create = False
    allow_fetch = True
    allow_commit = True
    allow_delete = False
    allow_list = False
    allow_head = False

    _query_mapping = resource.QueryParameters("quota_class_name", "project_id")
    #: Properties
    #: A quota_class_set id.
    id = resource.Body("id", type=str)
    #: The maximum number of share groups.
    share_groups = resource.Body("share_groups", type=int)
    #: The maximum number of share group snapshots.
    share_group_snapshots = resource.Body("share_group_snapshots", type=int)
    #: The total maximum number of shares that are allowed in a project.
    snapshots = resource.Body("snapshots", type=int)
    #: The maximum number of snapshot gigabytes that are allowed in a project.
    snapshot_gigabytes = resource.Body("snapshot_gigabytes", type=int)
    #: The total maximum number of snapshot gigabytes that are allowed in a project.
    shares = resource.Body("shares", type=int)
    #: The maximum number of share-networks that are allowed in a project.
    share_networks = resource.Body("share_networks", type=int)
    #: The maximum number of share replicas that is allowed.
    share_replicas = resource.Body("share_replicas", type=int)
    #: The total maximum number of share gigabytes that are allowed in a project.
    #: You cannot request a share that exceeds the allowed gigabytes quota.
    gigabytes = resource.Body("gigabytes", type=int)
    #: The maximum number of replica gigabytes that are allowed in a project.
    #: You cannot create a share, share replica, manage a share or extend a share
    #: if it is going to exceed the allowed replica gigabytes quota.
    replica_gigabytes = resource.Body("replica_gigabytes", type=int)
    #: The number of gigabytes per share allowed in a project.
    per_share_gigabytes = resource.Body("per_share_gigabytes", type=int)
    #: The total maximum number of share backups that are allowed in a project.
    backups = resource.Body("backups", type=int)
    #: The total maximum number of backup gigabytes that are allowed in a project.
    backup_gigabytes = resource.Body("backup_gigabytes", type=int)
