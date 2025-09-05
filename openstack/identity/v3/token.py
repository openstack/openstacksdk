# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from keystoneauth1 import adapter

from openstack import exceptions
from openstack import resource


class Token(resource.Resource):
    resource_key = 'token'
    base_path = '/auth/tokens'

    # capabilities
    allow_fetch = False
    allow_delete = False
    allow_list = False
    allow_head = False

    # Properties
    #: An authentication token. This is used rather than X-Auth-Token to allow
    #: users check or revoke a token other than their own.
    subject_token = resource.Header('x-subject-token')

    #: A list of one or two audit IDs. An audit ID is a unique, randomly
    #: generated, URL-safe string that you can use to track a token. The first
    #: audit ID is the current audit ID for the token. The second audit ID is
    #: present for only re-scoped tokens and is the audit ID from the token
    #: before it was re-scoped. A re- scoped token is one that was exchanged
    #: for another token of the same or different scope. You can use these
    #: audit IDs to track the use of a token or chain of tokens across multiple
    #: requests and endpoints without exposing the token ID to non-privileged
    #: users.
    audit_ids = resource.Body('audit_ids', type=list)
    #: The service catalog.
    catalog = resource.Body('catalog', type=list, list_type=dict)
    #: The date and time when the token expires.
    expires_at = resource.Body('expires_at')
    #: The date and time when the token was issued.
    issued_at = resource.Body('issued_at')
    #: The authentication method.
    methods = resource.Body('methods', type=list)
    #: The user that owns the token.
    user = resource.Body('user', type=dict)
    #: The project that the token is scoped to, if any.
    project = resource.Body('project', type=dict)
    #: The domain that the token is scoped to, if any.
    domain = resource.Body('domain', type=dict)
    #: Whether the project, if set, is acting as a domain.
    is_domain = resource.Body('is_domain', type=bool)
    #: The parts of the system the token is scoped to, if system-scoped.
    system = resource.Body('system', type=dict)
    #: The roles associated with the user.
    roles = resource.Body('roles', type=list, list_type=dict)

    @classmethod
    def validate(
        cls,
        session: adapter.Adapter,
        token: str,
        *,
        nocatalog: bool = False,
        allow_expired: bool = False,
    ) -> 'Token':
        path = cls.base_path

        params: dict[str, bool] = {}
        if nocatalog:
            params['nocatalog'] = nocatalog
        if allow_expired:
            params['allow_expired'] = allow_expired

        response = session.get(
            path, headers={'x-subject-token': token}, params=params
        )
        exceptions.raise_from_response(response)

        ret = cls()
        ret._translate_response(
            response, resource_response_key=cls.resource_key
        )
        return ret

    @classmethod
    def check(
        cls,
        session: adapter.Adapter,
        token: str,
        *,
        allow_expired: bool = False,
    ) -> bool:
        params: dict[str, bool] = {}
        if allow_expired:
            params['allow_expired'] = allow_expired

        response = session.head(
            cls.base_path, headers={'x-subject-token': token}, params=params
        )
        return response.status_code == 200

    @classmethod
    def revoke(cls, session: adapter.Adapter, token: str) -> None:
        response = session.delete(
            cls.base_path, headers={'x-subject-token': token}
        )
        exceptions.raise_from_response(response)
