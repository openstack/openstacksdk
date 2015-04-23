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
from openstack.volume.v2 import snapshot
from openstack.volume.v2 import type
from openstack.volume.v2 import volume


class Proxy(proxy.BaseProxy):

    def get_volume(self, **data):
        return volume.Volume(data).get(self.session)

    def delete_snapshot(self, value, ignore_missing=True):
        """Delete a snapshot

        :param value: The value can be either the ID of a snapshot or a
                      :class:`~openstack.volume.v2.snapshot.Snapshot` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the snapshot does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        self._delete(snapshot.Snapshot, value, ignore_missing)

    def delete_type(self, value, ignore_missing=True):
        """Delete a type

        :param value: The value can be either the ID of a type or a
                      :class:`~openstack.volume.v2.type.Type` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the type does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        self._delete(type.Type, value, ignore_missing)

    def delete_volume(self, value, ignore_missing=True):
        """Delete a volume

        :param value: The value can be either the ID of a volume or a
                      :class:`~openstack.volume.v2.volume.Volume` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the volume does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        self._delete(volume.Volume, value, ignore_missing)
