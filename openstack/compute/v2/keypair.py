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


class Keypair(resource2.Resource):
    resource_key = 'keypair'
    resources_key = 'keypairs'
    base_path = '/os-keypairs'
    service = compute_service.ComputeService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The short fingerprint associated with the ``public_key`` for
    #: this keypair.
    fingerprint = resource2.Body('fingerprint')
    # NOTE: There is in fact an 'id' field. However, it's not useful
    # because all operations use the 'name' as an identifier.
    # Additionally, the 'id' field only appears *after* creation,
    # so suddenly you have an 'id' field filled in after the fact,
    # and it just gets in the way. We need to cover this up by having
    # the name be both our id and name.
    #: The id identifying the keypair
    id = resource2.Body('name')
    #: A name identifying the keypair
    name = resource2.Body('name', alternate_id=True)
    #: The private key for the keypair
    private_key = resource2.Body('private_key')
    #: The SSH public key that is paired with the server.
    public_key = resource2.Body('public_key')

    @classmethod
    def list(cls, session, paginated=False):
        resp = session.get(cls.base_path, endpoint_filter=cls.service,
                           headers={"Accept": "application/json"})
        resp = resp.json()
        resp = resp[cls.resources_key]

        for data in resp:
            value = cls.existing(**data[cls.resource_key])
            yield value
