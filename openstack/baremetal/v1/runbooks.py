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

from keystoneauth1 import adapter

from openstack.baremetal.v1 import _common
from openstack import exceptions
from openstack import resource
from openstack import utils


class Runbook(_common.Resource):
    resources_key = 'runbooks'
    base_path = '/runbooks'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    allow_patch = True
    commit_method = 'PATCH'

    _query_mapping = resource.QueryParameters(
        'detail',
        fields={'type': _common.fields_type},
    )

    # Runbooks is available since 1.92
    # The description and traits fields added in 1.112
    _max_microversion = '1.112'
    name = resource.Body('name')
    #: Timestamp at which the runbook was created.
    created_at = resource.Body('created_at')
    #: A human readable description of the runbook. Introduced in API
    #: microversion 1.112.
    description = resource.Body('description')
    #: A set of one or more arbitrary metadata key and value pairs.
    extra = resource.Body('extra')
    #: A list of relative links. Includes the self and bookmark links.
    links = resource.Body('links', type=list)
    #: A set of physical information of the runbook.
    steps = resource.Body('steps', type=list)
    #: Indicates whether the runbook is publicly accessible.
    public = resource.Body('public', type=bool)
    #: The name or ID of the project that owns the runbook.
    owner = resource.Body('owner', type=str)
    #: The traits of the runbook. A node may only be acted upon by a runbook
    #: whose traits intersect with the traits of the node. Read-only here, use
    #: the trait methods to modify it. Introduced in API microversion 1.112.
    traits = resource.Body('traits', type=list)
    #: Timestamp at which the runbook was last updated.
    updated_at = resource.Body('updated_at')
    #: The UUID of the resource.
    id = resource.Body('uuid', alternate_id=True)

    def add_trait(self, session: adapter.Adapter, trait: str) -> None:
        """Add a trait to the runbook.

        :param session: The session to use for making this request.
        :param trait: The trait to add to the runbook.
        :returns: ``None``
        """
        session = self._get_session(session)
        version = utils.pick_microversion(
            session, _common.RUNBOOK_TRAITS_VERSION
        )
        request = self._prepare_request(requires_id=True)
        request.url = utils.urljoin(request.url, 'traits', trait)
        response = session.put(
            request.url,
            json=None,
            headers=request.headers,
            microversion=version,
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

        msg = f"Failed to add trait {trait} for runbook {self.id}"
        exceptions.raise_from_response(response, error_message=msg)

        self.traits = list(set(self.traits or ()) | {trait})

    def remove_trait(self, session: adapter.Adapter, trait: str) -> None:
        """Remove a trait from the runbook.

        Removing a trait the runbook does not have is a no-op on the server
        side.

        :param session: The session to use for making this request.
        :param trait: The trait to remove from the runbook.
        :returns: ``None``
        """
        session = self._get_session(session)
        version = utils.pick_microversion(
            session, _common.RUNBOOK_TRAITS_VERSION
        )
        request = self._prepare_request(requires_id=True)
        request.url = utils.urljoin(request.url, 'traits', trait)

        response = session.delete(
            request.url,
            headers=request.headers,
            microversion=version,
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

        msg = f"Failed to remove trait {trait} from runbook {self.id}"
        exceptions.raise_from_response(response, error_message=msg)

        if self.traits:
            self.traits = list(set(self.traits) - {trait})

    def set_traits(self, session: adapter.Adapter, traits: list[str]) -> None:
        """Set traits for the runbook.

        Removes any existing traits and adds the traits passed in to this
        method. Pass an empty list to remove all traits.

        :param session: The session to use for making this request.
        :param traits: list of traits to set on the runbook.
        :returns: ``None``
        """
        session = self._get_session(session)
        version = utils.pick_microversion(
            session, _common.RUNBOOK_TRAITS_VERSION
        )
        request = self._prepare_request(requires_id=True)
        request.url = utils.urljoin(request.url, 'traits')

        body = {'traits': traits}

        response = session.put(
            request.url,
            json=body,
            headers=request.headers,
            microversion=version,
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

        msg = f"Failed to set traits for runbook {self.id}"
        exceptions.raise_from_response(response, error_message=msg)

        self.traits = traits
