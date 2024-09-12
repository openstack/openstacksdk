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


class AbsoluteLimits(resource.Resource):
    _max_microversion = '2.57'

    # Properties
    #: The number of key-value pairs that can be set as image metadata.
    image_meta = resource.Body("maxImageMeta", aka="max_image_meta")
    #: The maximum number of personality contents that can be supplied.
    personality = resource.Body("maxPersonality", deprecated=True)
    #: The maximum size, in bytes, of a personality.
    personality_size = resource.Body("maxPersonalitySize", deprecated=True)
    #: The maximum amount of security group rules allowed.
    security_group_rules = resource.Body(
        "maxSecurityGroupRules", aka="max_security_group_rules"
    )
    #: The maximum amount of security groups allowed.
    security_groups = resource.Body(
        "maxSecurityGroups", aka="max_security_groups"
    )
    #: The amount of security groups currently in use.
    security_groups_used = resource.Body(
        "totalSecurityGroupsUsed", aka="total_security_groups_used"
    )
    #: The number of key-value pairs that can be set as server metadata.
    server_meta = resource.Body("maxServerMeta", aka="max_server_meta")
    #: The maximum amount of cores.
    total_cores = resource.Body("maxTotalCores", aka="max_total_cores")
    #: The amount of cores currently in use.
    total_cores_used = resource.Body("totalCoresUsed", aka="total_cores_used")
    #: The maximum amount of floating IPs.
    floating_ips = resource.Body(
        "maxTotalFloatingIps", aka="max_total_floating_ips"
    )
    #: The amount of floating IPs currently in use.
    floating_ips_used = resource.Body(
        "totalFloatingIpsUsed", aka="total_floating_ips_used"
    )
    #: The maximum amount of instances.
    instances = resource.Body("maxTotalInstances", aka="max_total_instances")
    #: The amount of instances currently in use.
    instances_used = resource.Body(
        "totalInstancesUsed", aka="total_instances_used"
    )
    #: The maximum amount of keypairs.
    keypairs = resource.Body("maxTotalKeypairs", aka="max_total_keypairs")
    #: The maximum RAM size in megabytes.
    total_ram = resource.Body("maxTotalRAMSize", aka="max_total_ram_size")
    #: The RAM size in megabytes currently in use.
    total_ram_used = resource.Body("totalRAMUsed", aka="total_ram_used")
    #: The maximum amount of server groups.
    server_groups = resource.Body("maxServerGroups", aka="max_server_groups")
    #: The amount of server groups currently in use.
    server_groups_used = resource.Body(
        "totalServerGroupsUsed", aka="total_server_groups_used"
    )
    #: The maximum number of members in a server group.
    server_group_members = resource.Body(
        "maxServerGroupMembers", aka="max_server_group_members"
    )


class RateLimit(resource.Resource):
    # Properties
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
    # Properties
    #: A list of the specific limits that apply to the ``regex`` and ``uri``.
    limits = resource.Body("limit", type=list, list_type=RateLimit)
    #: A regex representing which routes this rate limit applies to.
    regex = resource.Body("regex")
    #: A URI representing which routes this rate limit applies to.
    uri = resource.Body("uri")


class Limits(resource.Resource):
    base_path = "/limits"
    resource_key = "limits"

    allow_fetch = True

    _query_mapping = resource.QueryParameters(
        'tenant_id',
        'reserved',
        project_id='tenant_id',
    )

    # Properties
    #: An absolute limits object.
    absolute = resource.Body("absolute", type=AbsoluteLimits)
    #: Rate-limit compute resources. This is only populated when using the
    #: legacy v2 API which was removed in Nova 14.0.0 (Newton). In v2.1 it will
    #: always be an empty list.
    rate = resource.Body("rate", type=list, list_type=RateLimits)

    def fetch(
        self,
        session,
        requires_id=False,
        base_path=None,
        error_message=None,
        skip_cache=False,
        **params,
    ):
        """Get the Limits resource.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`

        :returns: A Limits instance
        :rtype: :class:`~openstack.compute.v2.limits.Limits`
        """
        # TODO(mordred) We shouldn't have to subclass just to declare
        # requires_id = False.
        return super().fetch(
            session,
            requires_id,
            error_message,
            base_path,
            skip_cache,
            **params,
        )
