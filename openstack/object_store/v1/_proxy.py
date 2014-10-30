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

    def get_account_metadata(self, container=None):
        """Get metatdata for this account.

        :param container: The container to retreive metadata for.
        :type container:
            :class:`~openstack.object_store.v1.container.Container`
        """
        # TODO(briancurtin): should just use Container.head directly?
        if container is None:
            container = _container.Container()
        container.head(self.session)
        return container

    def set_account_metadata(self, container):
        """Set metatdata for this account.

        :param container: The container to set metadata for.
        :type container:
            :class:`~openstack.object_store.v1.container.Container`
        """
        container.update(self.session)
        return container

    def containers(self, limit=None, marker=None, **kwargs):
        """Return a generator that yields the account's Container objects.

        :param int limit: Set the limit of how many containers to retrieve.
        :param str marker: The name of the container to begin iterating from.
        """
        return _container.Container.list(self.session, limit=limit,
                                         marker=marker, **kwargs)

    def get_container_metadata(self, container):
        """Get metatdata for a container.

        :param container: The container to retreive metadata for.
        :type container:
            :class:`~openstack.object_store.v1.container.Container`
        """
        container = _container.Container.from_id(container)
        # TODO(briancurtin): may want to check if the container has a
        # name at this point. If it doesn't, this call will work but it's
        # actually getting *account* metadata.
        container.head(self.session)
        return container

    def set_container_metadata(self, container):
        """Set metatdata for a container.

        :param container: The container to set metadata for.
        :type container:
            :class:`~openstack.object_store.v1.container.Container`
        """
        container.create(self.session)
        return container

    def create_container(self, container):
        """Create a container,

        :param container: A container name or object.
        :type container:
            :class:`~openstack.object_store.v1.container.Container`
        """
        container = _container.Container.from_id(container)
        container.create(self.session)
        return container

    def delete_container(self, container):
        """Delete a container.

        :param container: A container name or object.
        :type container:
            :class:`~openstack.object_store.v1.container.Container`
        """
        container = _container.Container.from_id(container)
        container.delete(self.session)

    def objects(self, container, limit=None, marker=None, **kwargs):
        """Return a generator that yields the Container's objects.

        :param container: A container name or object.
        :type container:
            :class:`~openstack.object_store.v1.container.Container`
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

        obj.create(self.session, data)
        return obj

    def copy_object(self):
        """Copy an object."""
        raise NotImplementedError

    def delete_object(self, obj):
        """Delete an object.

        :param obj: The object to delete.
        :type obj: :class:`~openstack.object_store.v1.obj.Object`
        """
        obj.delete(self.session)

    def get_object_metadata(self, obj):
        """Get metatdata for an object.

        :param obj: The object to retreive metadata from.
        :type obj: :class:`~openstack.object_store.v1.obj.Object`
        """
        obj.head(self.session)
        return obj

    def set_object_metadata(self, obj):
        """Set metatdata for an object.

        :param obj: The object to set metadata for.
        :type obj: :class:`~openstack.object_store.v1.obj.Object`
        """
        obj.create(self.session)
        return obj
