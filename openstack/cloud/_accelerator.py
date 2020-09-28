# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# import types so that we can reference ListType in sphinx param declarations.
# We can't just use list, because sphinx gets confused by
# openstack.resource.Resource.list and openstack.resource2.Resource.list

from openstack.cloud import _normalize


class AcceleratorCloudMixin(_normalize.Normalizer):

    def list_deployables(self, filters=None):
        """List all available deployables.
        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of deployable info.
        """

        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}
        return list(self.accelerator.deployables(**filters))

    def list_devices(self, filters=None):
        """List all devices.
        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of device info.
        """

        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}
        return list(self.accelerator.devices(**filters))

    def list_device_profiles(self, filters=None):
        """List all device_profiles.
        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of device profile info.
        """

        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}
        return list(self.accelerator.device_profiles(**filters))

    def create_device_profile(self, attrs):
        """Create a device_profile.
        :param attrs: The info of device_profile to be created.
        :returns: A ``munch.Munch`` of the created device_profile.
        """

        return self.accelerator.create_device_profile(**attrs)

    def delete_device_profile(self, name_or_id, filters):
        """Delete a device_profile.
        :param name_or_id: The Name(or uuid) of device_profile to be deleted.
        :param filters: dict of filter conditions to push down
        :returns: True if delete succeeded, False otherwise.
        """

        device_profile = self.accelerator.get_device_profile(
            name_or_id,
            filters
        )
        if device_profile is None:
            self.log.debug(
                "device_profile %s not found for deleting",
                name_or_id
            )
            return False

        self.accelerator.delete_device_profile(name_or_id=name_or_id)

        return True

    def list_accelerator_requests(self, filters=None):
        """List all accelerator_requests.
        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of accelerator request info.
        """

        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}
        return list(self.accelerator.accelerator_requests(**filters))

    def delete_accelerator_request(self, name_or_id, filters):
        """Delete a accelerator_request.
        :param name_or_id: The Name(or uuid) of accelerator_request.
        :param filters: dict of filter conditions to push down
        :returns: True if delete succeeded, False otherwise.
        """

        accelerator_request = self.accelerator.get_accelerator_request(
            name_or_id,
            filters
        )
        if accelerator_request is None:
            self.log.debug(
                "accelerator_request %s not found for deleting",
                name_or_id
            )
            return False

        self.accelerator.delete_accelerator_request(name_or_id=name_or_id)

        return True

    def create_accelerator_request(self, attrs):
        """Create an accelerator_request.
        :param attrs: The info of accelerator_request to be created.
        :returns: A ``munch.Munch`` of the created accelerator_request.
        """

        return self.accelerator.create_accelerator_request(**attrs)

    def bind_accelerator_request(self, uuid, properties):
        """Bind an accelerator to VM.
        :param uuid: The uuid of the accelerator_request to be binded.
        :param properties: The info of VM that will bind the accelerator.
        :returns: True if bind succeeded, False otherwise.
        """

        accelerator_request = self.accelerator.get_accelerator_request(uuid)
        if accelerator_request is None:
            self.log.debug(
                "accelerator_request %s not found for unbinding", uuid
            )
            return False

        return self.accelerator.update_accelerator_request(uuid, properties)

    def unbind_accelerator_request(self, uuid, properties):
        """Unbind an accelerator from VM.
        :param uuid: The uuid of the accelerator_request to be unbinded.
        :param properties: The info of VM that will unbind the accelerator.
        :returns:True if unbind succeeded, False otherwise.
        """

        accelerator_request = self.accelerator.get_accelerator_request(uuid)
        if accelerator_request is None:
            self.log.debug(
                "accelerator_request %s not found for unbinding", uuid
            )
            return False

        return self.accelerator.update_accelerator_request(uuid, properties)
