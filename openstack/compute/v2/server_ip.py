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

from openstack.compute import compute_service
from openstack import resource2
from openstack import utils


class ServerIP(resource2.Resource):
    resources_key = 'addresses'
    base_path = '/servers/%(server_id)s/ips'
    service = compute_service.ComputeService()

    # capabilities
    allow_list = True

    # Properties
    #: The IP address. The format of the address depends on :attr:`version`
    address = resource2.Body('addr')
    #: The network label, such as public or private.
    network_label = resource2.URI('network_label')
    #: The ID for the server.
    server_id = resource2.URI('server_id')
    # Version of the IP protocol. Currently either 4 or 6.
    version = resource2.Body('version')

    @classmethod
    def list(cls, session, paginated=False, server_id=None,
             network_label=None, **params):
        url = cls.base_path % {"server_id": server_id}

        if network_label is not None:
            url = utils.urljoin(url, network_label)

        resp = session.get(url, endpoint_filter=cls.service)
        resp = resp.json()

        if network_label is None:
            resp = resp[cls.resources_key]

        for label, addresses in resp.items():
            for address in addresses:
                yield cls.existing(network_label=label,
                                   address=address["addr"],
                                   version=address["version"])
