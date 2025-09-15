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

import typing as ty
import uuid

from keystoneauth1 import adapter
import typing_extensions as ty_ext

from openstack import resource


class MessageResource(resource.Resource):
    # FIXME(anyone): The name string of `location` field of Zaqar API response
    # is lower case. That is inconsistent with the guide from API-WG. This is
    # a workaround for this issue.
    location = resource.Header("location")

    #: The ID to identify the client accessing Zaqar API. Must be specified
    #: in header for each API request.
    client_id = resource.Header("Client-ID")
    #: The ID to identify the project. Must be provided when keystone
    #: authentication is not enabled in Zaqar service.
    project_id = resource.Header("X-PROJECT-ID")

    @classmethod
    def list(
        cls,
        session: adapter.Adapter,
        paginated: bool = True,
        base_path: str | None = None,
        allow_unknown_params: bool = False,
        *,
        microversion: str | None = None,
        headers: dict[str, str] | None = None,
        max_items: int | None = None,
        **params: ty.Any,
    ) -> ty.Generator[ty_ext.Self, None, None]:
        """This method is a generator which yields resource objects.

        This is almost the copy of list method of resource.Resource class.
        The only difference is the request header now includes `Client-ID`
        and `X-PROJECT-ID` fields which are required by Zaqar v2 API.
        """
        more_data = True

        if base_path is None:
            base_path = cls.base_path

        uri = base_path % params

        project_id = params.get('project_id', None) or session.get_project_id()
        assert project_id is not None

        headers = {
            "Client-ID": params.get('client_id', None) or str(uuid.uuid4()),
            "X-PROJECT-ID": project_id,
        }

        query_params = cls._query_mapping._transpose(params, cls)
        while more_data:
            resp = session.get(
                uri, headers=headers, params=query_params
            ).json()[cls.resources_key]

            if not resp:
                more_data = False

            yielded = 0
            new_marker = None
            for data in resp:
                value = cls.existing(**data)
                new_marker = value.id
                yielded += 1
                yield value

            if not paginated:
                return
            if "limit" in query_params and yielded < query_params["limit"]:
                return
            query_params["limit"] = yielded
            query_params["marker"] = new_marker

    def fetch(
        self,
        session,
        requires_id=True,
        base_path=None,
        error_message=None,
        skip_cache=False,
        **kwargs,
    ):
        request = self._prepare_request(
            requires_id=requires_id, base_path=base_path
        )
        headers = {
            "Client-ID": self.client_id or str(uuid.uuid4()),
            "X-PROJECT-ID": self.project_id or session.get_project_id(),
        }
        request.headers.update(headers)
        response = session.get(
            request.url, headers=headers, skip_cache=skip_cache
        )
        self._translate_response(response)

        return self

    def delete(
        self, session, error_message=None, *, microversion=None, **kwargs
    ):
        request = self._prepare_request()
        headers = {
            "Client-ID": self.client_id or str(uuid.uuid4()),
            "X-PROJECT-ID": self.project_id or session.get_project_id(),
        }
        request.headers.update(headers)
        response = session.delete(request.url, headers=headers)

        self._translate_response(response, has_body=False)
        return self
