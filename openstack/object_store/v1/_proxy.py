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

from openstack.object_store.v1 import container as _container
from openstack.object_store.v1 import obj as _obj


class Proxy(object):

    def __init__(self, session):
        self.session = session

    def get_account_metadata(self):
        """Get metatdata for this account.

        :rtype:
            :class:`~openstack.object_store.v1.container.Container`
        """
        return _container.Container().head(self.session)

    def set_account_metadata(self, container):
        """Set metatdata for this account.

        :param container: Account metadata specified on a
            :class:`~openstack.object_store.v1.container.Container` object
            to be sent to the server.
        :type container:
            :class:`~openstack.object_store.v1.container.Container`

        :rtype: ``None``
        """
        container.update(self.session)

    def containers(self, limit=None, marker=None, **kwargs):
        """Obtain Container objects for this account.

        :param int limit: Set the limit of how many containers to retrieve
            in each request to the server. By default, the value is ``None``,
            retrieving the maximum amount of containers per request that
            your server allows.
        :param str marker: The name of the container to begin iterating from.
            By default, the value is ``None``, returning all available
            containers.

        :rtype: A generator of
            :class:`~openstack.object_store.v1.container.Container` objects.
        """
        return _container.Container.list(self.session, limit=limit,
                                         marker=marker, **kwargs)

    def get_container_metadata(self, container):
        """Get metatdata for a container.

        :param container: The container to retreive metadata for. You can
            pass a container object or the name of a container to
            retrieve metadata for.
        :type container:
            :class:`~openstack.object_store.v1.container.Container`

        :rtype:
            :class:`~openstack.object_store.v1.container.Container`
        :raises: :exc:`ValueError` when an unnamed container object was
            specified, as this would instead retrieve account metadata.
        """
        container = _container.Container.from_id(container)
        if getattr(container, "name") is None:
            msg = "A named container or a name itself must be passed"
            raise ValueError(msg)

        return container.head(self.session)

    def set_container_metadata(self, container):
        """Set metatdata for a container.

        :param container: A container object containing metadata to be set.
        :type container:
            :class:`~openstack.object_store.v1.container.Container`

        :rtype: ``None``
        """
        container.create(self.session)

    def create_container(self, container):
        """Create a container,

        :param container: The container to create. You can pass a container
            object or the name of a container to create.
        :type container:
            :class:`~openstack.object_store.v1.container.Container`

        :rtype:
            :class:`~openstack.object_store.v1.container.Container`
        """
        container = _container.Container.from_id(container)
        return container.create(self.session)

    def delete_container(self, container):
        """Delete a container.

        :param container: The container to delete. You can pass a container
            object or the name of a container to delete.
        :type container:
            :class:`~openstack.object_store.v1.container.Container`

        :rtype: ``None``
        """
        container = _container.Container.from_id(container)
        container.delete(self.session)

    def objects(self, container, limit=None, marker=None, **kwargs):
        """Return a generator that yields the Container's objects.

        :param container: A container object or the name of a container
            that you want to retrieve objects from.
        :type container:
            :class:`~openstack.object_store.v1.container.Container`

        :rtype: A generator of
            :class:`~openstack.object_store.v1.obj.Object` objects.
        """
        container = _container.Container.from_id(container)

        objs = _obj.Object.list(self.session, limit=limit, marker=marker,
                                path_args={"container": container.name},
                                **kwargs)
        # TODO(briancurtin): Objects have to know their container at this
        # point, otherwise further operations like getting their metadata
        # or downloading them is a hassle because the end-user would have
        # to maintain both the container and the object separately.
        for ob in objs:
            ob.container = container.name
            yield ob

    def get_object_data(self, obj):
        """Retreive the data contained inside an object.

        :param obj: The object to retreive.
        :type obj: :class:`~openstack.object_store.v1.obj.Object`
        """
        return obj.get(self.session)

    def save_object(self, obj, path):
        """Save the data contained inside an object to disk.

        :param obj: The object to save to disk.
        :type obj: :class:`~openstack.object_store.v1.obj.Object`
        :param path str: Location to write the object contents.
        """
        with open(path, "w") as out:
            out.write(self.get_object_data(obj))

    def create_object(self, data, obj, container=None, **kwargs):
        """Create an object within the object store.

        :param data: The data to store.
        :param obj: The name of the object to create, or an obj.Object
        :type obj: :class:`~openstack.object_store.v1.obj.Object`
        """
        obj = _obj.Object.from_id(obj)

        # If we were given an Object complete with an underlying Container,
        # this attribute access will succeed. Otherwise we'll need to set
        # a container value on `obj` out of the `container` value.
        name = getattr(obj, "container")
        if not name:
            cnt = _container.Container.from_id(container)
            obj.container = cnt.name

        return obj.create(self.session, data)

    def copy_object(self):
        """Copy an object."""
        raise NotImplementedError

    def delete_object(self, obj):
        """Delete an object.

        :param obj: The object to delete.
        :type obj: :class:`~openstack.object_store.v1.obj.Object`

        :rtype: ``None``
        """
        obj.delete(self.session)

    def get_object_metadata(self, obj):
        """Get metatdata for an object.

        :param obj: The object to retreive metadata from.
        :type obj: :class:`~openstack.object_store.v1.obj.Object`

        :return: A :class:`~openstack.object_store.v1.obj.Object`
            populated with the server's response.
        """
        return obj.head(self.session)

    def set_object_metadata(self, obj):
        """Set metatdata for an object.

        :param obj: The object to set metadata for.
        :type obj: :class:`~openstack.object_store.v1.obj.Object`

        :rtype: ``None``
        """
        obj.create(self.session)
