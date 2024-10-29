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

import abc
import typing as ty
import warnings

from requests import structures

from openstack import format
from openstack import warnings as os_warnings

_SEEN_FORMAT = '{name}_seen'

_T1 = ty.TypeVar('_T1')
_T2 = ty.TypeVar('_T2')
_T3 = ty.TypeVar('_T3', str, bool, int, float)


# case 1: data_type is unset -> return value as-is
@ty.overload
def _convert_type(
    value: _T1,
    data_type: None,
    list_type: None = None,
) -> _T1: ...


# case 2: data_type is primitive type -> return value as said primitive type
@ty.overload
def _convert_type(
    value: _T1,
    data_type: type[_T3],
    list_type: None = None,
) -> _T3: ...


# case 3: data_type is list, no list_type -> return value as list of whatever
# we got
@ty.overload
def _convert_type(
    value: _T1,
    data_type: type[list[ty.Any]],
    list_type: None = None,
) -> list[_T1]: ...


# case 4: data_type is list, list_type is primitive type -> return value as
# list of said primitive type
@ty.overload
def _convert_type(
    value: ty.Any,
    data_type: type[list[ty.Any]],
    list_type: type[_T3],
) -> list[_T3]: ...


# case 5: data_type is dict or Resource -> return value as dict/Resource
@ty.overload
def _convert_type(
    value: ty.Any,
    data_type: type[dict[ty.Any, ty.Any]],
    list_type: None = None,
) -> dict[ty.Any, ty.Any]: ...


# case 6: data_type is a Formatter -> return value after conversion
@ty.overload
def _convert_type(
    value: ty.Any,
    data_type: type[format.Formatter[type[_T2]]],
    list_type: None = None,
) -> _T2: ...


def _convert_type(
    value: _T1,
    data_type: ty.Optional[
        type[
            ty.Union[
                _T3,
                list[ty.Any],
                dict[ty.Any, ty.Any],
                format.Formatter[_T2],
            ],
        ]
    ],
    list_type: ty.Optional[type[_T3]] = None,
) -> ty.Union[_T1, _T3, list[_T3], list[_T1], dict[ty.Any, ty.Any], _T2]:
    # This should allow handling list of dicts that have their own
    # Component type directly. See openstack/compute/v2/limits.py
    # and the RateLimit type for an example.
    if data_type is None:
        return value
    elif issubclass(data_type, list):
        if isinstance(value, (list, set, tuple)):
            if not list_type:
                return data_type(value)
            return [_convert_type(x, list_type) for x in value]
        elif list_type:
            return [_convert_type(value, list_type)]
        else:
            return [value]
    elif isinstance(value, data_type):
        return value
    elif issubclass(data_type, dict):
        if isinstance(value, dict):
            return data_type(**value)
        # TODO(stephenfin): This should be a warning/error
        return dict()
    elif issubclass(data_type, format.Formatter):
        return data_type.deserialize(value)
    elif issubclass(data_type, bool):
        return data_type(value)
    elif issubclass(data_type, (int, float)):
        if isinstance(value, (int, float)):
            return data_type(value)
        if isinstance(value, str):
            if issubclass(data_type, int) and value.isdigit():
                return data_type(value)
            elif issubclass(data_type, float) and (
                x.isdigit() for x in value.split()
            ):
                return data_type(value)
        return data_type()

    # at this point we expect to have a str and you can convert basically
    # anything to a string, but there could be untyped code out there passing
    # random monstrosities so we need the try-catch to be safe
    try:
        return data_type(value)
    except ValueError:
        return data_type()


class _BaseComponent(abc.ABC):
    # The name this component is being tracked as in the Resource
    key: ty.ClassVar[str]
    # The class to be used for mappings
    _map_cls: ty.ClassVar[type[ty.MutableMapping[str, ty.Any]]] = dict

    name: str
    data_type: ty.Optional[ty.Any]
    default: ty.Any
    alias: ty.Optional[str]
    aka: ty.Optional[str]
    alternate_id: bool
    list_type: ty.Optional[ty.Any]
    coerce_to_default: bool
    deprecated: bool
    deprecation_reason: ty.Optional[str]

    def __init__(
        self,
        name: str,
        type: ty.Optional[ty.Any] = None,
        default: ty.Any = None,
        alias: ty.Optional[str] = None,
        aka: ty.Optional[str] = None,
        alternate_id: bool = False,
        list_type: ty.Optional[ty.Any] = None,
        coerce_to_default: bool = False,
        deprecated: bool = False,
        deprecation_reason: ty.Optional[str] = None,
    ):
        """A typed descriptor for a component that makes up a Resource

        :param name: The name this component exists as on the server
        :param type:
            The type this component is expected to be by the server.
            By default this is None, meaning any value you specify
            will work. If you specify type=dict and then set a
            component to a string, __set__ will fail, for example.
        :param default: Typically None, but any other default can be set.
        :param alias: If set, alternative attribute on object to return.
        :param aka: If set, additional name attribute would be available under.
        :param alternate_id: When `True`, this property is known internally as
            a value that can be sent with requests that require an ID but when
            `id` is not a name the Resource has. This is a relatively uncommon
            case, and this setting should only be used once per Resource.
        :param list_type: If type is `list`, list_type designates what the type
            of the elements of the list should be.
        :param coerce_to_default: If the Component is None or not present,
            force the given default to be used. If a default is not given but a
            type is given, construct an empty version of the type in question.
        :param deprecated: Indicates if the option is deprecated. If it is, we
            display a warning message to the user.
        :param deprecation_reason: Custom deprecation message.
        """
        self.name = name
        self.data_type = type
        if type is not None and coerce_to_default and not default:
            self.default = type()
        else:
            self.default = default
        self.alias = alias
        self.aka = aka
        self.alternate_id = alternate_id
        self.list_type = list_type
        self.coerce_to_default = coerce_to_default

        self.deprecated = deprecated
        self.deprecation_reason = deprecation_reason

    def __get__(
        self,
        instance: object,
        owner: ty.Optional[type[object]] = None,
    ) -> ty.Any:
        if instance is None:
            return self

        attributes = getattr(instance, self.key)

        try:
            value = attributes[self.name]
        except KeyError:
            value = self.default
            if self.alias:
                # Resource attributes can be aliased to each other. If neither
                # of them exist, then simply doing a
                # getattr(instance, self.alias) here sends things into
                # infinite recursion (this _get method is what gets called
                # when getattr(instance) is called.
                # To combat that, we set a flag on the instance saying that
                # we have seen the current name, and we check before trying
                # to resolve the alias if there is already a flag set for that
                # alias name. We then remove the seen flag for ourselves after
                # we exit the alias getattr to clean up after ourselves for
                # the next time.
                alias_flag = _SEEN_FORMAT.format(name=self.alias)
                if not getattr(instance, alias_flag, False):
                    seen_flag = _SEEN_FORMAT.format(name=self.name)
                    # Prevent infinite recursion
                    setattr(instance, seen_flag, True)
                    value = getattr(instance, self.alias)
                    delattr(instance, seen_flag)
            self.warn_if_deprecated_property(value)
            return value

        # self.data_type() should not be called on None objects.
        if value is None:
            return None

        # This warning are pretty intrusive. Every time attribute is accessed
        # a warning is being thrown. In neutron clients we have way too many
        # places that still refer to tenant_id even though they may also
        # properly support project_id. For now we silence tenant_id warnings.
        if self.name != "tenant_id":
            self.warn_if_deprecated_property(value)

        return _convert_type(value, self.data_type, self.list_type)

    @property
    def type(self) -> ty.Optional[ty.Any]:
        # deprecated alias proxy
        return self.data_type

    def warn_if_deprecated_property(self, value: ty.Any) -> None:
        deprecated = object.__getattribute__(self, 'deprecated')
        deprecation_reason = object.__getattribute__(
            self,
            'deprecation_reason',
        )

        if value and deprecated:
            warnings.warn(
                "The field {!r} has been deprecated. {}".format(
                    self.name, deprecation_reason or "Avoid usage."
                ),
                os_warnings.RemovedFieldWarning,
            )

    def __set__(self, instance: object, value: ty.Any) -> None:
        if self.coerce_to_default and value is None:
            value_ = self.default
        elif value != self.default:
            value_ = _convert_type(value, self.data_type, self.list_type)
        else:
            value_ = value

        attributes = getattr(instance, self.key)
        attributes[self.name] = value_

    def __delete__(self, instance: object) -> None:
        try:
            attributes = getattr(instance, self.key)
            del attributes[self.name]
        except KeyError:
            pass


class Body(_BaseComponent):
    """Body attributes"""

    key = "_body"


class Header(_BaseComponent):
    """Header attributes"""

    key = "_header"
    _map_cls = structures.CaseInsensitiveDict


class URI(_BaseComponent):
    """URI attributes"""

    key = "_uri"


class Computed(_BaseComponent):
    """Computed attributes"""

    key = "_computed"
