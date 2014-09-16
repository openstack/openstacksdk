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


class ServerIP(resource.Resource):
    id_attribute = 'addr'
    resource_key = 'server_ip'
    resources_key = 'server_ips'
    base_path = '/servers/%(server_id)s/ips'
    service = compute_service.ComputeService()

    # capabilities
    allow_list = True

    # Properties
    addr = resource.prop('addr')
    network_label = resource.prop('network_label')
    server_id = resource.prop('server_id')
    version = resource.prop('version')

    @classmethod
    def list(cls, session, path_args=None, **params):
        url = cls.base_path % path_args
        resp = session.get(url, service=cls.service, params=params)
        ray = []
        for network_label, addresses in six.iteritems(resp.body['addresses']):
            for address in addresses:
                record = {
                    'server_id': path_args['server_id'],
                    'network_label': network_label,
                    'version': address['version'],
                    'addr': address['addr'],
                }
                ray.append(cls.existing(**record))
        return ray
