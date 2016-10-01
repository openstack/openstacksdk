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

import pbr.version

from os_client_config import cloud_config
from os_client_config.config import OpenStackConfig  # noqa


__version__ = pbr.version.VersionInfo('os_client_config').version_string()


def get_config(service_key=None, options=None, **kwargs):
    config = OpenStackConfig()
    if options:
        config.register_argparse_arguments(options, sys.argv, service_key)
        parsed_options = options.parse_known_args(sys.argv)
    else:
        parsed_options = None

    return config.get_one_cloud(options=parsed_options, **kwargs)


def make_rest_client(service_key, options=None, **kwargs):
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
    cloud = get_config(service_key=service_key, options=options, **kwargs)
    return cloud.get_session_client(service_key)
# Backwards compat - simple_client was a terrible name
simple_client = make_rest_client
# Backwards compat - session_client was a terrible name
session_client = make_rest_client


def make_client(service_key, constructor=None, options=None, **kwargs):
    """Simple wrapper for getting a client instance from a client lib.

    OpenStack Client Libraries all have a fairly consistent constructor
    interface which os-client-config supports. In the simple case, there
    is one and only one right way to construct a client object. If as a user
    you don't want to do fancy things, just use this. It honors OS_ environment
    variables and clouds.yaml - and takes as **kwargs anything you'd expect
    to pass in.
    """
    cloud = get_config(service_key=service_key, options=options, **kwargs)
    if not constructor:
        constructor = cloud_config._get_client(service_key)
    return cloud.get_legacy_client(service_key, constructor)


def make_sdk(options=None, **kwargs):
    """Simple wrapper for getting an OpenStack SDK Connection.

    For completeness, provide a mechanism that matches make_client and
    make_rest_client. The heavy lifting here is done in openstacksdk.

    :rtype: :class:`~openstack.connection.Connection`
    """
    from openstack import connection
    cloud = get_config(options=options, **kwargs)
    return connection.from_config(cloud_config=cloud, options=options)


def make_shade(options=None, **kwargs):
    """Simple wrapper for getting a Shade OpenStackCloud object

    A mechanism that matches make_sdk, make_client and make_rest_client.

    :rtype: :class:`~shade.OpenStackCloud`
    """
    import shade
    cloud = get_config(options=options, **kwargs)
    return shade.OpenStackCloud(cloud_config=cloud, **kwargs)
