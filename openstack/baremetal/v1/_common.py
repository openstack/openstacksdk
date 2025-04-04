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

from openstack import fields
from openstack import resource


RETRIABLE_STATUS_CODES = [
    # HTTP Conflict - happens if a node is locked
    409,
    # HTTP Service Unavailable happens if there's no free conductor
    503,
]
"""HTTP status codes that should be retried."""


PROVISIONING_VERSIONS = {
    'abort': 13,
    'adopt': 17,
    'clean': 15,
    'inspect': 6,
    'manage': 4,
    'provide': 4,
    'rescue': 38,
    'unrescue': 38,
    'unhold': 85,
    'service': 87,
}
"""API microversions introducing provisioning verbs."""


# Based on https://docs.openstack.org/ironic/latest/contributor/states.html
EXPECTED_STATES = {
    'active': 'active',
    'adopt': 'available',
    'clean': 'manageable',
    'deleted': 'available',
    'inspect': 'manageable',
    'manage': 'manageable',
    'provide': 'available',
    'rebuild': 'active',
    'rescue': 'rescue',
}
"""Mapping of provisioning actions to expected stable states."""

EXPECTED_POWER_STATES = {
    'power on': 'power on',
    'power off': 'power off',
    'rebooting': 'power on',
    'soft power off': 'power off',
    'soft rebooting': 'power on',
}
"""Mapping of target power states to expected power states."""

STATE_VERSIONS = {
    'available': '1.1',
    'enroll': '1.11',
    'manageable': '1.4',
}
"""API versions when certain states were introduced."""

VIF_VERSION = '1.28'
"""API version in which the VIF operations were introduced."""

VIF_OPTIONAL_PARAMS_VERSION = '1.67'
"""API version in which the VIF optional parameters were introduced."""

INJECT_NMI_VERSION = '1.29'
"""API vresion in which support for injecting NMI was introduced."""

CONFIG_DRIVE_REBUILD_VERSION = '1.35'
"""API version in which rebuild accepts a configdrive."""

RESET_INTERFACES_VERSION = '1.45'
"""API version in which the reset_interfaces parameter was introduced."""

CONFIG_DRIVE_DICT_VERSION = '1.56'
"""API version in which configdrive can be a dictionary."""

DEPLOY_STEPS_VERSION = '1.69'
"""API version in which deploy_steps was added to node provisioning."""

CHANGE_BOOT_MODE_VERSION = '1.76'
"""API version in which boot_mode and secure_boot states can be changed"""

FIRMWARE_VERSION = '1.86'
"""API version in which firmware components of a node can be accessed"""

VMEDIA_VERSION = '1.89'
"""API version in which the virtual media operations were introduced."""

RUNBOOKS_VERSION = '1.92'
"""API version in which a runbook can be used in place of arbitrary steps
for provisioning"""


class Resource(resource.Resource):
    """A subclass for resources that use the path to request a detailed view.

    Two patterns exist for fetching the detailed view when listing resources.

    - As part of the path. For example:

        GET /v1/ports/detail

    - As a query parameter. For example:

        GET /v1/conductors?detail=True

    This handles resources that use the former pattern, namely:

    - chassis
    - nodes
    - ports
    - portgroups
    """

    base_path: str

    @classmethod
    def list(
        cls,
        session,
        paginated=True,
        base_path=None,
        allow_unknown_params=False,
        *,
        microversion=None,
        details=False,
        **params,
    ):
        """This method is a generator which yields resource objects.

        This resource object list generator handles pagination and takes query
        params for response filtering.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param bool paginated: ``True`` if a GET to this resource returns
            a paginated series of responses, or ``False`` if a GET returns only
            one page of data. **When paginated is False only one page of data
            will be returned regardless of the API's support of pagination.**
        :param str base_path: Base part of the URI for listing resources, if
            different from :data:`~openstack.resource.Resource.base_path`.
        :param bool allow_unknown_params: ``True`` to accept, but discard
            unknown query parameters. This allows getting list of 'filters' and
            passing everything known to the server. ``False`` will result in
            validation exception when unknown query parameters are passed.
        :param str microversion: API version to override the negotiated one.
        :param bool details: Whether to return detailed resource records.
        :param dict params: These keyword arguments are passed through the
            :meth:`~openstack.resource.QueryParamter._transpose` method
            to find if any of them match expected query parameters to be sent
            in the *params* argument to
            :meth:`~keystoneauth1.adapter.Adapter.get`. They are additionally
            checked against the :data:`~openstack.resource.Resource.base_path`
            format string to see if any path fragments need to be filled in by
            the contents of this argument.
            Parameters supported as filters by the server side are passed in
            the API call, remaining parameters are applied as filters to the
            retrieved results.

        :return: A generator of :class:`Resource` objects.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
            :data:`Resource.allow_list` is not set to ``True``.
        :raises: :exc:`~openstack.exceptions.InvalidResourceQuery` if query
            contains invalid params.
        """
        if not base_path:
            base_path = cls.base_path
            if details:
                base_path += '/detail'

        return super().list(
            session,
            paginated=paginated,
            base_path=base_path,
            allow_unknown_params=allow_unknown_params,
            microversion=microversion,
            **params,
        )

    @classmethod
    def find(
        cls,
        session,
        name_or_id,
        ignore_missing=True,
        list_base_path=None,
        *,
        microversion=None,
        all_projects=None,
        details=False,
        **params,
    ):
        """Find a resource by its name or id.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param name_or_id: This resource's identifier, if needed by
            the request. The default is ``None``.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the resource does not exist.  When set to ``True``, None will be
            returned when attempting to find a nonexistent resource.
        :param str list_base_path: base_path to be used when need listing
            resources.
        :param str microversion: API version to override the negotiated one.
        :param bool details: Whether to return detailed resource records.
        :param dict params: Any additional parameters to be passed into
            underlying methods, such as to
            :meth:`~openstack.resource.Resource.existing` in order to pass on
            URI parameters.

        :return: The :class:`Resource` object matching the given name or id
            or None if nothing matches.
        :raises: :class:`openstack.exceptions.DuplicateResource` if more
            than one resource is found for this request.
        :raises: :class:`openstack.exceptions.ResourceNotFound` if nothing
            is found and ignore_missing is ``False``.
        """
        if not list_base_path:
            list_base_path = cls.base_path
            if details:
                list_base_path += '/detail'

        return super().find(
            session,
            name_or_id,
            ignore_missing=ignore_missing,
            list_base_path=list_base_path,
            microversion=microversion,
            all_projects=all_projects,
            **params,
        )


def comma_separated_list(value):
    if value is None:
        return None
    else:
        return ','.join(value)


def fields_type(value, resource_type):
    if value is None:
        return None

    resource_mapping = {
        key: value.name
        for key, value in resource_type.__dict__.items()
        if isinstance(value, fields.Body)
    }

    return comma_separated_list(resource_mapping.get(x, x) for x in value)
