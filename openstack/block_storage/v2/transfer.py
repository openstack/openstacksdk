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


class Transfer(resource.Resource):
    resource_key = "transfer"
    resources_key = "transfers"
    base_path = "/os-volume-transfer"

    # capabilities
    allow_create = True
    allow_delete = True
    allow_fetch = True
    allow_list = True

    # Properties
    #: UUID of the transfer.
    id = resource.Body("id")
    #: The date and time when the resource was created.
    created_at = resource.Body("created_at")
    #: Name of the volume to transfer.
    name = resource.Body("name")
    #: ID of the volume to transfer.
    volume_id = resource.Body("volume_id")
    #: Auth key for the transfer.
    auth_key = resource.Body("auth_key")
    #: A list of links associated with this volume. *Type: list*
    links = resource.Body("links")

    def accept(self, session, *, auth_key=None):
        """Accept a volume transfer.

        :param session: The session to use for making this request.
        :param auth_key: The authentication key for the volume transfer.

        :return: This :class:`Transfer` instance.
        """
        body = {'accept': {'auth_key': auth_key}}

        url = utils.urljoin(self.base_path, self.id, 'accept')
        resp = session.post(url, json=body)
        exceptions.raise_from_response(resp)

        transfer = Transfer()
        transfer._translate_response(resp)
        return transfer
