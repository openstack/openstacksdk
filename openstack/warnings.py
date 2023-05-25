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


class OpenStackDeprecationWarning(DeprecationWarning):
    """Base class for warnings about deprecated features in openstacksdk."""


class RemovedResourceWarning(OpenStackDeprecationWarning):
    """Indicates that a resource has been removed in newer API versions and
    should not be used.
    """


class RemovedFieldWarning(OpenStackDeprecationWarning):
    """Indicates that a field has been removed in newer API versions and should
    not be used.
    """


class LegacyAPIWarning(OpenStackDeprecationWarning):
    """Indicates an API that is in 'legacy' status, a long term deprecation."""


class OpenStackWarning(Warning):
    """Base class for general warnings in openstacksdk."""


class ConfigurationWarning(OpenStackWarning):
    """Indicates an issue with configuration."""


class UnsupportedServiceVersion(OpenStackWarning):
    """Indicates a major version that SDK doesn't understand."""
