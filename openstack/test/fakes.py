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

"""
The :mod:`~openstack.test.fakes` module exists to help application developers
using the OpenStack SDK to unit test their applications. It provides a number
of helper utilities to generate fake :class:`~openstack.resource.Resource` and
:class:`~openstack.proxy.Proxy` instances. These fakes do not require an
established connection and allow you to validate that your application using
valid attributes and methods for both :class:`~openstack.resource.Resource` and
:class:`~openstack.proxy.Proxy` instances.
"""

from collections.abc import Generator
import inspect
import random
import types
import typing
from typing import Any, cast
from unittest import mock
import uuid

from openstack import fields
from openstack import format as _format
from openstack import proxy
from openstack import resource
from openstack import service_description


def generate_fake_resource(
    resource_type: type[resource.ResourceT],
    **attrs: Any,
) -> resource.ResourceT:
    """Generate a fake resource

    Example usage:

    .. code-block:: python

        >>> from openstack.compute.v2 import server
        >>> from openstack.test import fakes
        >>> fakes.generate_fake_resource(server.Server)
        openstack.compute.v2.server.Server(...)

    :param resource_type: Object class
    :param attrs: Optional attributes to be set on resource
    :return: Instance of ``resource_type`` class populated with fake
        values of expected types
    :raises NotImplementedError: If a resource attribute specifies a ``type``
        or ``list_type`` that cannot be automatically generated
    """
    base_attrs: dict[str, Any] = {}
    for name, value in inspect.getmembers(
        resource_type,
        predicate=lambda x: isinstance(x, fields.Body | fields.URI),
    ):
        if isinstance(value, fields.Body):
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
                    base_attrs[name] = [generate_fake_resource(item_type)]
                elif issubclass(item_type, dict):
                    base_attrs[name] = [{}]
                elif issubclass(item_type, str):
                    base_attrs[name] = [uuid.uuid4().hex]
                else:
                    # Everything else
                    msg = (
                        f"Fake value for {resource_type.__name__}.{name} can "
                        f"not be generated"
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
                base_attrs[name] = random.randint(1, 100)  # noqa: S311
            elif issubclass(target_type, float):
                # float
                base_attrs[name] = random.random()  # noqa: S311
            elif issubclass(target_type, bool) or issubclass(
                target_type, _format.BoolStr
            ):
                # bool
                base_attrs[name] = random.choice([True, False])  # noqa: S311
            elif issubclass(target_type, dict):
                # some dict - without further details leave it empty
                base_attrs[name] = dict()
            else:
                # Everything else
                msg = (
                    f"Fake value for {resource_type.__name__}.{name} can not "
                    f"be generated"
                )
                raise NotImplementedError(msg)

        if isinstance(value, fields.URI):
            # For URI we just generate something
            base_attrs[name] = uuid.uuid4().hex

    base_attrs.update(**attrs)
    fake = resource_type(**base_attrs)
    return fake


def generate_fake_resources(
    resource_type: type[resource.ResourceT],
    count: int = 1,
    attrs: dict[str, Any] | None = None,
) -> Generator[resource.ResourceT, None, None]:
    """Generate a given number of fake resource entities

    Example usage:

    .. code-block:: python

        >>> from openstack.compute.v2 import server
        >>> from openstack.test import fakes
        >>> fakes.generate_fake_resources(server.Server, count=3)
        <generator object generate_fake_resources at 0x7f075dc65040>

    :param resource_type: Object class
    :param count: Number of objects to return
    :param attrs: Attribute values to set into each instance
    :return: Generator of ``resource_type`` class instances populated with fake
        values of expected types.
    """
    if not attrs:
        attrs = {}
    for _ in range(count):
        yield generate_fake_resource(resource_type, **attrs)


def _resource_type_from_hint(
    return_hint: Any,
) -> tuple[type[resource.Resource], bool] | None:
    """Extract a resource type and generator flag from a return type hint.

    Returns ``(resource_type, is_generator)`` or ``None`` if the hint does not
    describe a Resource (or Generator thereof).
    """
    # Direct Resource subclass: -> Server
    if isinstance(return_hint, type) and issubclass(
        return_hint, resource.Resource
    ):
        return (return_hint, False)

    origin = typing.get_origin(return_hint)
    args = typing.get_args(return_hint)

    # Generator[ResourceType, None, None]
    if origin is Generator and args:
        first = args[0]
        if isinstance(first, type) and issubclass(first, resource.Resource):
            return (first, True)

    # ResourceType | None  (types.UnionType from PEP 604)
    # typing.Union[ResourceType, None]  (legacy Optional)
    if isinstance(return_hint, types.UnionType) or origin is typing.Union:
        resource_types = [
            a
            for a in args
            if isinstance(a, type) and issubclass(a, resource.Resource)
        ]
        if len(resource_types) == 1:
            return (resource_types[0], False)

    return None


def _make_resource_side_effect(
    resource_type: type[resource.Resource],
    is_generator: bool,
) -> Any:
    """Return a callable suitable for use as a mock side_effect."""
    if is_generator:

        def _side_effect(*args: Any, **kwargs: Any) -> Any:
            return generate_fake_resources(resource_type)

    else:

        def _side_effect(*args: Any, **kwargs: Any) -> Any:
            return generate_fake_resource(resource_type)

    return _side_effect


def generate_fake_proxy(
    service: type[service_description.ServiceDescription[proxy.ProxyT]],
    api_version: str | None = None,
) -> proxy.ProxyT:
    """Generate a fake proxy for the given service type

    Proxy methods whose return type annotation is a
    :class:`~openstack.resource.Resource` subclass (or a
    ``Generator`` / optional thereof) are automatically configured to return
    fake resource instances via :func:`generate_fake_resource` or
    :func:`generate_fake_resources`.  Return values can still be overridden
    on the returned mock after the fact.

    Example usage:

    .. code-block:: python

        >>> from openstack.compute import compute_service
        >>> from openstack.compute.v2 import server
        >>> from openstack.test import fakes
        >>> fake_compute_proxy = fakes.generate_fake_proxy(
        ...    compute_service.ComputeService,
        ... )
        >>> # get_server is pre-configured; returns a fake Server
        >>> fake_server = fake_compute_proxy.get_server('some-uuid')
        >>> isinstance(fake_server, server.Server)
        True
        >>> # servers() is pre-configured; yields fake Server instances
        >>> fake_servers = list(fake_compute_proxy.servers())
        >>> isinstance(fake_servers[0], server.Server)
        True
        >>> fake_compute_proxy.serverssss()
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "/usr/lib64/python3.11/unittest/mock.py", line 653, in __getattr__
            raise AttributeError("Mock object has no attribute %r" % name)
        AttributeError: Mock object has no attribute 'serverssss'. Did you mean: 'server_ips'?

    :param service: The service to generate the fake proxy for.
    :type service: :class:`~openstack.service_description.ServiceDescription`
    :param api_version: The API version to generate the fake proxy for.
        This should be a major version must be supported by openstacksdk, as
        specified in the ``supported_versions`` attribute of the provided
        ``service``. This is only required if openstacksdk supports multiple
        API versions for the given service.
    :type api_version: int or None
    :raises ValueError: if the ``service`` is not a valid
        :class:`~openstack.service_description.ServiceDescription` or if
        ``api_version`` is not supported
    :returns: An autospecced mock of the :class:`~openstack.proxy.Proxy`
        implementation for the specified service type and API version
    """  # noqa: E501
    if not issubclass(service, service_description.ServiceDescription):
        raise ValueError(
            f"Service {service.__name__} is not a valid ServiceDescription"
        )

    supported_versions = service.supported_versions

    if api_version is None:
        if len(supported_versions) > 1:
            raise ValueError(
                f"api_version was not provided but service {service.__name__} "
                f"provides multiple API versions"
            )
        else:
            api_version = next(iter(supported_versions))
    elif api_version not in supported_versions:
        raise ValueError(
            f"API version {api_version} is not supported by openstacksdk. "
            f"Supported API versions are: {', '.join(supported_versions)}"
        )

    proxy_class = supported_versions[api_version]
    fake_proxy = cast(
        proxy.ProxyT, mock.create_autospec(proxy_class, spec_set=True)
    )

    for name, _ in inspect.getmembers(
        proxy_class, predicate=inspect.isfunction
    ):
        if name.startswith('_'):
            continue
        method = getattr(proxy_class, name)
        try:
            hints = typing.get_type_hints(method)
        except Exception:  # noqa: S112
            continue
        return_hint = hints.get('return')
        if return_hint is None:
            continue
        result = _resource_type_from_hint(return_hint)
        if result is None:
            continue
        resource_type, is_generator = result
        getattr(fake_proxy, name).side_effect = _make_resource_side_effect(
            resource_type, is_generator
        )

    return fake_proxy
