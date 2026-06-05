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

from typing import Any

from keystoneauth1 import adapter
import requests

from openstack import exceptions
from openstack import resource


class SecretConsumer(resource.Resource):
    resources_key = 'consumers'
    base_path = '/secrets/%(secret_id)s/consumers'

    allow_create = True
    allow_delete = True
    allow_list = True

    # DELETE on this endpoint uses a body and does not target a specific id
    requires_id = False

    # URI parameters
    secret_id = resource.URI('secret_id')

    service = resource.Body('service')
    resource_type = resource.Body('resource_type')
    resource_id = resource.Body('resource_id')

    def _raw_delete(
        self,
        session: adapter.Adapter,
        microversion: str | None = None,
        **attrs: Any,
    ) -> requests.Response:
        """Custom raw_delete method for Barbican consumers.

        Barbican requires DELETE requests to include a JSON body with
        service, resource_type, and resource_id fields.
        """
        if not self.allow_delete:
            raise exceptions.MethodNotSupported(self, 'delete')

        request = self._prepare_request(**attrs)
        session = self._get_session(session)
        if microversion is None:
            microversion = self._get_microversion(session)

        # Barbican expects JSON body with service/resource_type/resource_id
        body = self._prepare_request_body(prepend_key=False)

        return session.delete(
            request.url,
            json=body,
            headers=request.headers,
            microversion=microversion,
        )
