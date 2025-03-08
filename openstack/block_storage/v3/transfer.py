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
    base_path = "/volume-transfers"

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
    #: Whether to transfer snapshots or not
    no_snapshots = resource.Body("no_snapshots")

    _max_microversion = "3.55"

    def create(
        self,
        session,
        prepend_key=True,
        base_path=None,
        *,
        resource_request_key=None,
        resource_response_key=None,
        microversion=None,
        **params,
    ):
        """Create a volume transfer.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param prepend_key: A boolean indicating whether the resource_key
            should be prepended in a resource creation request. Default to
            True.
        :param str base_path: Base part of the URI for creating resources, if
            different from :data:`~openstack.resource.Resource.base_path`.
        :param str resource_request_key: Overrides the usage of
            self.resource_key when prepending a key to the request body.
            Ignored if `prepend_key` is false.
        :param str resource_response_key: Overrides the usage of
            self.resource_key when processing response bodies.
            Ignored if `prepend_key` is false.
        :param str microversion: API version to override the negotiated one.
        :param dict params: Additional params to pass.
        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
            :data:`Resource.allow_create` is not set to ``True``.
        """

        # With MV 3.55 we introduced new API for volume transfer
        # (/volume-transfers). Prior to that (MV < 3.55), we use
        # the old API (/os-volume-transfer)
        if not utils.supports_microversion(session, '3.55'):
            base_path = '/os-volume-transfer'
            # With MV 3.55, we also introduce the ability to transfer
            # snapshot along with the volume. If MV < 3.55, we should
            # not send 'no_snapshots' parameter in the request.
            if 'no_snapshots' in params:
                params.pop('no_snapshots')

        return super().create(
            session,
            prepend_key=prepend_key,
            base_path=base_path,
            resource_request_key=resource_request_key,
            resource_response_key=resource_response_key,
            microversion=microversion,
            **params,
        )

    def fetch(
        self,
        session,
        requires_id=True,
        base_path=None,
        error_message=None,
        skip_cache=False,
        *,
        resource_response_key=None,
        microversion=None,
        **params,
    ):
        """Get volume transfer.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param boolean requires_id: A boolean indicating whether resource ID
            should be part of the requested URI.
        :param str base_path: Base part of the URI for fetching resources, if
            different from :data:`~openstack.resource.Resource.base_path`.
        :param str error_message: An Error message to be returned if
            requested object does not exist.
        :param bool skip_cache: A boolean indicating whether optional API
            cache should be skipped for this invocation.
        :param str resource_response_key: Overrides the usage of
            self.resource_key when processing the response body.
        :param str microversion: API version to override the negotiated one.
        :param dict params: Additional parameters that can be consumed.
        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
            :data:`Resource.allow_fetch` is not set to ``True``.
        :raises: :exc:`~openstack.exceptions.NotFoundException` if
            the resource was not found.
        """

        if not utils.supports_microversion(session, '3.55'):
            base_path = '/os-volume-transfer'

        return super().fetch(
            session,
            requires_id=requires_id,
            base_path=base_path,
            error_message=error_message,
            skip_cache=skip_cache,
            resource_response_key=resource_response_key,
            microversion=microversion,
            **params,
        )

    def delete(
        self, session, error_message=None, *, microversion=None, **kwargs
    ):
        """Delete a volume transfer.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param str microversion: API version to override the negotiated one.
        :param dict kwargs: Parameters that will be passed to
            _prepare_request()

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
            :data:`Resource.allow_commit` is not set to ``True``.
        :raises: :exc:`~openstack.exceptions.NotFoundException` if
            the resource was not found.
        """

        if not utils.supports_microversion(session, '3.55'):
            kwargs['base_path'] = '/os-volume-transfer'
        return super().delete(
            session,
            error_message=error_message,
            microversion=microversion,
            **kwargs,
        )

    def accept(self, session, *, auth_key=None):
        """Accept a volume transfer.

        :param session: The session to use for making this request.
        :param auth_key: The authentication key for the volume transfer.

        :return: This :class:`Transfer` instance.
        """
        body = {'accept': {'auth_key': auth_key}}

        path = self.base_path
        if not utils.supports_microversion(session, '3.55'):
            path = '/os-volume-transfer'

        url = utils.urljoin(path, self.id, 'accept')
        microversion = self._get_microversion(session)
        resp = session.post(
            url,
            json=body,
            microversion=microversion,
        )
        exceptions.raise_from_response(resp)

        transfer = Transfer()
        transfer._translate_response(resp)
        return transfer
