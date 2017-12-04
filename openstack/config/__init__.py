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

_config = None


def get_config(
        service_key=None, options=None,
        app_name=None, app_version=None,
        **kwargs):
    load_yaml_config = kwargs.pop('load_yaml_config', True)
    global _config
    if not _config:
        _config = OpenStackConfig(
            load_yaml_config=load_yaml_config,
            app_name=app_name, app_version=app_version)
    if options:
        _config.register_argparse_arguments(options, sys.argv, service_key)
        parsed_options = options.parse_known_args(sys.argv)
    else:
        parsed_options = None

    return _config.get_one_cloud(options=parsed_options, **kwargs)


def make_rest_client(
        service_key, options=None,
        app_name=None, app_version=None, version=None,
        **kwargs):
    """Simple wrapper function. It has almost no features.

    This will get you a raw requests Session Adapter that is mounted
    on the given service from the keystone service catalog. If you leave
    off cloud and region_name, it will assume that you've got env vars
    set, but if you give them, it'll use clouds.yaml as you'd expect.

    This function is deliberately simple. It has no flexibility. If you
    want flexibility, you can make a cloud config object and call
    get_session_client on it. This function is to make it easy to poke
    at OpenStack REST APIs with a properly configured keystone session.
    """
    cloud = get_config(
        service_key=service_key, options=options,
        app_name=app_name, app_version=app_version,
        **kwargs)
    return cloud.get_session_client(service_key, version=version)
# Backwards compat - simple_client was a terrible name
simple_client = make_rest_client
# Backwards compat - session_client was a terrible name
session_client = make_rest_client


def make_connection(options=None, **kwargs):
    """Simple wrapper for getting an OpenStack SDK Connection.

    For completeness, provide a mechanism that matches make_client and
    make_rest_client. The heavy lifting here is done in openstacksdk.

    :rtype: :class:`~openstack.connection.Connection`
    """
    from openstack import connection
    cloud = get_config(options=options, **kwargs)
    return connection.from_config(cloud_config=cloud, options=options)


def make_cloud(options=None, **kwargs):
    """Simple wrapper for getting an OpenStackCloud object

    A mechanism that matches make_connection and make_rest_client.

    :rtype: :class:`~openstack.OpenStackCloud`
    """
    import openstack.cloud
    cloud = get_config(options=options, **kwargs)
    return openstack.OpenStackCloud(cloud_config=cloud, **kwargs)
