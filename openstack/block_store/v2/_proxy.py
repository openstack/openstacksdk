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

from openstack.block_store.v2 import snapshot
from openstack.block_store.v2 import type
from openstack.block_store.v2 import volume
from openstack import proxy


class Proxy(proxy.BaseProxy):

    def get_snapshot(self, value):
        """Get a single snapshot

        :param value: The value can be the ID of a snapshot or a
                      :class:`~openstack.volume.v2.snapshot.Snapshot` instance.

        :returns: One :class:`~openstack.volume.v2.snapshot.Snapshot`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(snapshot.Snapshot, value)

    def create_snapshot(self, **attrs):
        """Create a new snapshot from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.volume.v2.snapshot.Snapshot`,
                           comprised of the properties on the Snapshot class.

        :returns: The results of snapshot creation
        :rtype: :class:`~openstack.volume.v2.snapshot.Snapshot`
        """
        return self._create(snapshot.Snapshot, **attrs)

    def delete_snapshot(self, value, ignore_missing=True):
        """Delete a snapshot

        :param value: The value can be either the ID of a snapshot or a
                      :class:`~openstack.volume.v2.snapshot.Snapshot` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the snapshot does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent snapshot.

        :returns: ``None``
        """
        self._delete(snapshot.Snapshot, value, ignore_missing=ignore_missing)

    def get_type(self, value):
        """Get a single type

        :param value: The value can be the ID of a type or a
                      :class:`~openstack.volume.v2.type.Type` instance.

        :returns: One :class:`~openstack.volume.v2.type.Type`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(type.Type, value)

    def create_type(self, **attrs):
        """Create a new type from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.volume.v2.type.Type`,
                           comprised of the properties on the Type class.

        :returns: The results of type creation
        :rtype: :class:`~openstack.volume.v2.type.Type`
        """
        return self._create(type.Type, **attrs)

    def delete_type(self, value, ignore_missing=True):
        """Delete a type

        :param value: The value can be either the ID of a type or a
                      :class:`~openstack.volume.v2.type.Type` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the type does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent type.

        :returns: ``None``
        """
        self._delete(type.Type, value, ignore_missing=ignore_missing)

    def get_volume(self, value):
        """Get a single volume

        :param value: The value can be the ID of a volume or a
                      :class:`~openstack.volume.v2.volume.Volume` instance.

        :returns: One :class:`~openstack.volume.v2.volume.Volume`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(volume.Volume, value)

    def create_volume(self, **attrs):
        """Create a new volume from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.volume.v2.volume.Volume`,
                           comprised of the properties on the Volume class.

        :returns: The results of volume creation
        :rtype: :class:`~openstack.volume.v2.volume.Volume`
        """
        return self._create(volume.Volume, **attrs)

    def delete_volume(self, value, ignore_missing=True):
        """Delete a volume

        :param value: The value can be either the ID of a volume or a
                      :class:`~openstack.volume.v2.volume.Volume` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the volume does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent volume.

        :returns: ``None``
        """
        self._delete(volume.Volume, value, ignore_missing=ignore_missing)
