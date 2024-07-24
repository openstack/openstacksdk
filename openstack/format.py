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

import typing as ty

_T = ty.TypeVar('_T')


class Formatter(ty.Generic[_T]):
    @classmethod
    def deserialize(cls, value: ty.Any) -> _T:
        """Return a formatted object representing the value"""
        raise NotImplementedError


class BoolStr(Formatter[bool]):
    @classmethod
    def deserialize(cls, value: ty.Any) -> bool:
        """Convert a boolean string to a boolean"""
        expr = str(value).lower()
        if "true" == expr:
            return True
        elif "false" == expr:
            return False
        else:
            raise ValueError(f"Unable to deserialize boolean string: {value}")
