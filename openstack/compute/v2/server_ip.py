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

from keystoneauth1 import adapter
import typing_extensions as ty_ext

from openstack import resource
from openstack import utils


class ServerIP(resource.Resource):
    resources_key = 'addresses'
    base_path = '/servers/%(server_id)s/ips'

    # capabilities
    allow_list = True

    # Properties
    #: The IP address. The format of the address depends on :attr:`version`
    address = resource.Body('addr')
    #: The network label, such as public or private.
    network_label = resource.URI('network_label')
    #: The ID for the server.
    server_id = resource.URI('server_id')
    # Version of the IP protocol. Currently either 4 or 6.
    version = resource.Body('version')

    @classmethod
    def list(
        cls,
        session: adapter.Adapter,
        paginated: bool = False,
        base_path: str | None = None,
        allow_unknown_params: bool = False,
        *,
        microversion: str | None = None,
        headers: dict[str, str] | None = None,
        max_items: int | None = None,
        server_id: str | None = None,
        network_label: str | None = None,
        **params: ty.Any,
    ) -> ty.Generator[ty_ext.Self, None, None]:
        if base_path is None:
            base_path = cls.base_path

        url = base_path % {"server_id": server_id}

        if network_label is not None:
            url = utils.urljoin(url, network_label)

        resp = session.get(url)
        resp = resp.json()

        if network_label is None:
            resp = resp[cls.resources_key]

        for label, addresses in resp.items():
            for address in addresses:
                yield cls.existing(
                    network_label=label,
                    address=address["addr"],
                    version=address["version"],
                )
