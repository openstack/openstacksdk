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

"""The openstack SDK.

:py:mod:`openstacksdk` is a client library for building applications to work
with OpenStack clouds. The project aims to provide a consistent and complete
set of interactions with OpenStack's many services, along with complete
documentation, examples, and tools.

There are three ways to interact with :py:mod:`openstacksdk`. The *clouds
layer*, the *proxy layer*, and the *resource layer*. Most users will make use
of either the *cloud layer* or *proxy layer*.

Listing flavours using the *cloud layer*::

    >>> import openstack
    >>> conn = openstack.connect(cloud='mordred')
    >>> for server in conn.list_servers():
    ...     print(server.to_dict())

Listing servers using the *proxy layer*::

    >>> import openstack
    >>> conn = openstack.connect(cloud='mordred')
    >>> for server in conn.compute.servers():
    ...     print(server.to_dict())

Listing servers using the *resource layer*::

    >>> import openstack
    >>> import openstack.compute.v2.server
    >>> conn = openstack.connect(cloud='mordred')
    >>> for server in openstack.compute.v2.server.Server.list(
    ...     session=conn.compute,
    ... ):
    ...     print(server.to_dict())

For more information, refer to the documentation found in each submodule.
"""

import argparse
import typing as ty

from openstack._log import enable_logging
import openstack.config
import openstack.connection

__all__ = [
    'connect',
    'enable_logging',
]


def connect(
    cloud: ty.Optional[str] = None,
    app_name: ty.Optional[str] = None,
    app_version: ty.Optional[str] = None,
    options: ty.Optional[argparse.ArgumentParser] = None,
    load_yaml_config: bool = True,
    load_envvars: bool = True,
    **kwargs: ty.Any,
) -> openstack.connection.Connection:
    """Create a :class:`~openstack.connection.Connection`

    :param string cloud:
        The name of the configuration to load from clouds.yaml. Defaults
        to 'envvars' which will load configuration settings from environment
        variables that start with ``OS_``.
    :param argparse.ArgumentParser options:
        An argparse ArgumentParser object. SDK-specific options will be
        registered, parsed out and used to configure the connection.
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
        app_name=app_name,
        app_version=app_version,
        load_yaml_config=load_yaml_config,
        load_envvars=load_envvars,
        options=options,
        **kwargs,
    )
    return openstack.connection.Connection(
        config=cloud_region,
        vendor_hook=kwargs.get('vendor_hook'),
    )
