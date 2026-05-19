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

from collections.abc import Callable
import functools
from typing import Any, TypeVar, cast
import warnings

from openstack import warnings as os_warnings

F = TypeVar('F', bound=Callable[..., Any])


def renamed_param(old: str, new: str) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if old in kwargs:
                warnings.warn(
                    f"Parameter '{old}' has been renamed to '{new}'.",
                    os_warnings.RemovedInSDK50Warning,
                    stacklevel=2,
                )
                kwargs[new] = kwargs.pop(old)
            return func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator
