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

from openstack import resource


class Workflow(resource.Resource):
    resource_key = 'workflow'
    resources_key = 'workflows'
    base_path = '/workflows'

    # capabilities
    allow_create = True
    allow_commit = True
    allow_list = True
    allow_fetch = True
    allow_delete = True

    _query_mapping = resource.QueryParameters(
        'marker', 'limit', 'sort_keys', 'sort_dirs', 'fields'
    )

    #: The name of this Workflow
    name = resource.Body("name")
    #: The inputs for this Workflow
    input = resource.Body("input")
    #: A Workflow definition using the Mistral v2 DSL
    definition = resource.Body("definition")
    #: A list of values associated with a workflow that users can use
    #: to group workflows by some criteria
    # TODO(briancurtin): type=list
    tags = resource.Body("tags")
    #: Can be either "private" or "public"
    scope = resource.Body("scope")
    #: The ID of the associated project
    project_id = resource.Body("project_id")
    #: The time at which the workflow was created
    created_at = resource.Body("created_at")
    #: The time at which the workflow was created
    updated_at = resource.Body("updated_at")

    def _request_kwargs(
        self,
        prepend_key: bool = True,
        base_path: str | None = None,
    ) -> dict[str, Any]:
        request = self._prepare_request(
            requires_id=False, prepend_key=prepend_key, base_path=base_path
        )

        headers = {"Content-Type": 'text/plain'}
        kwargs = {
            "data": self.definition,
        }

        scope = f"?scope={self.scope}"
        uri = request.url + scope

        request.headers.update(headers)
        return dict(url=uri, json=None, headers=request.headers, **kwargs)

    # TODO(stephenfin): Migrate to _transform_create_request once _Request
    # gains a 'data' field for non-JSON request bodies. Currently the override
    # sends the workflow definition as text/plain via data=self.definition with
    # json=None, which cannot be expressed through the standard request object.
    def create(
        self,
        session: adapter.Adapter,
        prepend_key: bool = True,
        base_path: str | None = None,
        **params: Any,
    ) -> Self:
        kwargs = self._request_kwargs(
            prepend_key=prepend_key, base_path=base_path
        )
        response = session.post(**kwargs)
        self._translate_response(response, has_body=False)
        return self

    def commit(
        self,
        session: adapter.Adapter,
        prepend_key: bool = True,
        has_body: bool = True,
        retry_on_conflict: bool | None = None,
        base_path: str | None = None,
        *,
        microversion: str | None = None,
        **kwargs: Any,
    ) -> Self:
        request_kwargs = self._request_kwargs(
            prepend_key=prepend_key, base_path=base_path
        )
        response = session.put(**request_kwargs)
        self._translate_response(response, has_body=False)
        return self
