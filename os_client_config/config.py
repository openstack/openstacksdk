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
CACHE_PATH = os.path.join(os.path.expanduser(
    os.environ.get('XDG_CACHE_PATH', os.path.join('~', '.cache'))),
    'openstack')
BOOL_KEYS = ('insecure', 'cache')
REQUIRED_VALUES = ('auth_url', 'username', 'password')
VENDOR_SEARCH_PATH = [os.getcwd(), CONFIG_HOME, '/etc/openstack']
VENDOR_FILES = [
    os.path.join(d, 'clouds-public.yaml') for d in VENDOR_SEARCH_PATH]


def get_boolean(value):
    if value.lower() == 'true':
        return True
    return False


class OpenStackConfig(object):

    def __init__(self, config_files=None, vendor_files=None):
        self._config_files = config_files or CONFIG_FILES
        self._vendor_files = vendor_files or VENDOR_FILES

        defaults = defaults_dict.DefaultsDict()
        defaults.add('username')
        defaults.add('user_domain_name')
        defaults.add('password')
        defaults.add(
            'project_name', defaults.get('username', None),
            also='tenant_name')
        defaults.add('project_id', also='tenant_id')
        defaults.add('project_domain_name')
        defaults.add('auth_url')
        defaults.add('region_name')
        defaults.add('cache')
        defaults.add('auth_token')
        defaults.add('insecure')
        defaults.add('endpoint_type')
        defaults.add('cacert')
        defaults.add('auth_type')

        self.defaults = defaults

        # use a config file if it exists where expected
        self.cloud_config = self._load_config_file()
        if not self.cloud_config:
            self.cloud_config = dict(
                clouds=dict(openstack=dict(self.defaults)))

        self._cache_max_age = 300
        self._cache_path = CACHE_PATH
        if 'cache' in self.cloud_config:
            self._cache_max_age = self.cloud_config['cache'].get(
                'max_age', self._cache_max_age)
            self._cache_path = os.path.expanduser(
                self.cloud_config['cache'].get('path', self._cache_path))

    def _load_config_file(self):
        for path in self._config_files:
            if os.path.exists(path):
                return yaml.load(open(path, 'r'))

    def _load_vendor_file(self):
        for path in self._vendor_files:
            if os.path.exists(path):
                return yaml.load(open(path, 'r'))

    def get_cache_max_age(self):
        return self._cache_max_age

    def get_cache_path(self):
        return self._cache_path

    def _get_regions(self, cloud):
        try:
            return self.cloud_config['clouds'][cloud]['region_name']
        except KeyError:
            # No region configured
            return ''

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

        # Get the defaults (including env vars) first
        cloud.update(self.defaults)

        # yes, I know the next line looks silly
        if 'cloud' in our_cloud:
            cloud_name = our_cloud['cloud']
            vendor_file = self._load_vendor_file()
            if vendor_file and cloud_name in vendor_file['public-clouds']:
                cloud.update(vendor_file['public-clouds'][cloud_name])
            else:
                try:
                    cloud.update(vendors.CLOUD_DEFAULTS[cloud_name])
                except KeyError:
                    # Can't find the requested vendor config, go about business
                    pass

        cloud.update(our_cloud)
        if 'cloud' in cloud:
            del cloud['cloud']

        return self._fix_project_madness(cloud)

    def _fix_project_madness(self, cloud):
        project_name = None
        # Do the list backwards so that project_name is the ultimate winner
        for key in ('tenant_id', 'project_id', 'tenant_name', 'project_name'):
            if key in cloud:
                project_name = cloud[key]
                del cloud[key]
        cloud['project_name'] = project_name
        return cloud

    def get_all_clouds(self):

        clouds = []

        for cloud in self._get_cloud_sections():
            for region in self._get_regions(cloud).split(','):
                clouds.append(self.get_one_cloud(cloud, region_name=region))
        return clouds

    def _fix_args(self, args, argparse=None):
        """Massage the passed-in options

        Replace - with _ and strip os_ prefixes.

        Convert an argparse Namespace object to a dict, removing values
        that are either None or ''.
        """

        if argparse:
            # Convert the passed-in Namespace
            o_dict = vars(argparse)
            parsed_args = dict()
            for k in o_dict:
                if o_dict[k] is not None and o_dict[k] != '':
                    parsed_args[k] = o_dict[k]
            args.update(parsed_args)

        os_args = dict()
        new_args = dict()
        for (key, val) in args.iteritems():
            key = key.replace('-', '_')
            if key.startswith('os'):
                os_args[key[3:]] = val
            else:
                new_args[key] = val
        new_args.update(os_args)
        return new_args

    def get_one_cloud(self, cloud=None, validate=True,
                      argparse=None, **kwargs):
        """Retrieve a single cloud configuration and merge additional options

        :param string cloud:
            The name of the configuration to load from clouds.yaml
        :param boolean validate:
            Validate that required arguments are present and certain
            argument combinations are valid
        :param Namespace argparse:
            An argparse Namespace object; allows direct passing in of
            argparse options to be added to the cloud config.  Values
            of None and '' will be removed.
        :param kwargs: Additional configuration options
        """

        args = self._fix_args(kwargs, argparse=argparse)

        if cloud:
            name = cloud
        else:
            name = 'openstack'

        if 'region_name' not in args:
            args['region_name'] = self._get_region(name)

        config = self._get_base_cloud_config(name)

        # Can't just do update, because None values take over
        for (key, val) in args.iteritems():
            if val is not None:
                config[key] = val

        for key in BOOL_KEYS:
            if key in config:
                if type(config[key]) is not bool:
                    config[key] = get_boolean(config[key])

        if validate:
            for key in REQUIRED_VALUES:
                if key not in config or not config[key]:
                    raise exceptions.OpenStackConfigException(
                        'Unable to find full auth information for cloud'
                        ' {name} in config files {files}'
                        ' or environment variables.'.format(
                            name=name, files=','.join(self._config_files)))
            if 'project_name' not in config and 'project_id' not in config:
                raise exceptions.OpenStackConfigException(
                    'Neither project_name or project_id information found'
                    ' for cloud {name} in config files {files}'
                    ' or environment variables.'.format(
                        name=name, files=','.join(self._config_files)))

        # If any of the defaults reference other values, we need to expand
        for (key, value) in config.items():
            if hasattr(value, 'format'):
                config[key] = value.format(**config)

        return cloud_config.CloudConfig(
            name=name, region=config['region_name'], config=config)

if __name__ == '__main__':
    config = OpenStackConfig().get_all_clouds()
    for cloud in config:
        print(cloud.name, cloud.region, cloud.config)
