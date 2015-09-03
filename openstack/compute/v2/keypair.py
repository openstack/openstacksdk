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
from openstack import resource


class Keypair(resource.Resource):
    id_attribute = 'name'
    name_attribute = None
    resource_key = 'keypair'
    resources_key = 'keypairs'
    base_path = '/os-keypairs'
    service = compute_service.ComputeService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The short fingerprint associated with the ``public_key`` for
    #: this keypair.
    fingerprint = resource.prop('fingerprint')
    #: A name identifying the keypair
    name = resource.prop('name')
    #: The private key for the keypair
    private_key = resource.prop('private_key')
    #: The SSH public key that is paired with the server.
    public_key = resource.prop('public_key')

    def __init__(self, attrs=None, loaded=False):
        if attrs is not None:
            if 'keypair' in attrs:
                attrs = attrs['keypair']
        super(Keypair, self).__init__(attrs, loaded=loaded)

    def create(self, session):
        """Create a new keypair from this instance.

        This is needed because the name is the id, but we can't create one
        with a PUT.  That and we need the private_key out of the response.
        """
        resp = self.create_by_id(session, self._attrs)
        self._attrs = resp
        self._reset_dirty()
        return self
