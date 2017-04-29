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

"""
Connect to an OpenStack cloud.

For a full guide see TODO(etoews):link to docs on developer.openstack.org
"""

import argparse
import os

import os_client_config

from openstack import connection
from openstack import profile
from openstack import utils
import sys

utils.enable_logging(True, stream=sys.stdout)

#: Defines the OpenStack Client Config (OCC) cloud key in your OCC config
#: file, typically in $HOME/.config/openstack/clouds.yaml. That configuration
#: will determine where the examples will be run and what resource defaults
#: will be used to run the examples.
TEST_CLOUD = os.getenv('OS_TEST_CLOUD', 'devstack-admin')


class Opts(object):
    def __init__(self, cloud_name='devstack-admin', debug=False):
        self.cloud = cloud_name
        self.debug = debug
        # Use identity v3 API for examples.
        self.identity_api_version = '3'


def _get_resource_value(resource_key, default):
    try:
        return cloud.config['example'][resource_key]
    except KeyError:
        return default

occ = os_client_config.OpenStackConfig()
cloud = occ.get_one_cloud(TEST_CLOUD)

SERVER_NAME = 'openstacksdk-example'
IMAGE_NAME = _get_resource_value('image_name', 'cirros-0.3.5-x86_64-disk')
FLAVOR_NAME = _get_resource_value('flavor_name', 'm1.small')
NETWORK_NAME = _get_resource_value('network_name', 'private')
KEYPAIR_NAME = _get_resource_value('keypair_name', 'openstacksdk-example')
SSH_DIR = _get_resource_value(
    'ssh_dir', '{home}/.ssh'.format(home=os.path.expanduser("~")))
PRIVATE_KEYPAIR_FILE = _get_resource_value(
    'private_keypair_file', '{ssh_dir}/id_rsa.{key}'.format(
        ssh_dir=SSH_DIR, key=KEYPAIR_NAME))

EXAMPLE_IMAGE_NAME = 'openstacksdk-example-public-image'


def create_connection_from_config():
    opts = Opts(cloud_name=TEST_CLOUD)
    occ = os_client_config.OpenStackConfig()
    cloud = occ.get_one_cloud(opts.cloud)
    return connection.from_config(cloud_config=cloud, options=opts)


def create_connection_from_args():
    parser = argparse.ArgumentParser()
    config = os_client_config.OpenStackConfig()
    config.register_argparse_arguments(parser, sys.argv[1:])
    args = parser.parse_args()
    return connection.from_config(options=args)


def create_connection(auth_url, region, project_name, username, password):
    prof = profile.Profile()
    prof.set_region(profile.Profile.ALL, region)

    return connection.Connection(
        profile=prof,
        user_agent='examples',
        auth_url=auth_url,
        project_name=project_name,
        username=username,
        password=password
    )
