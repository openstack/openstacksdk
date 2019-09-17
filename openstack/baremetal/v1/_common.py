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

from openstack import resource


RETRIABLE_STATUS_CODES = [
    # HTTP Conflict - happens if a node is locked
    409,
    # HTTP Service Unavailable happens if there's no free conductor
    503
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

STATE_VERSIONS = {
    'enroll': '1.11',
    'manageable': '1.4',
}
"""API versions when certain states were introduced."""

VIF_VERSION = '1.28'
"""API version in which the VIF operations were introduced."""


class ListMixin(object):

    @classmethod
    def list(cls, session, details=False, **params):
        """This method is a generator which yields resource objects.

        This resource object list generator handles pagination and takes query
        params for response filtering.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param bool details: Whether to return detailed node records
        :param dict params: These keyword arguments are passed through the
            :meth:`~openstack.resource.QueryParameter._transpose` method
            to find if any of them match expected query parameters to be
            sent in the *params* argument to
            :meth:`~keystoneauth1.adapter.Adapter.get`.

        :return: A generator of :class:`openstack.resource.Resource` objects.
        :raises: :exc:`~openstack.exceptions.InvalidResourceQuery` if query
                 contains invalid params.
        """
        base_path = cls.base_path
        if details:
            base_path += '/detail'
        return super(ListMixin, cls).list(session, paginated=True,
                                          base_path=base_path, **params)


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
        if isinstance(value, resource.Body)
    }

    return comma_separated_list(resource_mapping.get(x, x) for x in value)
