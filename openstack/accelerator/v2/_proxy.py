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
from openstack import proxy
from openstack.accelerator.v2 import deployable as _deployable
from openstack.accelerator.v2 import device as _device
from openstack.accelerator.v2 import device_profile as _device_profile
from openstack.accelerator.v2 import accelerator_request as _arq


class Proxy(proxy.Proxy):

    def deployables(self, **query):
        """Retrieve a generator of deployables.

        :param kwargs query: Optional query parameters to be sent to
            restrict the deployables to be returned.
        :returns: A generator of deployable instances.
        """
        return self._list(_deployable.Deployable, **query)

    def get_deployable(self, uuid, fields=None):
        """Get a single deployable.

        :param uuid: The value can be the UUID of a deployable.
        :returns: One :class:`~openstack.accelerator.v2.deployable.Deployable`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            deployable matching the criteria could be found.
        """
        return self._get(_deployable.Deployable, uuid)

    def update_deployable(self, uuid, patch):
        """Reconfig the FPGA with new bitstream.

        :param uuid: The value can be the UUID of a deployable
        :param patch: The information to reconfig.
        :returns: The results of FPGA reconfig.
        """
        return self._get_resource(_deployable.Deployable,
                                  uuid).patch(self, patch)

    def devices(self, **query):
        """Retrieve a generator of devices.

        :param kwargs query: Optional query parameters to be sent to
            restrict the devices to be returned. Available parameters include:
            * hostname: The hostname of the device.
            * type: The type of the device.
            * vendor: The vendor ID of the device.
            * sort: A list of sorting keys separated by commas. Each sorting
            key can optionally be attached with a sorting direction
            modifier which can be ``asc`` or ``desc``.
            * limit: Requests a specified size of returned items from the
            query.  Returns a number of items up to the specified limit
            value.
            * marker: Specifies the ID of the last-seen item. Use the limit
            parameter to make an initial limited request and use the ID of
            the last-seen item from the response as the marker parameter
            value in a subsequent limited request.
        :returns: A generator of device instances.
        """
        return self._list(_device.Device, **query)

    def get_device(self, uuid, fields=None):
        """Get a single device.

        :param uuid: The value can be the UUID of a device.
        :returns: One :class:`~openstack.accelerator.v2.device.Device`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            device matching the criteria could be found.
        """
        return self._get(_device.Device, uuid)

    def device_profiles(self, **query):
        """Retrieve a generator of device profiles.

        :param kwargs query: Optional query parameters to be sent to
            restrict the device profiles to be returned.
        :returns: A generator of device profile instances.
        """
        return self._list(_device_profile.DeviceProfile, **query)

    def create_device_profile(self, **attrs):
        """Create a device_profile.

        :param kwargs attrs: a list of device_profiles.
        :returns: The list of created device profiles
        """
        return self._create(_device_profile.DeviceProfile, **attrs)

    def delete_device_profile(self, name_or_id, ignore_missing=True):
        """Delete a device profile

        :param name_or_id: The value can be either the ID or name of
            a device profile.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the device profile does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent device profile.
        :returns: ``None``
        """
        return self._delete(_device_profile.DeviceProfile,
                            name_or_id, ignore_missing=ignore_missing)

    def get_device_profile(self, uuid, fields=None):
        """Get a single device profile.

        :param uuid: The value can be the UUID of a device profile.
        :returns: One :class:
            `~openstack.accelerator.v2.device_profile.DeviceProfile`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            device profile matching the criteria could be found.
        """
        return self._get(_device_profile.DeviceProfile, uuid)

    def accelerator_requests(self, **query):
        """Retrieve a generator of accelerator requests.

        :param kwargs query: Optional query parameters to be sent to
            restrict the accelerator requests to be returned.
        :returns: A generator of accelerator request instances.
        """
        return self._list(_arq.AcceleratorRequest, **query)

    def create_accelerator_request(self, **attrs):
        """Create an ARQs for a single device profile.

        :param kwargs attrs: request body.
        :returns: The created accelerator request instance.
        """
        return self._create(_arq.AcceleratorRequest, **attrs)

    def delete_accelerator_request(self, name_or_id, ignore_missing=True):
        """Delete a device profile
        :param name_or_id: The value can be either the ID or name of
        an accelerator request.
        :param bool ignore_missing: When set to ``False``
        :class:`~openstack.exceptions.ResourceNotFound` will be
        raised when the device profile does not exist.
        When set to ``True``, no exception will be set when
        attempting to delete a nonexistent accelerator request.
        :returns: ``None``
        """
        return self._delete(_arq.AcceleratorRequest, name_or_id,
                            ignore_missing=ignore_missing)

    def get_accelerator_request(self, uuid, fields=None):
        """Get a single accelerator request.
        :param uuid: The value can be the UUID of a accelerator request.
        :returns: One :class:
        `~openstack.accelerator.v2.accelerator_request.AcceleratorRequest`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
        accelerator request matching the criteria could be found.
        """
        return self._get(_arq.AcceleratorRequest, uuid)

    def update_accelerator_request(self, uuid, properties):
        """Bind/Unbind an accelerator to VM.
        :param uuid: The uuid of the accelerator_request to be bound/unbound.
        :param properties: The info of VM
        that will bind/unbind the accelerator.
        :returns: True if bind/unbind succeeded, False otherwise.
        """
        return self._get_resource(_arq.AcceleratorRequest,
                                  uuid).patch(self, properties)
