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


import os

import yaml

from os_client_config import cloud_config
from os_client_config import defaults_dict
from os_client_config import exceptions
from os_client_config import vendors

CONFIG_HOME = os.path.join(os.path.expanduser(
    os.environ.get('XDG_CONFIG_HOME', os.path.join('~', '.config'))),
    'openstack')
CONFIG_SEARCH_PATH = [os.getcwd(), CONFIG_HOME, '/etc/openstack']
CONFIG_FILES = [
    os.path.join(d, 'clouds.yaml') for d in CONFIG_SEARCH_PATH]
BOOL_KEYS = ('insecure', 'cache')
REQUIRED_VALUES = ('auth_url', 'username', 'password', 'project_id')


def get_boolean(value):
    if value.lower() == 'true':
        return True
    return False


class OpenStackConfig(object):

    def __init__(self, config_files=None):
        self._config_files = config_files or CONFIG_FILES

        defaults = defaults_dict.DefaultsDict()
        defaults.add('username')
        defaults.add('user_domain_name')
        defaults.add('password')
        defaults.add('project_id', defaults['username'], also='tenant_name')
        defaults.add('project_domain_name')
        defaults.add('auth_url')
        defaults.add('region_name')
        defaults.add('cache')
        defaults.add('auth_token')
        defaults.add('insecure')
        defaults.add('endpoint_type')
        defaults.add('cacert')

        self.defaults = defaults

        # use a config file if it exists where expected
        self.cloud_config = self._load_config_file()
        if not self.cloud_config:
            self.cloud_config = dict(
                clouds=dict(openstack=dict(self.defaults)))

    @classmethod
    def get_services(klass):
        return SERVICES

    def _load_config_file(self):
        for path in self._config_files:
            if os.path.exists(path):
                return yaml.load(open(path, 'r'))

    def _get_regions(self, cloud):
        return self.cloud_config['clouds'][cloud]['region_name']

    def _get_region(self, cloud):
        return self._get_regions(cloud).split(',')[0]

    def _get_cloud_sections(self):
        return self.cloud_config['clouds'].keys()

    def _get_base_cloud_config(self, name):
        cloud = dict()
        if name in self.cloud_config['clouds']:
            our_cloud = self.cloud_config['clouds'][name]
        else:
            our_cloud = dict()

        # yes, I know the next line looks silly
        if 'cloud' in our_cloud:
            cloud.update(vendors.CLOUD_DEFAULTS[our_cloud['cloud']])

        cloud.update(self.defaults)
        cloud.update(our_cloud)
        if 'cloud' in cloud:
            del cloud['cloud']
        return cloud

    def get_all_clouds(self):

        clouds = []

        for cloud in self._get_cloud_sections():
            for region in self._get_regions(cloud).split(','):
                clouds.append(self.get_one_cloud(cloud, region))
        return clouds

    def get_one_cloud(self, name='openstack', region=None):

        if not region:
            region = self._get_region(name)

        config = self._get_base_cloud_config(name)
        config['region_name'] = region

        for key in BOOL_KEYS:
            if key in config:
                config[key] = get_boolean(config[key])

        for key in REQUIRED_VALUES:
            if key not in config or not config[key]:
                raise exceptions.OpenStackConfigException(
                    'Unable to find full auth information for cloud {name} in'
                    ' config files {files}'
                    ' or environment variables.'.format(
                        name=name, files=','.join(self._config_files)))

        # If any of the defaults reference other values, we need to expand
        for (key, value) in config.items():
            if hasattr(value, 'format'):
                config[key] = value.format(**config)

        return cloud_config.CloudConfig(
            name=name, region=region, config=config)

if __name__ == '__main__':
    config = OpenStackConfig().get_all_clouds()
    for cloud in config:
        print(cloud.name, cloud.region, cloud.config)
