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

from collections.abc import Mapping
from typing import Any
import warnings

from openstack.accelerator.v2 import accelerator_request as _arq
from openstack.accelerator.v2 import deployable as _deployable
from openstack.accelerator.v2 import device as _device
from openstack.accelerator.v2 import device_profile as _device_profile
from openstack.cloud import openstackcloud
from openstack import warnings as os_warnings


class AcceleratorCloudMixin(openstackcloud._OpenStackCloudMixin):
    def list_deployables(
        self, filters: dict[str, Any] | None = None
    ) -> list[_deployable.Deployable]:
        """List all available deployables.

        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of accelerator ``Deployable`` objects.
        """
        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}
        return list(self.accelerator.deployables(**filters))

    def list_devices(
        self, filters: dict[str, Any] | None = None
    ) -> list[_device.Device]:
        """List all devices.

        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of accelerator ``Device`` objects.
        """
        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}
        return list(self.accelerator.devices(**filters))

    def list_device_profiles(
        self, filters: dict[str, Any] | None = None
    ) -> list[_device_profile.DeviceProfile]:
        """List all device_profiles.

        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of accelerator ``DeviceProfile`` objects.
        """
        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}
        return list(self.accelerator.device_profiles(**filters))

    def create_device_profile(
        self, attrs: Mapping[str, Any]
    ) -> _device_profile.DeviceProfile:
        """Create a device_profile.

        :param attrs: The info of device_profile to be created.
        :returns: An accelerator ``DeviceProfile`` objects.
        """
        return self.accelerator.create_device_profile(**attrs)

    def delete_device_profile(self, uuid: str, filters: Any = None) -> bool:
        """Delete a device_profile.

        :param uuid: The UUID of the device profile to be deleted.
        :param filters: dict of filter conditions to push down
        :returns: True if delete succeeded, False otherwise.
        """
        if filters is not None:
            warnings.warn(
                'The fields argument is a no-op and will be removed in a '
                'future release',
                os_warnings.RemovedInSDK50Warning,
            )

        self.accelerator.delete_device_profile(uuid)
        return True

    def list_accelerator_requests(
        self, filters: dict[str, Any] | None = None
    ) -> list[_arq.AcceleratorRequest]:
        """List all accelerator_requests.

        :param filters: (optional) dict of filter conditions to push down
        :returns: A list of accelerator ``AcceleratorRequest`` objects.
        """
        # Translate None from search interface to empty {} for kwargs below
        if not filters:
            filters = {}
        return list(self.accelerator.accelerator_requests(**filters))

    def delete_accelerator_request(
        self, uuid: str, filters: Any = None
    ) -> bool:
        """Delete a accelerator_request.

        :param uuid: The UUID of the accelerator request to be deleted.
        :param filters: dict of filter conditions to push down
        :returns: True if delete succeeded, False otherwise.
        """
        if filters is not None:
            warnings.warn(
                'The fields argument is a no-op and will be removed in a '
                'future release',
                os_warnings.RemovedInSDK50Warning,
            )

        self.accelerator.delete_accelerator_request(
            accelerator_request=uuid,
        )
        return True

    def create_accelerator_request(
        self, attrs: Mapping[str, Any]
    ) -> _arq.AcceleratorRequest:
        """Create an accelerator_request.

        :param attrs: The info of accelerator_request to be created.
        :returns: An accelerator ``AcceleratorRequest`` object.
        """
        return self.accelerator.create_accelerator_request(**attrs)

    def patch_accelerator_request(
        self, uuid: str, patch: list[dict[str, Any]]
    ) -> _arq.AcceleratorRequest:
        """Update an accelerator request.

        :param uuid: The UUID of the accelerator request to be updated.
        :param patch: The that will bind the accelerator.
        :returns: True if bind succeeded, False otherwise.
        """
        return self.accelerator.patch_accelerator_request(uuid, patch)

    def bind_accelerator_request(
        self, uuid: str, properties: list[dict[str, Any]]
    ) -> _arq.AcceleratorRequest:
        """Bind an accelerator to VM.

        A deprecated alias for `patch_accelerator_request`.
        """
        return self.patch_accelerator_request(uuid, properties)

    def unbind_accelerator_request(
        self, uuid: str, properties: list[dict[str, Any]]
    ) -> _arq.AcceleratorRequest:
        """Unbind an accelerator from VM.

        A deprecated alias for `patch_accelerator_request`.
        """
        return self.patch_accelerator_request(uuid, properties)
