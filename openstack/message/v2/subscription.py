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


class Subscription(resource.Resource):
    # FIXME(anyone): The name string of `location` field of Zaqar API response
    # is lower case. That is inconsistent with the guide from API-WG. This is
    # a workaround for this issue.
    location = resource.Header("location")

    resources_key = 'subscriptions'
    base_path = '/queues/%(queue_name)s/subscriptions'

    # capabilities
    allow_create = True
    allow_list = True
    allow_fetch = True
    allow_delete = True

    # Properties
    #: The value in seconds indicating how long the subscription has existed.
    age = resource.Body("age")
    #: Alternate id of the subscription. This key is used in response of
    #: subscription create API to return id of subscription created.
    subscription_id = resource.Body("subscription_id", alternate_id=True)
    #: The extra metadata for the subscription. The value must be a dict.
    #: If the subscriber is `mailto`. The options can contain `from` and
    #: `subject` to indicate the email's author and title.
    options = resource.Body("options", type=dict)
    #: The queue name which the subscription is registered on.
    source = resource.Body("source")
    #: The destination of the message. Two kinds of subscribers are supported:
    #: http/https and email. The http/https subscriber should start with
    #: `http/https`. The email subscriber should start with `mailto`.
    subscriber = resource.Body("subscriber")
    #: Number of seconds the subscription remains alive? The ttl value must
    #: be great than 60 seconds. The default value is 3600 seconds.
    ttl = resource.Body("ttl")
    #: The queue name which the subscription is registered on.
    queue_name = resource.URI("queue_name")
    #: The ID to identify the client accessing Zaqar API. Must be specified
    #: in header for each API request.
    client_id = resource.Header("Client-ID")
    #: The ID to identify the project. Must be provided when keystone
    #: authentication is not enabled in Zaqar service.
    project_id = resource.Header("X-PROJECT-ID")

    def create(self, session, prepend_key=True, base_path=None):
        request = self._prepare_request(requires_id=False,
                                        prepend_key=prepend_key,
                                        base_path=base_path)
        headers = {
            "Client-ID": self.client_id or str(uuid.uuid4()),
            "X-PROJECT-ID": self.project_id or session.get_project_id()
        }
        request.headers.update(headers)
        response = session.post(request.url,
                                json=request.body, headers=request.headers)

        self._translate_response(response)
        return self

    @classmethod
    def list(cls, session, paginated=True, base_path=None, **params):
        """This method is a generator which yields subscription objects.

        This is almost the copy of list method of resource.Resource class.
        The only difference is the request header now includes `Client-ID`
        and `X-PROJECT-ID` fields which are required by Zaqar v2 API.
        """
        more_data = True

        if base_path is None:
            base_path = cls.base_path

        uri = base_path % params
        headers = {
            "Client-ID": params.get('client_id', None) or str(uuid.uuid4()),
            "X-PROJECT-ID": params.get('project_id', None
                                       ) or session.get_project_id()
        }

        query_params = cls._query_mapping._transpose(params, cls)
        while more_data:
            resp = session.get(uri,
                               headers=headers, params=query_params)
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

    def fetch(self, session, requires_id=True,
              base_path=None, error_message=None):
        request = self._prepare_request(requires_id=requires_id,
                                        base_path=base_path)
        headers = {
            "Client-ID": self.client_id or str(uuid.uuid4()),
            "X-PROJECT-ID": self.project_id or session.get_project_id()
        }

        request.headers.update(headers)
        response = session.get(request.url,
                               headers=request.headers)
        self._translate_response(response)

        return self

    def delete(self, session):
        request = self._prepare_request()
        headers = {
            "Client-ID": self.client_id or str(uuid.uuid4()),
            "X-PROJECT-ID": self.project_id or session.get_project_id()
        }

        request.headers.update(headers)
        response = session.delete(request.url,
                                  headers=request.headers)

        self._translate_response(response, has_body=False)
        return self
