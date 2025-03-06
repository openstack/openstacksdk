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

from openstack import exceptions
from openstack import resource


class AcceleratorRequest(resource.Resource):
    resource_key = 'arq'
    resources_key = 'arqs'
    base_path = '/accelerator_requests'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_delete = True
    allow_list = True
    #: Allow patch operation for binding.
    allow_patch = True

    #: The device address associated with this ARQ (if any)
    attach_handle_info = resource.Body('attach_handle_info')
    #: The type of attach handle (e.g. PCI, mdev...)
    attach_handle_type = resource.Body('attach_handle_type')
    #: The name of the device profile
    device_profile_name = resource.Body('device_profile_name')
    #: The id of the device profile group
    device_profile_group_id = resource.Body('device_profile_group_id')
    #: The UUID of the bound device RP (if any)
    device_rp_uuid = resource.Body('device_rp_uuid')
    #: The host name to which ARQ is bound. (if any)
    hostname = resource.Body('hostname')
    #: The UUID of the instance associated with this ARQ (if any)
    instance_uuid = resource.Body('instance_uuid')
    #: The state of the ARQ
    state = resource.Body('state')
    #: The UUID of the ARQ
    uuid = resource.Body('uuid', alternate_id=True)

    def _convert_patch(self, patch):
        # This overrides the default behavior of _convert_patch because
        # the PATCH method consumes JSON, its key is the ARQ uuid
        # and its value is an ordinary JSON patch. spec:
        # https://specs.openstack.org/openstack/cyborg-specs/specs/train/implemented/cyborg-api

        converted = super()._convert_patch(patch)
        converted = {self.id: converted}
        return converted

    def patch(
        self,
        session,
        patch=None,
        prepend_key=True,
        has_body=True,
        retry_on_conflict=None,
        base_path=None,
        *,
        microversion=None,
    ):
        # This overrides the default behavior of patch because
        # the PATCH method consumes a dict rather than a list. spec:
        # https://specs.openstack.org/openstack/cyborg-specs/specs/train/implemented/cyborg-api

        # The id cannot be dirty for an commit
        self._body._dirty.discard("id")

        # Only try to update if we actually have anything to commit.
        if not patch and not self.requires_commit:
            return self

        if not self.allow_patch:
            raise exceptions.MethodNotSupported(self, "patch")

        request = self._prepare_request(
            prepend_key=prepend_key, base_path=base_path, patch=True
        )
        microversion = self._get_microversion(session)
        if patch:
            request.body = self._convert_patch(patch)

        return self._commit(
            session,
            request,
            'PATCH',
            microversion,
            has_body=has_body,
            retry_on_conflict=retry_on_conflict,
        )

    def _consume_attrs(self, mapping, attrs):
        # This overrides the default behavior of _consume_attrs because
        # cyborg api returns an ARQ as list. spec:
        # https://specs.openstack.org/openstack/cyborg-specs/specs/train/implemented/cyborg-api
        if isinstance(self, AcceleratorRequest):
            if self.resources_key in attrs:
                attrs = attrs[self.resources_key][0]
        return super()._consume_attrs(mapping, attrs)

    def create(self, session, prepend_key=False, *args, **kwargs):
        # This overrides the default behavior of resource creation because
        # cyborg doesn't accept resource_key in its request.
        return super().create(session, prepend_key, *args, **kwargs)
