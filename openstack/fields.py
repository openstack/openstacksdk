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


def _convert_type(value, data_type, list_type=None):
    # This should allow handling list of dicts that have their own
    # Component type directly. See openstack/compute/v2/limits.py
    # and the RateLimit type for an example.
    if not data_type:
        return value
    elif issubclass(data_type, list):
        if isinstance(value, (list, tuple, set)):
            if not list_type:
                return data_type(value)
            return [_convert_type(raw, list_type) for raw in value]
        elif list_type:
            return [_convert_type(value, list_type)]
        else:
            # "if-match" in Object is a good example of the need here
            return [value]
    elif isinstance(value, data_type):
        return value
    elif isinstance(value, dict):
        # This should allow handling sub-dicts that have their own
        # Component type directly. See openstack/compute/v2/limits.py
        # and the AbsoluteLimits type for an example.
        # NOTE(stephenfin): This will fail if value is not one of a select set
        # of types (basically dict or list of two item tuples/lists)
        return data_type(**value)
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
    key: str
    # The class to be used for mappings
    _map_cls: type[ty.Mapping] = dict

    #: Marks the property as deprecated.
    deprecated = False
    #: Deprecation reason message used to warn users when deprecated == True
    deprecation_reason = None

    #: Control field used to manage the deprecation warning. We want to warn
    #: only once when the attribute is retrieved in the code.
    already_warned_deprecation = False

    def __init__(
        self,
        name,
        type=None,
        default=None,
        alias=None,
        aka=None,
        alternate_id=False,
        list_type=None,
        coerce_to_default=False,
        deprecated=False,
        deprecation_reason=None,
        **kwargs,
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
        :param alternate_id:
            When `True`, this property is known internally as a value that
            can be sent with requests that require an ID but when `id` is
            not a name the Resource has. This is a relatively uncommon case,
            and this setting should only be used once per Resource.
        :param list_type:
            If type is `list`, list_type designates what the type of the
            elements of the list should be.
        :param coerce_to_default:
            If the Component is None or not present, force the given default
            to be used. If a default is not given but a type is given,
            construct an empty version of the type in question.
        :param deprecated:
            Indicates if the option is deprecated. If it is, we display a
            warning message to the user.
        :param deprecation_reason:
            Custom deprecation message.
        """
        self.name = name
        self.type = type
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

    def __get__(self, instance, owner):
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

        # self.type() should not be called on None objects.
        if value is None:
            return None

        # This warning are pretty intrusive. Every time attribute is accessed
        # a warning is being thrown. In neutron clients we have way too many
        # places that still refer to tenant_id even though they may also
        # properly support project_id. For now we silence tenant_id warnings.
        if self.name != "tenant_id":
            self.warn_if_deprecated_property(value)

        return _convert_type(value, self.type, self.list_type)

    def warn_if_deprecated_property(self, value):
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
        return value

    def __set__(self, instance, value):
        if self.coerce_to_default and value is None:
            value = self.default
        if value != self.default:
            value = _convert_type(value, self.type, self.list_type)

        attributes = getattr(instance, self.key)
        attributes[self.name] = value

    def __delete__(self, instance):
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
