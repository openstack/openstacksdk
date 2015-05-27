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

from openstack.object_store import object_store_service
from openstack import resource


class BaseResource(resource.Resource):
    service = object_store_service.ObjectStoreService()

    @classmethod
    def update_by_id(cls, session, resource_id, attrs, path_args=None):
        """Update a Resource with the given attributes.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param resource_id: This resource's identifier, if needed by
                            the request. The default is ``None``.
        :param dict attrs: The attributes to be sent in the body
                           of the request.
        :param dict path_args: This parameter is sent by the base
                               class but is ignored for this method.

        :return: A ``dict`` representing the response headers.
        """
        url = cls._get_url(None, resource_id)
        headers = attrs.get(resource.HEADERS, dict())
        headers['Accept'] = ''
        return session.post(url, endpoint_filter=cls.service,
                            headers=headers).headers
