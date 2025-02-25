# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
#
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

import argparse
import sys
import typing as ty

from openstack.config.loader import OpenStackConfig  # noqa

if ty.TYPE_CHECKING:
    from openstack.config.cloud import cloud_region


# TODO(stephenfin): Expand kwargs once we've typed OpenstackConfig.get_one
def get_cloud_region(
    service_key: ty.Optional[str] = None,
    options: ty.Optional[argparse.ArgumentParser] = None,
    app_name: ty.Optional[str] = None,
    app_version: ty.Optional[str] = None,
    load_yaml_config: bool = True,
    load_envvars: bool = True,
    **kwargs: ty.Any,
) -> 'cloud_region.CloudRegion':
    """Retrieve a single CloudRegion and merge additional options

    :param service_key: Service this argparse should be specialized for, if
        known. This will be used as the default value for service_type.
    :param options: Parser to attach additional options to
    :param app_name: Name of the application to be added to User Agent.
    :param app_version: Version of the application to be added to User Agent.
    :param load_yaml_config: Whether to load configuration from clouds.yaml and
        related configuration files.
    :param load_envvars: Whether to load configuration from environment
        variables
    :returns: A populated
        :class:`~openstack.config.cloud.cloud_region.CloudRegion` object.
    """
    config = OpenStackConfig(
        load_yaml_config=load_yaml_config,
        load_envvars=load_envvars,
        app_name=app_name,
        app_version=app_version,
    )
    if options:
        config.register_argparse_arguments(options, sys.argv, service_key)
        parsed_options, _ = options.parse_known_args(sys.argv)
    else:
        parsed_options = None

    return config.get_one(argparse=parsed_options, **kwargs)
