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

For a full guide see
https://docs.openstack.org/openstacksdk/latest/user/guides/connect_from_config.html
"""

import argparse
import os
import sys

import openstack
from openstack.config import loader

openstack.enable_logging(True, stream=sys.stdout)

#: Defines the OpenStack Config cloud key in your config file,
#: typically in $HOME/.config/openstack/clouds.yaml. That configuration
#: will determine where the examples will be run and what resource defaults
#: will be used to run the examples.
TEST_CLOUD = os.getenv('OS_TEST_CLOUD', 'devstack-admin')
EXAMPLE_CONFIG_KEY = os.getenv('OPENSTACKSDK_EXAMPLE_CONFIG_KEY', 'example')
config = loader.OpenStackConfig()
cloud = openstack.connect(cloud=TEST_CLOUD)


class Opts:
    def __init__(self, cloud_name='devstack-admin', debug=False):
        self.cloud = cloud_name
        self.debug = debug
        # Use identity v3 API for examples.
        self.identity_api_version = '3'


def _get_resource_value(resource_key, default):
    return config.get_extra_config(
        EXAMPLE_CONFIG_KEY).get(resource_key, default)


SERVER_NAME = 'openstacksdk-example'
IMAGE_NAME = _get_resource_value('image_name', 'cirros-0.4.0-x86_64-disk')
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
    return openstack.connect(cloud=TEST_CLOUD)


def create_connection_from_args():
    parser = argparse.ArgumentParser()
    return openstack.connect(options=parser)


def create_connection(auth_url, region, project_name, username, password,
                      user_domain, project_domain):
    return openstack.connect(
        auth_url=auth_url,
        project_name=project_name,
        username=username,
        password=password,
        region_name=region,
        user_domain_name=user_domain,
        project_domain_name=project_domain,
        app_name='examples',
        app_version='1.0',
    )
