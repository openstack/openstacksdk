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

import inspect
from random import choice
from random import randint
from random import random
import uuid

from openstack import format as _format
from openstack import resource


def generate_fake_resource(resource_type, **attrs):
    """Generate fake resource

    :param type resource_type: Object class
    :param dict attrs: Optional attributes to be set on resource

    :return: Instance of `resource_type` class populated with fake
        values of expected types.
    """
    base_attrs = dict()
    for name, value in inspect.getmembers(
        resource_type,
        predicate=lambda x: isinstance(x, (resource.Body, resource.URI)),
    ):
        if isinstance(value, resource.Body):
            target_type = value.type
            if target_type is None:
                if (
                    name == "properties"
                    and hasattr(
                        resource_type, "_store_unknown_attrs_as_properties"
                    )
                    and resource_type._store_unknown_attrs_as_properties
                ):
                    # virtual "properties" attr which hosts all unknown attrs
                    # (i.e. Image)
                    base_attrs[name] = dict()
                else:
                    # Type not defined - string
                    base_attrs[name] = uuid.uuid4().hex
            elif issubclass(target_type, resource.Resource):
                # Attribute is of another Resource type
                base_attrs[name] = generate_fake_resource(target_type)
            elif issubclass(target_type, list) and value.list_type is not None:
                # List of ...
                item_type = value.list_type
                if issubclass(item_type, resource.Resource):
                    # item is of Resource type
                    base_attrs[name] = generate_fake_resource(item_type)
                elif issubclass(item_type, dict):
                    base_attrs[name] = dict()
                elif issubclass(item_type, str):
                    base_attrs[name] = [uuid.uuid4().hex]
                else:
                    # Everything else
                    msg = "Fake value for %s.%s can not be generated" % (
                        resource_type.__name__,
                        name,
                    )
                    raise NotImplementedError(msg)
            elif issubclass(target_type, list) and value.list_type is None:
                # List of str
                base_attrs[name] = [uuid.uuid4().hex]
            elif issubclass(target_type, str):
                # definitely string
                base_attrs[name] = uuid.uuid4().hex
            elif issubclass(target_type, int):
                # int
                base_attrs[name] = randint(1, 100)
            elif issubclass(target_type, float):
                # float
                base_attrs[name] = random()
            elif issubclass(target_type, bool) or issubclass(
                target_type, _format.BoolStr
            ):
                # bool
                base_attrs[name] = choice([True, False])
            elif issubclass(target_type, dict):
                # some dict - without further details leave it empty
                base_attrs[name] = dict()
            else:
                # Everything else
                msg = "Fake value for %s.%s can not be generated" % (
                    resource_type.__name__,
                    name,
                )
                raise NotImplementedError(msg)
        if isinstance(value, resource.URI):
            # For URI we just generate something
            base_attrs[name] = uuid.uuid4().hex

    base_attrs.update(**attrs)
    fake = resource_type(**base_attrs)
    return fake


def generate_fake_resources(resource_type, count=1, attrs=None):
    """Generate given number of fake resource entities

    :param type resource_type: Object class
    :param int count: Number of objects to return
    :param dict attrs: Attribute values to set into each instance

    :return: Array of `resource_type` class instances populated with fake
        values of expected types.
    """
    if not attrs:
        attrs = {}
    for _ in range(count):
        yield generate_fake_resource(resource_type, **attrs)
