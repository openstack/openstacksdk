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

from collections.abc import Callable, Generator
from typing import Any, ClassVar, Literal
import warnings

from openstack.accelerator.v2 import accelerator_request as _arq
from openstack.accelerator.v2 import attribute as _attribute
from openstack.accelerator.v2 import deployable as _deployable
from openstack.accelerator.v2 import device as _device
from openstack.accelerator.v2 import device_profile as _device_profile
from openstack import proxy
from openstack import resource
from openstack import warnings as os_warnings


class Proxy(proxy.Proxy):
    api_version: ClassVar[Literal['2']] = '2'

    # ========== Deployables ==========

    def deployables(
        self,
        **query: Any,
    ) -> Generator[_deployable.Deployable, None, None]:
        """Retrieve a generator of deployables.

        :param query: Optional query parameters to be sent to
            restrict the deployables to be returned.
        :returns: A generator of deployable instances.
        """
        return self._list(_deployable.Deployable, **query)

    def get_deployable(
        self,
        deployable: str | _deployable.Deployable,
        fields: list[str] | None = None,
    ) -> _deployable.Deployable:
        """Get a single deployable.

        :param deployable: The value can be the ID of a deployable or a
            ::class:`~openstack.accelerator.v2.deployable.Deployable` instance.
        :returns: One :class:`~openstack.accelerator.v2.deployable.Deployable`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            deployable matching the criteria could be found.
        """
        if fields is not None:
            warnings.warn(
                'The fields argument is a no-op and will be removed in a '
                'future release',
                os_warnings.RemovedInSDK50Warning,
            )

        return self._get(_deployable.Deployable, deployable)

    # TODO(stephenfin): Rename to patch_deployable
    def update_deployable(
        self,
        uuid: str | _deployable.Deployable,
        patch: list[dict[str, Any]],
    ) -> _deployable.Deployable:
        """Reconfig the FPGA with new bitstream.

        :param uuid: The value can be the UUID of a deployable
        :param patch: The information to reconfig.
        :returns: The results of FPGA reconfig.
        """
        return self._get_resource(_deployable.Deployable, uuid).patch(
            self, patch
        )

    # ========== Devices ==========

    def devices(self, **query: Any) -> Generator[_device.Device, None, None]:
        """Retrieve a generator of devices.

        :param query: Optional query parameters to be sent to
            restrict the devices to be returned. Available parameters include:

            * hostname: The hostname of the device.
            * type: The type of the device.
            * vendor: The vendor ID of the device.
            * sort: A list of sorting keys separated by commas. Each sorting
              key can optionally be attached with a sorting direction
              modifier which can be ``asc`` or ``desc``.
            * limit: Requests a specified size of returned items from the
              query. Returns a number of items up to the specified limit
              value.
            * marker: Specifies the ID of the last-seen item. Use the limit
              parameter to make an initial limited request and use the ID of
              the last-seen item from the response as the marker parameter
              value in a subsequent limited request.
        :returns: A generator of device instances.
        """
        return self._list(_device.Device, **query)

    def get_device(
        self, device: str | _device.Device, fields: list[str] | None = None
    ) -> _device.Device:
        """Get a single device.

        :param device: The value can be the ID of a device or a
            :class:`~openstack.accelerator.v2.device.Device` instance.
        :returns: One :class:`~openstack.accelerator.v2.device.Device`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            device matching the criteria could be found.
        """
        if fields is not None:
            warnings.warn(
                'The fields argument is a no-op and will be removed in a '
                'future release',
                os_warnings.RemovedInSDK50Warning,
            )

        return self._get(_device.Device, device)

    # ========== Device profiles ==========

    def device_profiles(
        self,
        **query: Any,
    ) -> Generator[_device_profile.DeviceProfile, None, None]:
        """Retrieve a generator of device profiles.

        :param query: Optional query parameters to be sent to
            restrict the device profiles to be returned.
        :returns: A generator of device profile instances.
        """
        return self._list(_device_profile.DeviceProfile, **query)

    def create_device_profile(
        self, **attrs: Any
    ) -> _device_profile.DeviceProfile:
        """Create a device_profile.

        :param kwargs attrs: a list of device_profiles.
        :returns: The list of created device profiles
        """
        return self._create(_device_profile.DeviceProfile, **attrs)

    # TODO(stephenfin): This method should return None
    def delete_device_profile(
        self,
        device_profile: str | _device_profile.DeviceProfile,
        ignore_missing: bool = True,
    ) -> _device_profile.DeviceProfile | None:
        """Delete a device profile

        :param device_profile: The value can be either the ID of a device
            profile or a
            :class:`~openstack.accelerator.v2.device_profile.DeviceProfile`
            instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the device profile does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent device profile.
        :returns: The deleted device profile.
        """
        return self._delete(
            _device_profile.DeviceProfile,
            device_profile,
            ignore_missing=ignore_missing,
        )

    def get_device_profile(
        self,
        device_profile: str | _device_profile.DeviceProfile,
        fields: list[str] | None = None,
    ) -> _device_profile.DeviceProfile:
        """Get a single device profile.

        :param device_profile: The value can be the ID of a device profile or a
            `~openstack.accelerator.v2.device_profile.DeviceProfile` instance.
        :returns: One :class:
            `~openstack.accelerator.v2.device_profile.DeviceProfile`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            device profile matching the criteria could be found.
        """
        if fields is not None:
            warnings.warn(
                'The fields argument is a no-op and will be removed in a '
                'future release',
                os_warnings.RemovedInSDK50Warning,
            )

        return self._get(_device_profile.DeviceProfile, device_profile)

    # ========== Accelerator requests ==========

    def accelerator_requests(
        self,
        **query: Any,
    ) -> Generator[_arq.AcceleratorRequest, None, None]:
        """Retrieve a generator of accelerator requests.

        :param query: Optional query parameters to be sent to
            restrict the accelerator requests to be returned.
        :returns: A generator of accelerator request instances.
        """
        return self._list(_arq.AcceleratorRequest, **query)

    def create_accelerator_request(
        self, **attrs: Any
    ) -> _arq.AcceleratorRequest:
        """Create an ARQs for a single device profile.

        :param kwargs attrs: request body.
        :returns: The created accelerator request instance.
        """
        return self._create(_arq.AcceleratorRequest, **attrs)

    def delete_accelerator_request(
        self,
        accelerator_request: str | _arq.AcceleratorRequest,
        ignore_missing: bool = True,
    ) -> None:
        """Delete an accelerator request

        :param accelerator_request: The value can be either the ID of an
            accelerator request or a
            :class:`~openstack.accelerator.v2.accelerator_request.AcceleratorRequest`
            instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the accelerator request does not exist. When set to ``True``,
            no exception will be set when attempting to delete a nonexistent
            accelerator request.
        :returns: ``None``
        """
        self._delete(
            _arq.AcceleratorRequest,
            accelerator_request,
            ignore_missing=ignore_missing,
        )

    def get_accelerator_request(
        self,
        accelerator_request: str | _arq.AcceleratorRequest,
        fields: list[str] | None = None,
    ) -> _arq.AcceleratorRequest:
        """Get a single accelerator request.

        :param accelerator_request: The value can be the ID of a accelerator
            request or a
            `~openstack.accelerator.v2.accelerator_request.AcceleratorRequest`
            instance.
        :returns: One :class:
            `~openstack.accelerator.v2.accelerator_request.AcceleratorRequest`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            accelerator request matching the criteria could be found.
        """
        if fields is not None:
            warnings.warn(
                'The fields argument is a no-op and will be removed in a '
                'future release',
                os_warnings.RemovedInSDK50Warning,
            )

        return self._get(_arq.AcceleratorRequest, accelerator_request)

    # TODO(stephenfin): Rename to patch_accelerator_request
    def update_accelerator_request(
        self,
        uuid: str | _arq.AcceleratorRequest,
        properties: list[dict[str, Any]],
    ) -> _arq.AcceleratorRequest:
        """Bind/Unbind an accelerator to VM.

        :param uuid: The uuid of the accelerator_request to be bound/unbound.
        :param properties: The info of VM
            that will bind/unbind the accelerator.
        :returns: True if bind/unbind succeeded, False otherwise.
        """
        return self._get_resource(_arq.AcceleratorRequest, uuid).patch(
            self, properties
        )

    # ========== Attributes ==========

    def attributes(
        self,
        **query: Any,
    ) -> Generator[_attribute.Attribute, None, None]:
        """Retrieve a generator of attributes.

        :param query: Optional query parameters to be sent to
            restrict the attributes to be returned.
        :returns: A generator of attribute instances.
        """
        return self._list(_attribute.Attribute, **query)

    def create_attribute(self, **attrs: Any) -> _attribute.Attribute:
        """Create a attribute.

        :param kwargs attrs: a list of attributes.
        :returns: The list of created attributes
        """
        return self._create(_attribute.Attribute, **attrs)

    # TODO(stephenfin): This method should return None
    def delete_attribute(
        self,
        attribute: str | _attribute.Attribute,
        ignore_missing: bool = True,
    ) -> _attribute.Attribute | None:
        """Delete a attribute

        :param attribute: The value can be either the ID of a attributes or a
            :class:`~openstack.accelerator.v2.attribute.Attributes`
            instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the device profile does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent device profile.
        :returns: The deleted attribute.
        """
        return self._delete(
            _attribute.Attribute,
            attribute,
            ignore_missing=ignore_missing,
        )

    def get_attribute(
        self,
        attribute: str | _attribute.Attribute,
        fields: list[str] | None = None,
    ) -> _attribute.Attribute:
        """Get a single device profile.

        :param attribute: The value can be the ID of a attribute or a.
            `~openstack.accelerator.v2.attribute.Attribute` instance.
        :returns: One :class:
            `~openstack.accelerator.v2.attribute.Attribute`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            device profile matching the criteria could be found.
        """
        if fields is not None:
            warnings.warn(
                'The fields argument is a no-op and will be removed in a '
                'future release',
                os_warnings.RemovedInSDK50Warning,
            )

        return self._get(_attribute.Attribute, attribute)

    # ========== Utilities ==========

    def wait_for_status(
        self,
        res: resource.ResourceT,
        status: str,
        failures: list[str] | None = None,
        interval: int | float | None = 2,
        wait: int | None = None,
        attribute: str = 'status',
        callback: Callable[[int], None] | None = None,
    ) -> resource.ResourceT:
        """Wait for the resource to be in a particular status.

        :param session: The session to use for making this request.
        :param resource: The resource to wait on to reach the status. The
            resource must have a status attribute specified via ``attribute``.
        :param status: Desired status of the resource.
        :param failures: Statuses that would indicate the transition
            failed such as 'ERROR'. Defaults to ['ERROR'].
        :param interval: Number of seconds to wait between checks.
        :param wait: Maximum number of seconds to wait for transition.
            Set to ``None`` to wait forever.
        :param attribute: Name of the resource attribute that contains the
            status.
        :param callback: A callback function. This will be called with a single
            value, progress. This is API specific but is generally a percentage
            value from 0-100.

        :return: The updated resource.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if the
            transition to status failed to occur in ``wait`` seconds.
        :raises: :class:`~openstack.exceptions.ResourceFailure` if the resource
            transitioned to one of the states in ``failures``.
        :raises: :class:`~AttributeError` if the resource does not have a
            ``status`` attribute
        """
        return resource.wait_for_status(
            self, res, status, failures, interval, wait, attribute, callback
        )

    def wait_for_delete(
        self,
        res: resource.ResourceT,
        interval: int | float | None = 2,
        wait: int | None = 120,
        callback: Callable[[int], None] | None = None,
    ) -> resource.ResourceT:
        """Wait for a resource to be deleted.

        :param res: The resource to wait on to be deleted.
        :param interval: Number of seconds to wait before to consecutive
            checks.
        :param wait: Maximum number of seconds to wait before the change.
        :param callback: A callback function. This will be called with a single
            value, progress, which is a percentage value from 0-100.

        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
            to delete failed to occur in the specified seconds.
        """
        return resource.wait_for_delete(self, res, interval, wait, callback)
