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

from openstack.object_store.v1 import account as _account
from openstack.object_store.v1 import container as _container
from openstack.object_store.v1 import obj as _obj
from openstack import proxy


class Proxy(proxy.BaseProxy):

    def get_account_metadata(self):
        """Get metadata for this account.

        :rtype:
            :class:`~openstack.object_store.v1.account.Account`
        """
        return self._head(_account.Account)

    def set_account_metadata(self, **metadata):
        """Set metadata for this account.

        :param kwargs metadata: Key/value pairs to be set as metadata
                                on the container. Custom  metadata can be set.
                                Custom metadata are keys and values defined
                                by the user.
        """
        account = self._get_resource(_account.Account, None)
        account.set_metadata(self.session, metadata)

    def delete_account_metadata(self, keys):
        """Delete metadata for this account.

        :param list keys: The keys of metadata to be deleted.
        """
        account = self._get_resource(_account.Account, None)
        account.delete_metadata(self.session, keys)

    def containers(self, **query):
        """Obtain Container objects for this account.

        :param kwargs query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :rtype: A generator of
            :class:`~openstack.object_store.v1.container.Container` objects.
        """
        return _container.Container.list(self.session, **query)

    def create_container(self, **attrs):
        """Create a new container from attributes

        :param dict attrs: Keyword arguments which will be used to create
               a :class:`~openstack.object_store.v1.container.Container`,
               comprised of the properties on the Container class.

        :returns: The results of container creation
        :rtype: :class:`~openstack.object_store.v1.container.Container`
        """
        return self._create(_container.Container, **attrs)

    def delete_container(self, container, ignore_missing=True):
        """Delete a container

        :param container: The value can be either the name of a container or a
                      :class:`~openstack.object_store.v1.container.Container`
                      instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the container does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        self._delete(_container.Container, container,
                     ignore_missing=ignore_missing)

    def get_container_metadata(self, container):
        """Get metadata for a container

        :param container: The value can be the name of a container or a
               :class:`~openstack.object_store.v1.container.Container`
               instance.

        :returns: One :class:`~openstack.object_store.v1.container.Container`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._head(_container.Container, container)

    def set_container_metadata(self, container, **metadata):
        """Set metadata for a container.

        :param container: The value can be the name of a container or a
               :class:`~openstack.object_store.v1.container.Container`
               instance.
        :param kwargs metadata: Key/value pairs to be set as metadata
                                on the container. Both custom and system
                                metadata can be set. Custom metadata are keys
                                and values defined by the user. System
                                metadata are keys defined by the Object Store
                                and values defined by the user. The system
                                metadata keys are:

                                - `content_type`
                                - `is_content_type_detected`
                                - `versions_location`
                                - `read_ACL`
                                - `write_ACL`
                                - `sync_to`
                                - `sync_key`
        """
        res = self._get_resource(_container.Container, container)
        res.set_metadata(self.session, metadata)

    def delete_container_metadata(self, container, keys):
        """Delete metadata for a container.

        :param container: The value can be the ID of a container or a
               :class:`~openstack.object_store.v1.container.Container`
               instance.
        :param list keys: The keys of metadata to be deleted.
        """
        res = self._get_resource(_container.Container, container)
        res.delete_metadata(self.session, keys)

    def objects(self, container, **query):
        """Return a generator that yields the Container's objects.

        :param container: A container object or the name of a container
            that you want to retrieve objects from.
        :type container:
            :class:`~openstack.object_store.v1.container.Container`
        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :rtype: A generator of
            :class:`~openstack.object_store.v1.obj.Object` objects.
        """
        container = _container.Container.from_id(container)

        objs = _obj.Object.list(self.session,
                                path_args={"container": container.name},
                                **query)
        for obj in objs:
            obj.container = container.name
            yield obj

    def _get_container_name(self, obj, container):
        if isinstance(obj, _obj.Object):
            if obj.container is not None:
                return obj.container
        if container is not None:
            container = _container.Container.from_id(container)
            return container.name

        raise ValueError("container must be specified")

    def get_object(self, obj, container=None):
        """Get the data associated with an object

        :param obj: The value can be the name of an object or a
                       :class:`~openstack.object_store.v1.obj.Object` instance.
        :param container: The value can be the name of a container or a
               :class:`~openstack.object_store.v1.container.Container`
               instance.

        :returns: The contents of the object.  Use the
                  :func:`~get_object_metadata`
                  method if you want an object resource.
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        container_name = self._get_container_name(obj, container)

        return self._get(_obj.Object, obj,
                         path_args={"container": container_name})

    def download_object(self, obj, container=None, path=None):
        """Download the data contained inside an object to disk.

        :param obj: The value can be the name of an object or a
                       :class:`~openstack.object_store.v1.obj.Object` instance.
        :param container: The value can be the name of a container or a
               :class:`~openstack.object_store.v1.container.Container`
               instance.
        :param path str: Location to write the object contents.

        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        with open(path, "w") as out:
            out.write(self.get_object(obj, container))

    def upload_object(self, **attrs):
        """Upload a new object from attributes

        :param dict attrs: Keyword arguments which will be used to create
               a :class:`~openstack.object_store.v1.obj.Object`,
               comprised of the properties on the Object class.
               **Required**: A `container` argument must be specified,
               which is either the ID of a container or a
               :class:`~openstack.object_store.v1.container.Container`
               instance.

        :returns: The results of object creation
        :rtype: :class:`~openstack.object_store.v1.container.Container`
        """
        container = attrs.pop("container", None)
        container_name = self._get_container_name(None, container)

        return self._create(_obj.Object,
                            path_args={"container": container_name}, **attrs)

    def copy_object(self):
        """Copy an object."""
        raise NotImplementedError

    def delete_object(self, obj, ignore_missing=True, container=None):
        """Delete an object

        :param obj: The value can be either the name of an object or a
                       :class:`~openstack.object_store.v1.container.Container`
                       instance.
        :param container: The value can be the ID of a container or a
               :class:`~openstack.object_store.v1.container.Container`
               instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the object does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        container_name = self._get_container_name(obj, container)

        self._delete(_obj.Object, obj, ignore_missing=ignore_missing,
                     path_args={"container": container_name})

    def get_object_metadata(self, obj, container=None):
        """Get metadata for an object.

        :param obj: The value can be the name of an object or a
                    :class:`~openstack.object_store.v1.obj.Object` instance.
        :param container: The value can be the ID of a container or a
               :class:`~openstack.object_store.v1.container.Container`
               instance.

        :returns: One :class:`~openstack.object_store.v1.obj.Object`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        container_name = self._get_container_name(obj, container)

        return self._head(_obj.Object, obj,
                          path_args={"container": container_name})

    def set_object_metadata(self, obj, container=None, **metadata):
        """Set metadata for an object.

        Note: This method will do an extra HEAD call.

        :param obj: The value can be the name of an object or a
                    :class:`~openstack.object_store.v1.obj.Object` instance.
        :param container: The value can be the name of a container or a
               :class:`~openstack.object_store.v1.container.Container`
               instance.
        :param kwargs metadata: Key/value pairs to be set as metadata
                                on the container. Both custom and system
                                metadata can be set. Custom metadata are keys
                                and values defined by the user. System
                                metadata are keys defined by the Object Store
                                and values defined by the user. The system
                                metadata keys are:

                                - `content_type`
                                - `content_encoding`
                                - `content_disposition`
                                - `delete_after`
                                - `delete_at`
                                - `is_content_type_detected`
        """
        container_name = self._get_container_name(obj, container)
        res = self._get_resource(_obj.Object, obj,
                                 path_args={"container": container_name})
        res.set_metadata(self.session, metadata)

    def delete_object_metadata(self, obj, container=None, keys=None):
        """Delete metadata for an object.

        :param obj: The value can be the name of an object or a
                    :class:`~openstack.object_store.v1.obj.Object` instance.
        :param container: The value can be the ID of a container or a
               :class:`~openstack.object_store.v1.container.Container`
               instance.
        :param list keys: The keys of metadata to be deleted.
        """
        container_name = self._get_container_name(obj, container)
        res = self._get_resource(_obj.Object, obj,
                                 path_args={"container": container_name})
        res.delete_metadata(self.session, keys)
