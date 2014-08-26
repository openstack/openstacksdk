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

from openstack.compute import compute_service
from openstack import resource


class LimitsAbsolute(resource.Resource):
    resource_key = 'limits_absolute'
    resources_key = 'limits_absolutes'
    base_path = '/limits'
    service = compute_service.ComputeService()

    # capabilities
    allow_list = True

    # Properties
    name = resource.prop('name')
    value = resource.prop('value')

    @classmethod
    def list(cls, session, path_args=None, **params):
        url = cls.base_path
        resp = session.get(url, service=cls.service, params=params).body
        resp = resp['limits']['absolute']
        return [cls.existing(name=key, value=value)
                for key, value in six.iteritems(resp)]
