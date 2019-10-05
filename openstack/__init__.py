# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from openstack._log import enable_logging  # noqa
import openstack.config
import openstack.connection

__all__ = [
    'connect',
    'enable_logging',
]


def connect(
        cloud=None,
        app_name=None,  # type: Optional[str]
        app_version=None,  # type: Optional[str]
        options=None,
        load_yaml_config=True,  # type: bool
        load_envvars=True,  # type: bool
        **kwargs):
    # type: (...) -> openstack.connection.Connection
    """Create a :class:`~openstack.connection.Connection`

    :param string cloud:
        The name of the configuration to load from clouds.yaml. Defaults
        to 'envvars' which will load configuration settings from environment
        variables that start with ``OS_``.
    :param argparse.Namespace options:
        An argparse Namespace object. allows direct passing in of
        argparse options to be added to the cloud config.  Values
        of None and '' will be removed.
    :param bool load_yaml_config:
        Whether or not to load config settings from clouds.yaml files.
        Defaults to True.
    :param bool load_envvars:
        Whether or not to load config settings from environment variables.
        Defaults to True.
    :param kwargs:
        Additional configuration options.

    :returns: openstack.connnection.Connection
    :raises: keystoneauth1.exceptions.MissingRequiredOptions
        on missing required auth parameters
    """
    cloud_region = openstack.config.get_cloud_region(
        cloud=cloud,
        app_name=app_name, app_version=app_version,
        load_yaml_config=load_yaml_config,
        load_envvars=load_envvars,
        options=options, **kwargs)
    return openstack.connection.Connection(
        config=cloud_region,
        vendor_hook=kwargs.get('vendor_hook'))
