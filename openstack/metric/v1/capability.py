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

from openstack.metric import metric_service
from openstack import resource


class Capability(resource.Resource):
    base_path = '/capabilities'
    service = metric_service.MetricService()

    # Supported Operations
    allow_list = True

    # Properties
    value = resource.prop('value')

    @classmethod
    def page(cls, session, limit, marker=None, path_args=None, **params):
        if marker:
            return []

        resp = super(Capability, cls).page(session, limit,
                                           marker, path_args, **params)

        return [{"id": key, "value": value}
                for key, value in six.iteritems(resp)]
