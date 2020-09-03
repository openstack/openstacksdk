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

    _query_mapping = resource.QueryParameters(
        'user_id')

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_delete = True
    allow_list = True

    _max_microversion = '2.10'

    # Properties
    #: The date and time when the resource was created.
    created_at = resource.Body('created_at')
    #: A boolean indicates whether this keypair is deleted or not.
    is_deleted = resource.Body('deleted', type=bool)
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
    #: The type of the keypair.
    type = resource.Body('type', default='ssh')
    #: The user_id for a keypair.
    user_id = resource.Body('user_id')

    def _consume_attrs(self, mapping, attrs):
        # TODO(mordred) This should not be required. However, without doing
        # it **SOMETIMES** keypair picks up id and not name. This is a hammer.
        if 'id' in attrs:
            attrs.setdefault('name', attrs.pop('id'))
        return super(Keypair, self)._consume_attrs(mapping, attrs)

    @classmethod
    def existing(cls, connection=None, **kwargs):
        """Create an instance of an existing remote resource.

        When creating the instance set the ``_synchronized`` parameter
        of :class:`Resource` to ``True`` to indicate that it represents the
        state of an existing server-side resource. As such, all attributes
        passed in ``**kwargs`` are considered "clean", such that an immediate
        :meth:`update` call would not generate a body of attributes to be
        modified on the server.

        :param dict kwargs: Each of the named arguments will be set as
                            attributes on the resulting Resource object.
        """
        # Listing KPs return list with resource_key structure. Instead of
        # overriding whole list just try to create object smart.
        if cls.resource_key in kwargs:
            args = kwargs.pop(cls.resource_key)
            kwargs.update(**args)
        return cls(_synchronized=True, connection=connection, **kwargs)
