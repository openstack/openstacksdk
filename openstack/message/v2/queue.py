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

import uuid

from openstack import resource


class Queue(resource.Resource):
    # FIXME(anyone): The name string of `location` field of Zaqar API response
    # is lower case. That is inconsistent with the guide from API-WG. This is
    # a workaround for this issue.
    location = resource.Header("location")

    resources_key = "queues"
    base_path = "/queues"

    # capabilities
    allow_create = True
    allow_list = True
    allow_fetch = True
    allow_delete = True

    # Properties
    #: The default TTL of messages defined for a queue, which will effect for
    #: any messages posted to the queue.
    default_message_ttl = resource.Body("_default_message_ttl")
    #: Description of the queue.
    description = resource.Body("description")
    #: The max post size of messages defined for a queue, which will effect
    #: for any messages posted to the queue.
    max_messages_post_size = resource.Body("_max_messages_post_size")
    #: Name of the queue. The name is the unique identity of a queue. It
    #: must not exceed 64 bytes in length, and it is limited to US-ASCII
    #: letters, digits, underscores, and hyphens.
    name = resource.Body("name", alternate_id=True)
    #: The ID to identify the client accessing Zaqar API. Must be specified
    #: in header for each API request.
    client_id = resource.Header("Client-ID")
    #: The ID to identify the project accessing Zaqar API. Must be specified
    #: in case keystone auth is not enabled in Zaqar service.
    project_id = resource.Header("X-PROJECT-ID")

    def create(self, session, prepend_key=False, base_path=None, **kwargs):
        request = self._prepare_request(
            requires_id=True, prepend_key=prepend_key, base_path=None
        )
        headers = {
            "Client-ID": self.client_id or str(uuid.uuid4()),
            "X-PROJECT-ID": self.project_id or session.get_project_id(),
        }
        request.headers.update(headers)
        response = session.put(
            request.url, json=request.body, headers=request.headers
        )

        self._translate_response(response, has_body=False)
        return self

    @classmethod
    def list(cls, session, paginated=False, base_path=None, **params):
        """This method is a generator which yields queue objects.

        This is almost the copy of list method of resource.Resource class.
        The only difference is the request header now includes `Client-ID`
        and `X-PROJECT-ID` fields which are required by Zaqar v2 API.
        """
        more_data = True
        query_params = cls._query_mapping._transpose(params, cls)

        if base_path is None:
            base_path = cls.base_path

        uri = base_path % params
        headers = {
            "Client-ID": params.get('client_id', None) or str(uuid.uuid4()),
            "X-PROJECT-ID": params.get('project_id', None)
            or session.get_project_id(),
        }

        while more_data:
            resp = session.get(uri, headers=headers, params=query_params)
            resp = resp.json()
            resp = resp[cls.resources_key]

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
