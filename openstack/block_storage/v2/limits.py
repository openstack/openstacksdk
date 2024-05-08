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


class AbsoluteLimit(resource.Resource):
    #: Properties
    #: The maximum total amount of backups, in gibibytes (GiB).
    max_total_backup_gigabytes = resource.Body(
        "maxTotalBackupGigabytes", type=int
    )
    #: The maximum number of backups.
    max_total_backups = resource.Body("maxTotalBackups", type=int)
    #: The maximum number of snapshots.
    max_total_snapshots = resource.Body("maxTotalSnapshots", type=int)
    #: The maximum total amount of volumes, in gibibytes (GiB).
    max_total_volume_gigabytes = resource.Body(
        "maxTotalVolumeGigabytes", type=int
    )
    #: The maximum number of volumes.
    max_total_volumes = resource.Body("maxTotalVolumes", type=int)
    #: The total number of backups gibibytes (GiB) used.
    total_backup_gigabytes_used = resource.Body(
        "totalBackupGigabytesUsed", type=int
    )
    #: The total number of backups used.
    total_backups_used = resource.Body("totalBackupsUsed", type=int)
    #: The total number of gibibytes (GiB) used.
    total_gigabytes_used = resource.Body("totalGigabytesUsed", type=int)
    #: The total number of snapshots used.
    total_snapshots_used = resource.Body("totalSnapshotsUsed", type=int)
    #: The total number of volumes used.
    total_volumes_used = resource.Body("totalVolumesUsed", type=int)


class RateLimit(resource.Resource):
    #: Properties
    #: Rate limits next availabe time.
    next_available = resource.Body("next-available")
    #: Integer for rate limits remaining.
    remaining = resource.Body("remaining", type=int)
    #: Unit of measurement for the value parameter.
    unit = resource.Body("unit")
    #: Integer number of requests which can be made.
    value = resource.Body("value", type=int)
    #: An HTTP verb (POST, PUT, etc.).
    verb = resource.Body("verb")


class RateLimits(resource.Resource):
    #: Properties
    #: A list of the specific limits that apply to the ``regex`` and ``uri``.
    limits = resource.Body("limit", type=list, list_type=RateLimit)
    #: A regex representing which routes this rate limit applies to.
    regex = resource.Body("regex")
    #: A URI representing which routes this rate limit applies to.
    uri = resource.Body("uri")


class Limits(resource.Resource):
    resource_key = "limits"
    base_path = "/limits"

    # capabilities
    allow_fetch = True

    #: Properties
    #: An absolute limits object.
    absolute = resource.Body("absolute", type=AbsoluteLimit)
    #: Rate-limit volume copy bandwidth, used to mitigate
    #: slow down of data access from the instances.
    rate = resource.Body("rate", type=list, list_type=RateLimits)


# legacy alias
Limit = Limits
