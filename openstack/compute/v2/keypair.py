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

from openstack import resource


class Keypair(resource.Resource):
    resource_key = 'keypair'
    resources_key = 'keypairs'
    base_path = '/os-keypairs'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The short fingerprint associated with the ``public_key`` for
    #: this keypair.
    fingerprint = resource.Body('fingerprint')
    # NOTE: There is in fact an 'id' field. However, it's not useful
    # because all operations use the 'name' as an identifier.
    # Additionally, the 'id' field only appears *after* creation,
    # so suddenly you have an 'id' field filled in after the fact,
    # and it just gets in the way. We need to cover this up by listing
    # name as alternate_id and listing id as coming from name.
    #: The id identifying the keypair
    id = resource.Body('name')
    #: A name identifying the keypair
    name = resource.Body('name', alternate_id=True)
    #: The private key for the keypair
    private_key = resource.Body('private_key')
    #: The SSH public key that is paired with the server.
    public_key = resource.Body('public_key')

    def _consume_attrs(self, mapping, attrs):
        # TODO(mordred) This should not be required. However, without doing
        # it **SOMETIMES** keypair picks up id and not name. This is a hammer.
        if 'id' in attrs:
            attrs.setdefault('name', attrs.pop('id'))
        return super(Keypair, self)._consume_attrs(mapping, attrs)

    @classmethod
    def list(cls, session, paginated=False):
        resp = session.get(cls.base_path,
                           headers={"Accept": "application/json"})
        resp = resp.json()
        resp = resp[cls.resources_key]

        for data in resp:
            value = cls.existing(**data[cls.resource_key])
            yield value
