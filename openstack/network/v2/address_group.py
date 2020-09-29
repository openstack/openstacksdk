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

from openstack import exceptions
from openstack import resource
from openstack import utils


class AddressGroup(resource.Resource):
    """Address group extension."""
    resource_key = 'address_group'
    resources_key = 'address_groups'
    base_path = '/address-groups'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        "sort_key", "sort_dir",
        'name', 'description',
        project_id='tenant_id'
    )

    # Properties
    #: The ID of the address group.
    id = resource.Body('id')
    #: The address group name.
    name = resource.Body('name')
    #: The address group name.
    description = resource.Body('description')
    #: The ID of the project that owns the address group.
    project_id = resource.Body('tenant_id')
    #: The IP addresses of the address group.
    addresses = resource.Body('addresses', type=list)

    def _put(self, session, url, body):
        resp = session.put(url, json=body)
        exceptions.raise_from_response(resp)
        return resp

    def add_addresses(self, session, addresses):
        """Add addresses into the address group.

        :param session: The session to communicate through.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param list addresses: The list of address strings.

        :returns: The response as a AddressGroup object with updated addresses

        :raises: :class:`~openstack.exceptions.SDKException` on error.
        """
        url = utils.urljoin(self.base_path, self.id, 'add_addresses')
        resp = self._put(session, url, {'addresses': addresses})
        self._translate_response(resp)
        return self

    def remove_addresses(self, session, addresses):
        """Remove addresses from the address group.

        :param session: The session to communicate through.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param list addresses: The list of address strings.

        :returns: The response as a AddressGroup object with updated addresses

        :raises: :class:`~openstack.exceptions.SDKException` on error.
        """
        url = utils.urljoin(self.base_path, self.id, 'remove_addresses')
        resp = self._put(session, url, {'addresses': addresses})
        self._translate_response(resp)
        return self
