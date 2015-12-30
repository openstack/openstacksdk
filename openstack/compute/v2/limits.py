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

from openstack.compute import compute_service
from openstack import resource


class AbsoluteLimits(resource.Resource):

    #: The number of key-value pairs that can be set as image metadata.
    image_meta = resource.prop("maxImageMeta")
    #: The maximum number of personality contents that can be supplied.
    personality = resource.prop("maxPersonality")
    #: The maximum size, in bytes, of a personality.
    personality_size = resource.prop("maxPersonalitySize")
    #: The maximum amount of security group rules allowed.
    security_group_rules = resource.prop("maxSecurityGroupRules")
    #: The maximum amount of security groups allowed.
    security_groups = resource.prop("maxSecurityGroups")
    #: The amount of security groups currently in use.
    security_groups_used = resource.prop("totalSecurityGroupsUsed")
    #: The number of key-value pairs that can be set as sever metadata.
    server_meta = resource.prop("maxServerMeta")
    #: The maximum amount of cores.
    total_cores = resource.prop("maxTotalCores")
    #: The amount of cores currently in use.
    total_cores_used = resource.prop("totalCoresUsed")
    #: The maximum amount of floating IPs.
    floating_ips = resource.prop("maxTotalFloatingIps")
    #: The amount of floating IPs currently in use.
    floating_ips_used = resource.prop("totalFloatingIpsUsed")
    #: The maximum amount of instances.
    instances = resource.prop("maxTotalInstances")
    #: The amount of instances currently in use.
    instances_used = resource.prop("totalInstancesUsed")
    #: The maximum amount of keypairs.
    keypairs = resource.prop("maxTotalKeypairs")
    #: The maximum RAM size in megabytes.
    total_ram = resource.prop("maxTotalRAMSize")
    #: The RAM size in megabytes currently in use.
    total_ram_used = resource.prop("totalRAMUsed")
    #: The maximum amount of server groups.
    server_groups = resource.prop("maxServerGroups")
    #: The amount of server groups currently in use.
    server_groups_used = resource.prop("totalServerGroupsUsed")
    #: The maximum number of members in a server group.
    server_group_members = resource.prop("maxServerGroupMembers")


class RateLimits(resource.Resource):

    #: A list of the specific limits that apply to the ``regex`` and ``uri``.
    limits = resource.prop("limit", type=list)
    #: A regex representing which routes this rate limit applies to.
    regex = resource.prop("regex")
    #: A URI representing which routes this rate limit applies to.
    uri = resource.prop("uri")


class Limits(resource.Resource):
    base_path = "/limits"
    resource_key = "limits"
    service = compute_service.ComputeService()

    allow_retrieve = True

    absolute = resource.prop("absolute", type=AbsoluteLimits)
    rate = resource.prop("rate", type=list)

    def get(self, session, args=None, include_headers=False):
        """Get the Limits resource.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param dict args: An optional dict that will be translated into query
            strings for retrieving the object when specified.

        :returns: A Limits instance
        :rtype: :class:`~openstack.compute.v2.limits.Limits`
        """
        body = self.get_data_by_id(session, self.id,
                                   include_headers=include_headers)

        # Split the rates away from absolute limits. We can create
        # the `absolute` property and AbsoluteLimits resource directly
        # from the body. We have to iterate through the list inside `rate`
        # in order to create the RateLimits instances for the `rate` property.
        rate_body = body.pop("rate")
        self._attrs.update(body)

        rates = []
        for rate in rate_body:
            rates.append(RateLimits(rate))

        self._attrs.update({"rate": rates})
        self._loaded = True
        return self
