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

from typing import Any, Generic, TypeVar

_T = TypeVar('_T')


class Formatter(Generic[_T]):
    @classmethod
    def deserialize(cls, value: Any) -> _T:
        """Return a formatted object representing the value"""
        raise NotImplementedError


class BoolStr(Formatter[bool]):
    @classmethod
    def deserialize(cls, value: Any) -> bool:
        """Convert a boolean string to a boolean"""
        expr = str(value).lower()
        if "true" == expr:
            return True
        elif "false" == expr:
            return False
        else:
            raise ValueError(f"Unable to deserialize boolean string: {value}")


class FlexibleBoolStr(Formatter[bool]):
    """Leniently convert a boolean string to a boolean

    Behaves like ``oslo_utils.strutils.bool_from_string`` with its default
    arguments, which is how services such as Nova interpret these values:
    recognised strings map to ``True`` or ``False`` and anything else is
    ``False``. This also means a single malformed value cannot prevent the
    containing resource from being loaded.
    """

    TRUE_STRINGS = frozenset(('1', 't', 'true', 'on', 'y', 'yes'))

    @classmethod
    def deserialize(cls, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in cls.TRUE_STRINGS
