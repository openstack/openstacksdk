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
    resource_key = 'quota_class_set'
    base_path = '/os-quota-class-sets'

    # Capabilities
    allow_fetch = True
    allow_commit = True

    # Properties
    #: The size (GB) of backups that are allowed for each project.
    backup_gigabytes = resource.Body('backup_gigabytes', type=int)
    #: The number of backups that are allowed for each project.
    backups = resource.Body('backups', type=int)
    #: The size (GB) of volumes and snapshots that are allowed for each
    #: project.
    gigabytes = resource.Body('gigabytes', type=int)
    #: The number of groups that are allowed for each project.
    groups = resource.Body('groups', type=int)
    #: The size (GB) of volumes in request that are allowed for each volume.
    per_volume_gigabytes = resource.Body('per_volume_gigabytes', type=int)
    #: The number of snapshots that are allowed for each project.
    snapshots = resource.Body('snapshots', type=int)
    #: The number of volumes that are allowed for each project.
    volumes = resource.Body('volumes', type=int)
