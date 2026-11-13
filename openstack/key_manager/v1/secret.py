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

from typing import Self

from keystoneauth1 import adapter

from openstack import exceptions
from openstack.key_manager.v1 import _format
from openstack.key_manager.v1 import _microversion
from openstack import resource
from openstack import utils


class Secret(resource.Resource):
    resources_key = 'secrets'
    base_path = '/secrets'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    # secret_store_id / secret_store_ref on secret GET/list, and
    # PUT .../secrets/{id}/secret-store/{store_id}, were introduced in 1.3
    _max_microversion = '1.3'

    @classmethod
    def _get_microversion(cls, session: adapter.Adapter) -> str | None:
        # Barbican's unversioned discovery has no min/max; use the probe.
        return _microversion.get_microversion(session, cls._max_microversion)

    _query_mapping = resource.QueryParameters(
        "name",
        "mode",
        "bits",
        "secret_type",
        "acl_only",
        "created",
        "updated",
        "expiration",
        "sort",
        algorithm="alg",
    )

    # Properties
    #: Metadata provided by a user or system for informational purposes
    algorithm = resource.Body('algorithm')
    #: Metadata provided by a user or system for informational purposes.
    #: Value must be greater than zero.
    bit_length = resource.Body('bit_length')
    #: Consumers registered for this secret, as a list of dictionaries with
    #: ``service``, ``resource_type``, and ``resource_id`` keys.
    #: Available in API microversion 1.1 and later.
    consumers = resource.Body('consumers', type=list)
    #: A list of content types
    content_types = resource.Body('content_types', type=dict)
    #: Once this timestamp has past, the secret will no longer be available.
    expires_at = resource.Body('expiration')
    #: Timestamp of when the secret was created.
    created_at = resource.Body('created')
    #: Timestamp of when the secret was last updated.
    updated_at = resource.Body('updated')
    #: The type/mode of the algorithm associated with the secret information.
    mode = resource.Body('mode')
    #: The name of the secret set by the user
    name = resource.Body('name')
    #: A URI to the sercret
    secret_ref = resource.Body('secret_ref')
    #: Computed UUID of the secret store currently holding the payload
    #: (microversion 1.3+; JSON null when N/A)
    secret_store_id = resource.Body('secret_store_id')
    #: Computed HREF of the secret store currently holding the payload
    #: (microversion 1.3+; JSON null when N/A)
    secret_store_ref = resource.Body('secret_store_ref')
    #: The ID of the secret
    # NOTE: This is not really how alternate IDs are supposed to work and
    # ultimately means this has to work differently than all other services
    # in all of OpenStack because of the departure from using actual IDs
    # that even this service can't even use itself.
    secret_id = resource.Body(
        'secret_ref', alternate_id=True, type=_format.HREFToUUID
    )
    #: Used to indicate the type of secret being stored.
    secret_type = resource.Body('secret_type')
    #: The status of this secret
    status = resource.Body('status')
    #: A timestamp when this secret was updated.
    updated_at = resource.Body('updated')
    #: The secret's data to be stored. payload_content_type must also
    #: be supplied if payload is included. (optional)
    payload = resource.Body('payload')
    #: The media type for the content of the payload.
    #: (required if payload is included)
    payload_content_type = resource.Body('payload_content_type')
    #: The encoding used for the payload to be able to include it in
    #: the JSON request. Currently only base64 is supported.
    #: (required if payload is encoded)
    payload_content_encoding = resource.Body('payload_content_encoding')

    def fetch_payload(
        self,
        session: adapter.Adapter,
        *,
        microversion: str | None = None,
    ) -> Self:
        """Fetch the secret's payload.

        Uses ``payload_content_type`` if set, otherwise the default from
        ``content_types``. If neither is available, no request is made.
        Fetch the secret's metadata first to populate ``content_types``.

        :param session: The session to use for making this request.
        :param microversion: API microversion to use. Defaults to the
            negotiated microversion for this resource.
        :returns: The secret with its payload populated. Text/plain payloads
            are decoded as UTF-8; other payloads are returned as bytes.
        """
        content_type = self.payload_content_type
        if content_type is None and self.content_types:
            content_type = self.content_types.get('default')
        if content_type is None:
            return self

        # The alternate resource ID is a full reference, not a UUID.
        url = utils.urljoin(
            self.base_path, self.secret_id or self.id, 'payload'
        )
        if microversion is None:
            microversion = self._get_microversion(session)
        response = session.get(
            url,
            headers={"Accept": content_type},
            microversion=microversion,
        )
        exceptions.raise_from_response(response)
        # Do not use response.text: automatic encoding detection could corrupt
        # the payload. Text payloads use UTF-8, matching barbicanclient.
        payload = response.content
        if content_type == "text/plain":
            payload = payload.decode("UTF-8")
        self._update_from_body_attrs({'payload': payload})
        return self

    def migrate_store(
        self,
        session: adapter.Adapter,
        secret_store_id: str,
        *,
        microversion: str | None = None,
    ) -> None:
        """Migrate this secret onto another secret store.

        Requires key-manager microversion 1.3. Prefer
        :meth:`~openstack.key_manager.v1._proxy.Proxy.migrate_secret_store`
        which enforces that and accepts UUID/URI/``SecretStore``.

        :param session: The session to use for making this request.
        :param secret_store_id: Destination store UUID (or trailing path
            segment of a ``…/secret-stores/<uuid>`` URI).
        :param microversion: API microversion to use. Defaults to the
            negotiated microversion for this resource.
        :returns: None
        """
        if microversion is None:
            microversion = self._get_microversion(session)
        url = utils.urljoin(
            self.base_path, self.id, 'secret-store', secret_store_id
        )
        session.put(url, microversion=microversion)
