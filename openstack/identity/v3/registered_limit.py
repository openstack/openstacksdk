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


class RegisteredLimit(resource.Resource):
    resource_key = 'registered_limit'
    resources_key = 'registered_limits'
    base_path = '/registered_limits'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    commit_method = 'PATCH'
    commit_jsonpatch = True

    _query_mapping = resource.QueryParameters(
        'service_id', 'region_id', 'resource_name'
    )

    # Properties
    #: User-facing description of the registered_limit. *Type: string*
    description = resource.Body('description')
    #: The links for the registered_limit resource.
    links = resource.Body('links')
    #: ID of service. *Type: string*
    service_id = resource.Body('service_id')
    #: ID of region, if any. *Type: string*
    region_id = resource.Body('region_id')
    #: The resource name. *Type: string*
    resource_name = resource.Body('resource_name')
    #: The default limit value. *Type: int*
    default_limit = resource.Body('default_limit')

    def create(
        self,
        session,
        prepend_key=True,
        base_path=None,
        *,
        resource_request_key=None,
        resource_response_key='registered_limits',
        microversion=None,
        **params,
    ):
        return super().create(
            session,
            prepend_key=prepend_key,
            base_path=base_path,
            resource_request_key=resource_request_key,
            resource_response_key=resource_response_key,
            microversion=microversion,
            **params,
        )

    def _prepare_request_body(
        self,
        patch,
        prepend_key,
        *,
        resource_request_key=None,
    ):
        body = self._body.dirty
        if prepend_key and self.resource_key is not None:
            if patch:
                body = {self.resource_key: body}
            else:
                # Keystone supports bunch create for registered limit. So the
                # request body for creating registered_limit is a list instead
                # of dict.
                body = {self.resources_key: [body]}
        return body

    def _translate_response(
        self,
        response,
        has_body=None,
        error_message=None,
        *,
        resource_response_key=None,
    ):
        """Given a KSA response, inflate this instance with its data

        DELETE operations don't return a body, so only try to work
        with a body when has_body is True.

        This method updates attributes that correspond to headers
        and body on this instance and clears the dirty set.
        """
        if has_body is None:
            has_body = self.has_body

        exceptions.raise_from_response(response, error_message=error_message)

        if has_body:
            try:
                body = response.json()
                if resource_response_key and resource_response_key in body:
                    body = body[resource_response_key]
                elif self.resource_key and self.resource_key in body:
                    body = body[self.resource_key]

                # Keystone supports bunch create for registered limit. So the
                # response body for creating registered_limit is a list instead of dict.
                if isinstance(body, list):
                    body = body[0]

                # Do not allow keys called "self" through. Glance chose
                # to name a key "self", so we need to pop it out because
                # we can't send it through cls.existing and into the
                # Resource initializer. "self" is already the first
                # argument and is practically a reserved word.
                body.pop("self", None)

                body_attrs = self._consume_body_attrs(body)
                if self._allow_unknown_attrs_in_body:
                    body_attrs.update(body)
                    self._unknown_attrs_in_body.update(body)
                elif self._store_unknown_attrs_as_properties:
                    body_attrs = self._pack_attrs_under_properties(
                        body_attrs, body
                    )

                self._body.attributes.update(body_attrs)
                self._body.clean()
                if self.commit_jsonpatch or self.allow_patch:
                    # We need the original body to compare against
                    self._original_body = body_attrs.copy()
            except ValueError:
                # Server returned not parse-able response (202, 204, etc)
                # Do simply nothing
                pass

        headers = self._consume_header_attrs(response.headers)
        self._header.attributes.update(headers)
        self._header.clean()
        self._update_location()
        dict.update(self, self.to_dict())
