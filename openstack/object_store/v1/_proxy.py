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

import six

from openstack.object_store.v1 import container as _container
from openstack.object_store.v1 import obj as _obj


class Proxy(object):

    def __init__(self, session):
        self.session = session

    def get_account_metadata(self, container=None):
        """Get metatdata for this account.

        :param container:
        :type Container: :class:`~openstack.object_store.v1.container`
        """
        if container is None:
            container = _container.Container()
        container.head(self.session)
        return container

    def set_account_metadata(self, container):
        """Set metatdata for this account.

        :param container:
        :type Container: :class:`~openstack.object_store.v1.container`
        """
        container.update(self.session)
        return container

    def list_containers(self):
        """List containers for this account."""
        container = _container.Container()
        return container.list(self.session)

    def get_container_metadata(self, container):
        """Get metatdata for a container.

        :param container:
        :type Container: :class:`~openstack.object_store.v1.container`
        """
        container.head(self.session)
        return container

    def set_container_metadata(self, container):
        """Set metatdata for a container.

        :param container:
        :type Container: :class:`~openstack.object_store.v1.container`
        """
        container.create(self.session)
        return container

    def create_container(self, container):
        """Create a container,

        :param container:
        :type Container: :class:`~openstack.object_store.v1.container`
        """
        if isinstance(container, six.text_type):
            cont = _container.Container()
            cont.name = container
            cont.create(self.session)
            return cont
        container.create(self.session)
        return container

    def delete_container(self, container):
        """Delete a container.

        :param container:
        :type Container: :class:`~openstack.object_store.v1.container`
        """
        if isinstance(container, six.text_type):
            cont = _container.Container()
            cont.name = container
            cont.delete(self.session)
        container.delete(self.session)

    def list_objects(self, container):
        """List objects inside a container.

        :param container:
        :type Container: :class:`~openstack.object_store.v1.container`
        """
        cont_name = getattr(container, "name", None)
        if cont_name is None:
            cont_name = container

        obj = _obj.Object()
        objs = obj.list(self.session, path_args={"container": cont_name})
        # TODO(brian): Objects have to know their container at this point,
        # otherwise further operations like getting their metadata
        # or downloading them is a hassle because the end-user would have
        # to maintain both the container and the object separately.
        for ob in objs:
            ob.container = cont_name
        return objs

    def get_object_data(self, obj):
        """Retreive the data contained inside an object.

        :param obj:
        :type Object: :class:`~openstack.object_store.v1.obj`
        """
        return obj.get(self.session)

    def save_object(self, obj, path):
        """Save the data contained inside an object to disk.

        :param obj:
        :type Object: :class:`~openstack.object_store.v1.obj`
        "param path str: Location to write the object contents.
        """
        with open(path, "w") as out:
            out.write(self.get_object_data(obj))

    def create_object(self, **kwargs):
        """Create an object."""
        # Have to have data
        data = kwargs.pop("data")

        # If we're given an Object...
        obj = kwargs.pop("obj", False)
        if obj:
            obj.create(self.session, data)
            return obj

        # If we're given a container to house the object...
        # Could be a string name, could be a Container object.
        container = kwargs.pop("container", False)
        container_name = getattr(container, "name", None)
        if container_name is None:
            container_name = container

        cont = _container.Container()
        cont.name = container_name
        cont.create(self.session)

        name = kwargs.pop("name", False)
        if not name:
            raise ValueError("need a `name` argument with `container`")

        ob = _obj.Object()
        ob.container = cont.name
        ob.name = name

        ob.create(self.session, data)

        return ob

    def copy_object(self):
        """Copy an object."""
        raise NotImplementedError

    def delete_object(self, obj):
        """Delete an object.

        :param obj:
        :type Object: :class:`~openstack.object_store.v1.obj`
        """
        obj.delete(self.session)

    def get_object_metadata(self, obj):
        """Get metatdata for an object.

        :param obj:
        :type Object: :class:`~openstack.object_store.v1.obj`
        """
        obj.head(self.session)
        return obj

    def set_object_metadata(self, obj):
        """Set metatdata for an object.

        :param obj:
        :type Object: :class:`~openstack.object_store.v1.obj`
        """
        obj.create(self.session)
        return obj
