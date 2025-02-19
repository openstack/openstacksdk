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

from openstack import exceptions
from openstack import resource


# ATTENTION: Please do not inherit this class for anything else then QuotaSet,
# since attribute processing is here very different!
class QuotaSet(resource.Resource):
    resource_key = 'quota_set'
    # ATTENTION: different services might be using different base_path
    base_path = '/os-quota-sets/%(project_id)s'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_delete = True
    allow_commit = True

    _query_mapping = resource.QueryParameters("usage")

    # NOTE(gtema) Sadly this attribute is useless in all the methods, but keep
    # it here extra as a reminder
    requires_id = False

    # Quota-sets are not very well designed. We must keep what is
    # there and try to process it on best effort
    _allow_unknown_attrs_in_body = True

    #: Properties
    #: Current reservations
    #: *type:dict*
    reservation = resource.Body('reservation', type=dict)
    #: Quota usage
    #: *type:dict*
    usage = resource.Body('usage', type=dict)

    project_id = resource.URI('project_id')

    def fetch(
        self,
        session,
        requires_id=False,
        base_path=None,
        error_message=None,
        skip_cache=False,
        *,
        resource_response_key=None,
        microversion=None,
        **params,
    ):
        return super().fetch(
            session,
            requires_id,
            base_path,
            error_message,
            skip_cache,
            resource_response_key=resource_response_key,
            microversion=microversion,
            **params,
        )

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
                if self.resource_key and self.resource_key in body:
                    body = body[self.resource_key]

                # Do not allow keys called "self" through. Glance chose
                # to name a key "self", so we need to pop it out because
                # we can't send it through cls.existing and into the
                # Resource initializer. "self" is already the first
                # argument and is practically a reserved word.
                body.pop("self", None)

                # Process body_attrs to strip usage and reservation out
                normalized_attrs: dict[str, ty.Any] = dict(
                    reservation={},
                    usage={},
                )

                for key, val in body.items():
                    if isinstance(val, dict):
                        if 'in_use' in val:
                            normalized_attrs['usage'][key] = val['in_use']
                        if 'reserved' in val:
                            normalized_attrs['reservation'][key] = val[
                                'reserved'
                            ]
                        if 'limit' in val:
                            normalized_attrs[key] = val['limit']
                    else:
                        normalized_attrs[key] = val

                self._unknown_attrs_in_body.update(normalized_attrs)

                self._body.attributes.update(normalized_attrs)
                self._body.clean()
                if self.commit_jsonpatch or self.allow_patch:
                    # We need the original body to compare against
                    self._original_body = normalized_attrs.copy()
            except ValueError:
                # Server returned not parsable response (202, 204, etc)
                # Do simply nothing
                pass

        headers = self._consume_header_attrs(response.headers)
        self._header.attributes.update(headers)
        self._header.clean()
        self._update_location()
        dict.update(self, self.to_dict())

    def _prepare_request_body(
        self,
        patch,
        prepend_key,
        *,
        resource_request_key=None,
    ):
        body = self._body.dirty
        # Ensure we never try to send meta props reservation and usage
        body.pop('reservation', None)
        body.pop('usage', None)

        if prepend_key and self.resource_key is not None:
            body = {self.resource_key: body}
        return body
