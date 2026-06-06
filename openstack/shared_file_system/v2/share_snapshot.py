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

from typing import Any, Self

from keystoneauth1 import adapter
import requests

from openstack.common import metadata
from openstack import exceptions
from openstack import resource
from openstack import utils


class ShareSnapshot(resource.Resource, metadata.MetadataMixin):
    resource_key = "snapshot"
    resources_key = "snapshots"
    base_path = "/snapshots"

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    allow_head = False

    _query_mapping = resource.QueryParameters("snapshot_id")

    #: Properties
    #: The date and time stamp when the resource was
    #: created within the services's database.
    created_at = resource.Body("created_at")
    #: The user defined description of the resource.
    description = resource.Body("description", type=str)
    #: The user defined name of the resource.
    display_name = resource.Body("display_name", type=str)
    #: The user defined description of the resource
    display_description = resource.Body("display_description", type=str)
    #: ID of the project that the snapshot belongs to.
    project_id = resource.Body("project_id", type=str)
    #: The UUID of the source share that was used to
    #: create the snapshot.
    share_id = resource.Body("share_id", type=str)
    #: The file system protocol of a share snapshot
    share_proto = resource.Body("share_proto", type=str)
    #: The snapshot's source share's size, in GiBs.
    share_size = resource.Body("share_size", type=int)
    #: The snapshot size, in GiBs.
    size = resource.Body("size", type=int)
    #: The snapshot status
    status = resource.Body("status", type=str)
    #: ID of the user that the snapshot was created by.
    user_id = resource.Body("user_id", type=str)

    def _action(
        self,
        session: adapter.Adapter,
        body: dict[str, Any],
        microversion: str | None = None,
    ) -> requests.Response:
        url = utils.urljoin(self.base_path, self.id, 'action')
        headers = {'Accept': ''}

        if microversion is None:
            microversion = self._get_microversion(session)

        response = session.post(
            url, json=body, headers=headers, microversion=microversion
        )

        exceptions.raise_from_response(response)
        return response

    def reset_status(self, session: adapter.Adapter, status: str) -> None:
        """Reset the snapshot to the given status.

        :param status: The status of the share to reset to.
        :returns: ``None``
        """
        body = {'reset_status': {'status': status}}
        self._action(session, body)

    def force_delete(self, session: adapter.Adapter) -> None:
        """Force delete the snapshot.

        :returns: ``None``
        """
        body = {'force_delete': None}
        self._action(session, body)

    def manage(
        self,
        session: adapter.Adapter,
        share_id: str,
        provider_location: str,
        **params: Any,
    ) -> Self:
        """Manage a share snapshot.

        :param session: A session object used for sending request.
        :param share_id: The UUID of the share that has snapshot which
            should be managed.
        :param provider_location: Provider location of the snapshot on the
            backend.
        :param params: Optional parameters to be sent. Available
            parameters include:

            * name: The user defined name of the resource.
            * display_name: The user defined name of the resource. This field
              sets the name parameter.
            * description: The user defined description of the resource.
            * display_description: The user defined description of the
              resource. This field sets the description parameter.
            * driver_options: A set of one or more key and value pairs, as a
              dictionary of strings, that describe driver options.

        :returns: The share snapshot that was managed.
        """
        attrs = {
            'snapshot': {
                'share_id': share_id,
                'provider_location': provider_location,
            }
        }
        attrs['snapshot'].update(params)

        url = utils.urljoin(self.base_path, 'manage')
        resp = session.post(url, json=attrs)
        self._translate_response(resp)
        return self

    def unmanage(self, session: adapter.Adapter) -> None:
        """Unmanage a share snapshot.

        :param session: A session object used for sending request.
        :returns: ``None``
        """
        body = {'unmanage': None}
        self._action(session, body)
