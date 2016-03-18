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

import six

from openstack import resource
from openstack.telemetry import telemetry_service


class Capability(resource.Resource):
    """.. caution:: This API is a work in progress and is subject to change."""
    resource_key = 'capability'
    resources_key = 'capabilities'
    base_path = '/capabilities'
    service = telemetry_service.TelemetryService()

    # Supported Operations
    allow_list = True

    # Properties
    is_enabled = resource.prop('enabled', type=bool)

    @classmethod
    def list(cls, session, limit=None, marker=None, path_args=None,
             paginated=False, **params):
        resp = session.get(cls.base_path, endpoint_filter=cls.service,
                           params=params)
        resp = resp.json()
        for key, value in six.iteritems(resp['api']):
            yield cls.existing(id=key, enabled=value)
