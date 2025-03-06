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

from openstack.dns.v2 import _base
from openstack import exceptions
from openstack import resource


class ZoneImport(_base.Resource):
    """DNS Zone Import Resource"""

    resource_key = ''
    resources_key = 'imports'
    base_path = '/zones/tasks/import'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters('zone_id', 'message', 'status')

    #: Properties
    #: Timestamp when the zone was created
    created_at = resource.Body('created_at')
    #: Links contains a `self` pertaining to this zone or a `next` pertaining
    #: to next page
    links = resource.Body('links', type=dict)
    #: Message
    message = resource.Body('message')
    #: Returns the total_count of resources matching this filter
    metadata = resource.Body('metadata', type=list)
    #: The project id which the zone belongs to
    project_id = resource.Body('project_id')
    #: Current status of the zone import
    status = resource.Body('status')
    #: Timestamp when the zone was last updated
    updated_at = resource.Body('updated_at')
    #: Version of the resource
    version = resource.Body('version', type=int)
    #: ID for the zone that was created by this import
    zone_id = resource.Body('zone_id')

    def create(self, session, prepend_key=True, base_path=None, **kwargs):
        """Create a remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param prepend_key: A boolean indicating whether the resource_key
                            should be prepended in a resource creation
                            request. Default to True.
        :param str base_path: Base part of the URI for creating resources, if
                              different from
                              :data:`~openstack.resource.Resource.base_path`.
        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_create` is not set to ``True``.
        """
        if not self.allow_create:
            raise exceptions.MethodNotSupported(self, "create")

        session = self._get_session(session)
        microversion = self._get_microversion(session)
        # Create ZoneImport requires empty body and 'text/dns' as content-type
        # skip _prepare_request completely, since we need just empty body
        request = resource._Request(
            self.base_path, None, {'content-type': 'text/dns'}
        )
        response = session.post(
            request.url,
            json=request.body,
            headers=request.headers,
            microversion=microversion,
        )

        self.microversion = microversion
        self._translate_response(response)
        return self
