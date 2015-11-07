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
        """Get metatdata for this account

        :rtype:
            :class:`~openstack.object_store.v1.account.Account`
        """
        return self._head(_account.Account)

    def set_account_metadata(self, account):
        """Set metatdata for this account.

        :param account: Account metadata specified on a
            :class:`~openstack.object_store.v1.account.Account` object
            to be sent to the server.
        :type account:
            :class:`~openstack.object_store.v1.account.Account`

        :rtype: ``None``
        """
        account.update(self.session)

    def containers(self, **query):
        """Obtain Container objects for this account.

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :rtype: A generator of
            :class:`~openstack.object_store.v1.container.Container` objects.
        """
        return _container.Container.list(self.session, **query)

    def get_container_metadata(self, value):
        """Get metatdata for a container

        :param value: The value can be the name of a container or a
               :class:`~openstack.object_store.v1.container.Container`
               instance.

        :returns: One :class:`~openstack.object_store.v1.container.Container`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._head(_container.Container, value)

    def set_container_metadata(self, container):
        """Set metatdata for a container.

        :param container: A container object containing metadata to be set.
        :type container:
            :class:`~openstack.object_store.v1.container.Container`

        :rtype: ``None``
        """
        container.create(self.session)

    def create_container(self, **attrs):
        """Create a new container from attributes

        :param dict attrs: Keyword arguments which will be used to create
               a :class:`~openstack.object_store.v1.container.Container`,
               comprised of the properties on the Container class.

        :returns: The results of container creation
        :rtype: :class:`~openstack.object_store.v1.container.Container`
        """
        # TODO(brian): s/_container/container once other changes propogate
        return self._create(_container.Container, **attrs)

    def delete_container(self, value, ignore_missing=True):
        """Delete a container

        :param value: The value can be either the name of a container or a
                      :class:`~openstack.object_store.v1.container.Container`
                      instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the container does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        # TODO(brian): s/_container/container once other changes propogate
        self._delete(_container.Container, value,
                     ignore_missing=ignore_missing)

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
        # TODO(briancurtin): Objects have to know their container at this
        # point, otherwise further operations like getting their metadata
        # or downloading them is a hassle because the end-user would have
        # to maintain both the container and the object separately.
        for ob in objs:
            ob.container = container.name
            yield ob

    def _get_container_name(self, value, container):
        if isinstance(value, _obj.Object):
            if value.container is not None:
                return value.container
        if container is not None:
            container = _container.Container.from_id(container)
            return container.name

        raise ValueError("container must be specified")

    def get_object(self, value, container=None):
        """Get the data associated with an object

        :param value: The value can be the ID of an object or a
                      :class:`~openstack.object_store.v1.obj.Object` instance.
        :param container: The value can be the ID of a container or a
               :class:`~openstack.object_store.v1.container.Container`
               instance.

        :returns: The contents of the object.  Use the
                  :func:`~get_object_metadata`
                  method if you want an object resource.
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        container_name = self._get_container_name(value, container)

        # TODO(brian): s/_obj/obj once other changes propogate
        return self._get(_obj.Object, value,
                         path_args={"container": container_name})

    def download_object(self, obj, path):
        """Download the data contained inside an object to disk.

        :param obj: The object to save to disk.
        :type obj: :class:`~openstack.object_store.v1.obj.Object`
        :param path str: Location to write the object contents.
        """
        with open(path, "w") as out:
            out.write(self.get_object(obj))

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

        # TODO(brian): s/_container/container once other changes propogate
        return self._create(_obj.Object,
                            path_args={"container": container_name}, **attrs)

    def copy_object(self):
        """Copy an object."""
        raise NotImplementedError

    def delete_object(self, value, ignore_missing=True, container=None):
        """Delete an object

        :param value: The value can be either the name of an object or a
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
        container_name = self._get_container_name(value, container)

        # TODO(brian): s/_obj/obj once other changes propogate
        self._delete(_obj.Object, value, ignore_missing=ignore_missing,
                     path_args={"container": container_name})

    def get_object_metadata(self, value, container=None):
        """Get metatdata for an object

        :param value: The value is an
               :class:`~openstack.object_store.v1.obj.Object`
               instance.
        :param container: The value can be the ID of a container or a
               :class:`~openstack.object_store.v1.container.Container`
               instance.

        :returns: One :class:`~openstack.object_store.v1.obj.Object`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        container_name = self._get_container_name(value, container)

        return self._head(_obj.Object, value,
                          path_args={"container": container_name})

    def set_object_metadata(self, obj):
        """Set metatdata for an object.

        :param obj: The object to set metadata for.
        :type obj: :class:`~openstack.object_store.v1.obj.Object`

        :rtype: ``None``
        """
        obj.create(self.session)
