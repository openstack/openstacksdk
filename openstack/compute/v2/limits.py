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
from openstack import resource2


class AbsoluteLimits(resource2.Resource):

    #: The number of key-value pairs that can be set as image metadata.
    image_meta = resource2.Body("maxImageMeta")
    #: The maximum number of personality contents that can be supplied.
    personality = resource2.Body("maxPersonality")
    #: The maximum size, in bytes, of a personality.
    personality_size = resource2.Body("maxPersonalitySize")
    #: The maximum amount of security group rules allowed.
    security_group_rules = resource2.Body("maxSecurityGroupRules")
    #: The maximum amount of security groups allowed.
    security_groups = resource2.Body("maxSecurityGroups")
    #: The amount of security groups currently in use.
    security_groups_used = resource2.Body("totalSecurityGroupsUsed")
    #: The number of key-value pairs that can be set as sever metadata.
    server_meta = resource2.Body("maxServerMeta")
    #: The maximum amount of cores.
    total_cores = resource2.Body("maxTotalCores")
    #: The amount of cores currently in use.
    total_cores_used = resource2.Body("totalCoresUsed")
    #: The maximum amount of floating IPs.
    floating_ips = resource2.Body("maxTotalFloatingIps")
    #: The amount of floating IPs currently in use.
    floating_ips_used = resource2.Body("totalFloatingIpsUsed")
    #: The maximum amount of instances.
    instances = resource2.Body("maxTotalInstances")
    #: The amount of instances currently in use.
    instances_used = resource2.Body("totalInstancesUsed")
    #: The maximum amount of keypairs.
    keypairs = resource2.Body("maxTotalKeypairs")
    #: The maximum RAM size in megabytes.
    total_ram = resource2.Body("maxTotalRAMSize")
    #: The RAM size in megabytes currently in use.
    total_ram_used = resource2.Body("totalRAMUsed")
    #: The maximum amount of server groups.
    server_groups = resource2.Body("maxServerGroups")
    #: The amount of server groups currently in use.
    server_groups_used = resource2.Body("totalServerGroupsUsed")
    #: The maximum number of members in a server group.
    server_group_members = resource2.Body("maxServerGroupMembers")


class RateLimit(resource2.Resource):

    #: A list of the specific limits that apply to the ``regex`` and ``uri``.
    limits = resource2.Body("limit", type=list)
    #: A regex representing which routes this rate limit applies to.
    regex = resource2.Body("regex")
    #: A URI representing which routes this rate limit applies to.
    uri = resource2.Body("uri")


class Limits(resource2.Resource):
    base_path = "/limits"
    resource_key = "limits"
    service = compute_service.ComputeService()

    allow_get = True

    absolute = resource2.Body("absolute", type=AbsoluteLimits)
    rate = resource2.Body("rate", type=list)

    def get(self, session, requires_id=False):
        """Get the Limits resource.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`

        :returns: A Limits instance
        :rtype: :class:`~openstack.compute.v2.limits.Limits`
        """
        request = self._prepare_request(requires_id=False, prepend_key=False)

        response = session.get(request.uri, endpoint_filter=self.service)

        body = response.json()
        body = body[self.resource_key]

        absolute_body = self._filter_component(
            body["absolute"], AbsoluteLimits._body_mapping())
        self.absolute = AbsoluteLimits.existing(**absolute_body)

        rates_body = body["rate"]

        rates = []
        for rate_body in rates_body:
            rate_body = self._filter_component(rate_body,
                                               RateLimit._body_mapping())
            rates.append(RateLimit(**rate_body))

        self.rate = rates

        return self
