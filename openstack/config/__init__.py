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

import sys

from openstack.config.loader import OpenStackConfig  # noqa


def get_cloud_region(
        service_key=None, options=None,
        app_name=None, app_version=None,
        load_yaml_config=True,
        load_envvars=True,
        **kwargs):
    config = OpenStackConfig(
        load_yaml_config=load_yaml_config,
        load_envvars=load_envvars,
        app_name=app_name, app_version=app_version)
    if options:
        config.register_argparse_arguments(options, sys.argv, service_key)
        parsed_options = options.parse_known_args(sys.argv)
    else:
        parsed_options = None

    return config.get_one(options=parsed_options, **kwargs)
