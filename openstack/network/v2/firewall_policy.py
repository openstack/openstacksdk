# Copyright (c) 2018 China Telecom Corporation
# All Rights Reserved.
#
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
from openstack.exceptions import HttpException

from openstack import resource
from openstack import utils


class FirewallPolicy(resource.Resource):
    resource_key = 'firewall_policy'
    resources_key = 'firewall_policies'
    base_path = '/fwaas/firewall_policies'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'description', 'firewall_rules', 'name', 'project_id', 'shared')

    # Properties
    #: Each time that the firewall policy or its associated rules are changed,
    #: the API sets this attribute to false. To audit the policy,
    #: explicitly set this attribute to true.
    audited = resource.Body('audited')
    #: The firewall group rule description.
    description = resource.Body('description')
    #: The ID of the firewall policy.
    id = resource.Body('id')
    #: A list of the IDs of the firewall rules associated with the
    #: firewall policy.
    firewall_rules = resource.Body('firewall_rules')
    #: The name of a firewall policy
    name = resource.Body('name')
    #: The ID of the project that owns the resource.
    project_id = resource.Body('project_id')
    #: Set to true to make this firewall policy visible to other projects.
    shared = resource.Body('shared')

    def insert_rule(self, session, **body):
        """Insert a firewall_rule into a firewall_policy in order.

        :param session: The session to communicate through.
        :type session: :class:`~openstack.session.Session`
        :param dict body: The body requested to be updated on the router

        :returns: The updated firewall policy
        :rtype: :class:`~openstack.network.v2.firewall_policy.FirewallPolicy`

        :raises: :class:`~openstack.exceptions.HttpException` on error.
        """
        url = utils.urljoin(self.base_path, self.id, 'insert_rule')
        return self._put_request(session, url, body)

    def remove_rule(self, session, **body):
        """Remove a firewall_rule from a firewall_policy.

        :param session: The session to communicate through.
        :type session: :class:`~openstack.session.Session`
        :param dict body: The body requested to be updated on the router

        :returns: The updated firewall policy
        :rtype: :class:`~openstack.network.v2.firewall_policy.FirewallPolicy`

        :raises: :class:`~openstack.exceptions.HttpException` on error.
        """
        url = utils.urljoin(self.base_path, self.id, 'remove_rule')
        return self._put_request(session, url, body)

    def _put_request(self, session, url, json_data):
        resp = session.put(url, json=json_data)
        data = resp.json()
        if not resp.ok:
            message = None
            if 'NeutronError' in data:
                message = data['NeutronError']['message']
            raise HttpException(message=message, response=resp)

        self._body.attributes.update(data)
        self._update_location()
        return self
