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
import warnings

import appdirs
import yaml

try:
    import keystoneclient.auth as ksc_auth
except ImportError:
    ksc_auth = None

from os_client_config import cloud_config
from os_client_config import defaults
from os_client_config import exceptions
from os_client_config import vendors

APPDIRS = appdirs.AppDirs('openstack', 'OpenStack', multipath='/etc')
CONFIG_HOME = APPDIRS.user_config_dir
CACHE_PATH = APPDIRS.user_cache_dir

UNIX_CONFIG_HOME = os.path.join(
    os.path.expanduser(os.path.join('~', '.config')), 'openstack')
UNIX_SITE_CONFIG_HOME = '/etc/openstack'

SITE_CONFIG_HOME = APPDIRS.site_config_dir

CONFIG_SEARCH_PATH = [
    os.getcwd(),
    CONFIG_HOME, UNIX_CONFIG_HOME,
    SITE_CONFIG_HOME, UNIX_SITE_CONFIG_HOME
]
YAML_SUFFIXES = ('.yaml', '.yml')
CONFIG_FILES = [
    os.path.join(d, 'clouds' + s)
    for d in CONFIG_SEARCH_PATH
    for s in YAML_SUFFIXES
]
VENDOR_FILES = [
    os.path.join(d, 'clouds-public' + s)
    for d in CONFIG_SEARCH_PATH
    for s in YAML_SUFFIXES
]

BOOL_KEYS = ('insecure', 'cache')


# NOTE(dtroyer): This turns out to be not the best idea so let's move
#                overriding defaults to a kwarg to OpenStackConfig.__init__()
#                Remove this sometime in June 2015 once OSC is comfortably
#                changed-over and global-defaults is updated.
def set_default(key, value):
    defaults._defaults[key] = value


def get_boolean(value):
    if value.lower() == 'true':
        return True
    return False


def _get_os_environ():
    ret = defaults.get_defaults()
    environkeys = [k for k in os.environ.keys() if k.startswith('OS_')]
    if not environkeys:
        return None
    for k in environkeys:
        newkey = k[3:].lower()
        ret[newkey] = os.environ[k]
    return ret


def _auth_update(old_dict, new_dict):
    """Like dict.update, except handling the nested dict called auth."""
    for (k, v) in new_dict.items():
        if k == 'auth':
            if k in old_dict:
                old_dict[k].update(v)
            else:
                old_dict[k] = v.copy()
        else:
            old_dict[k] = v
    return old_dict


class OpenStackConfig(object):

    def __init__(self, config_files=None, vendor_files=None,
                 override_defaults=None):
        self._config_files = config_files or CONFIG_FILES
        self._vendor_files = vendor_files or VENDOR_FILES

        self.defaults = defaults.get_defaults()
        if override_defaults:
            self.defaults.update(override_defaults)

        # First, use a config file if it exists where expected
        self.config_filename, self.cloud_config = self._load_config_file()

        if not self.cloud_config:
            self.cloud_config = {'clouds': {}}
        if 'clouds' not in self.cloud_config:
            self.cloud_config['clouds'] = {}

        # Next, process environment variables and add them to the mix
        self.envvar_key = os.environ.pop('OS_CLOUD_NAME', 'envvars')
        if self.envvar_key in self.cloud_config['clouds']:
            raise exceptions.OpenStackConfigException(
                '"{0}" defines a cloud named "{1}", but'
                ' OS_CLOUD_NAME is also set to "{1}". Please rename'
                ' either your environment based cloud, or one of your'
                ' file-based clouds.'.format(self.config_filename,
                                             self.envvar_key))

        envvars = _get_os_environ()
        if envvars:
            self.cloud_config['clouds'][self.envvar_key] = envvars

        # Finally, fall through and make a cloud that starts with defaults
        # because we need somewhere to put arguments, and there are neither
        # config files or env vars
        if not self.cloud_config['clouds']:
            self.cloud_config = dict(
                clouds=dict(defaults=dict(self.defaults)))

        self._cache_max_age = 0
        self._cache_path = CACHE_PATH
        self._cache_class = 'dogpile.cache.null'
        self._cache_arguments = {}
        if 'cache' in self.cloud_config:
            self._cache_max_age = self.cloud_config['cache'].get(
                'max_age', self._cache_max_age)
            if self._cache_max_age:
                self._cache_class = 'dogpile.cache.memory'
            self._cache_path = os.path.expanduser(
                self.cloud_config['cache'].get('path', self._cache_path))
            self._cache_class = self.cloud_config['cache'].get(
                'class', self._cache_class)
            self._cache_arguments = self.cloud_config['cache'].get(
                'arguments', self._cache_arguments)

    def _load_config_file(self):
        return self._load_yaml_file(self._config_files)

    def _load_vendor_file(self):
        return self._load_yaml_file(self._vendor_files)

    def _load_yaml_file(self, filelist):
        for path in filelist:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return path, yaml.safe_load(f)
        return (None, None)

    def _normalize_keys(self, config):
        new_config = {}
        for key, value in config.items():
            key = key.replace('-', '_')
            if isinstance(value, dict):
                new_config[key] = self._normalize_keys(value)
            else:
                new_config[key] = value
        return new_config

    def get_cache_max_age(self):
        return self._cache_max_age

    def get_cache_path(self):
        return self._cache_path

    def get_cache_class(self):
        return self._cache_class

    def get_cache_arguments(self):
        return self._cache_arguments

    def _get_regions(self, cloud):
        try:
            return self.cloud_config['clouds'][cloud]['region_name']
        except KeyError:
            # No region configured
            return ''

    def _get_region(self, cloud=None):
        return self._get_regions(cloud).split(',')[0]

    def get_cloud_names(self):
        return self.cloud_config['clouds'].keys()

    def _get_base_cloud_config(self, name):
        cloud = dict()

        # Only validate cloud name if one was given
        if name and name not in self.cloud_config['clouds']:
            raise exceptions.OpenStackConfigException(
                "Named cloud {name} requested that was not found.".format(
                    name=name))

        our_cloud = self.cloud_config['clouds'].get(name, dict())

        # Get the defaults
        cloud.update(self.defaults)

        # Expand a profile if it exists. 'cloud' is an old confusing name
        # for this.
        profile_name = our_cloud.get('profile', our_cloud.get('cloud', None))
        if profile_name:
            if 'cloud' in our_cloud:
                warnings.warn(
                    "{0} use the keyword 'cloud' to reference a known "
                    "vendor profile. This has been deprecated in favor of the "
                    "'profile' keyword.".format(self.config_filename))
            vendor_filename, vendor_file = self._load_vendor_file()
            if vendor_file and profile_name in vendor_file['public-clouds']:
                _auth_update(cloud, vendor_file['public-clouds'][profile_name])
            else:
                try:
                    _auth_update(cloud, vendors.CLOUD_DEFAULTS[profile_name])
                except KeyError:
                    # Can't find the requested vendor config, go about business
                    warnings.warn("Couldn't find the vendor profile '{0}', for"
                                  " the cloud '{1}'".format(profile_name,
                                                            name))

        if 'auth' not in cloud:
            cloud['auth'] = dict()

        _auth_update(cloud, our_cloud)
        if 'cloud' in cloud:
            del cloud['cloud']

        return self._fix_backwards_madness(cloud)

    def _fix_backwards_madness(self, cloud):
        cloud = self._fix_backwards_project(cloud)
        cloud = self._fix_backwards_auth_plugin(cloud)
        return cloud

    def _fix_backwards_project(self, cloud):
        # Do the lists backwards so that project_name is the ultimate winner
        mappings = {
            'project_name': ('tenant_id', 'project_id',
                             'tenant_name', 'project_name'),
        }
        for target_key, possible_values in mappings.items():
            target = None
            for key in possible_values:
                if key in cloud:
                    target = str(cloud[key])
                    del cloud[key]
                if key in cloud['auth']:
                    target = str(cloud['auth'][key])
                    del cloud['auth'][key]
            if target:
                cloud['auth'][target_key] = target
        return cloud

    def _fix_backwards_auth_plugin(self, cloud):
        # Do the lists backwards so that auth_type is the ultimate winner
        mappings = {
            'auth_type': ('auth_plugin', 'auth_type'),
        }
        for target_key, possible_values in mappings.items():
            target = None
            for key in possible_values:
                if key in cloud:
                    target = cloud[key]
                    del cloud[key]
            cloud[target_key] = target
        return cloud

    def get_all_clouds(self):

        clouds = []

        for cloud in self.get_cloud_names():
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
        for (key, val) in iter(args.items()):
            key = key.replace('-', '_')
            if key.startswith('os'):
                os_args[key[3:]] = val
            else:
                new_args[key] = val
        new_args.update(os_args)
        return new_args

    def _find_winning_auth_value(self, opt, config):
        opt_name = opt.name.replace('-', '_')
        if opt_name in config:
            return config[opt_name]
        else:
            for d_opt in opt.deprecated_opts:
                d_opt_name = d_opt.name.replace('-', '_')
                if d_opt_name in config:
                    return config[d_opt_name]

    def _validate_auth(self, config):
        # May throw a keystoneclient.exceptions.NoMatchingPlugin
        plugin_options = ksc_auth.get_plugin_class(
            config['auth_type']).get_options()

        for p_opt in plugin_options:
            # if it's in config.auth, win, kill it from config dict
            # if it's in config and not in config.auth, move it
            # deprecated loses to current
            # provided beats default, deprecated or not
            winning_value = self._find_winning_auth_value(
                p_opt, config['auth'])
            if not winning_value:
                winning_value = self._find_winning_auth_value(p_opt, config)

            # if the plugin tells us that this value is required
            # then error if it's doesn't exist now
            if not winning_value and p_opt.required:
                raise exceptions.OpenStackConfigException(
                    'Unable to find auth information for cloud'
                    ' {cloud} in config files {files}'
                    ' or environment variables. Missing value {auth_key}'
                    ' required for auth plugin {plugin}'.format(
                        cloud=cloud, files=','.join(self._config_files),
                        auth_key=p_opt.name, plugin=config.get('auth_type')))

            # Clean up after ourselves
            for opt in [p_opt.name] + [o.name for o in p_opt.deprecated_opts]:
                opt = opt.replace('-', '_')
                config.pop(opt, None)
                config['auth'].pop(opt, None)

            if winning_value:
                # Prefer the plugin configuration dest value if the value's key
                # is marked as depreciated.
                if p_opt.dest is None:
                    config['auth'][p_opt.name.replace('-', '_')] = (
                        winning_value)
                else:
                    config['auth'][p_opt.dest] = winning_value

        return config

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

        if cloud is None and self.envvar_key in self.get_cloud_names():
            cloud = self.envvar_key

        args = self._fix_args(kwargs, argparse=argparse)

        if 'region_name' not in args or args['region_name'] is None:
            args['region_name'] = self._get_region(cloud)

        config = self._get_base_cloud_config(cloud)

        # Can't just do update, because None values take over
        for (key, val) in iter(args.items()):
            if val is not None:
                if key == 'auth' and config[key] is not None:
                    config[key] = _auth_update(config[key], val)
                else:
                    config[key] = val

        for key in BOOL_KEYS:
            if key in config:
                if type(config[key]) is not bool:
                    config[key] = get_boolean(config[key])

        if 'auth_type' in config:
            if config['auth_type'] in ('', 'None', None):
                validate = False

        if validate and ksc_auth:
            config = self._validate_auth(config)

        # If any of the defaults reference other values, we need to expand
        for (key, value) in config.items():
            if hasattr(value, 'format'):
                config[key] = value.format(**config)

        if cloud is None:
            cloud_name = ''
        else:
            cloud_name = str(cloud)
        return cloud_config.CloudConfig(
            name=cloud_name, region=config['region_name'],
            config=self._normalize_keys(config))

    @staticmethod
    def set_one_cloud(config_file, cloud, set_config=None):
        """Set a single cloud configuration.

        :param string config_file:
            The path to the config file to edit. If this file does not exist
            it will be created.
        :param string cloud:
            The name of the configuration to save to clouds.yaml
        :param dict set_config: Configuration options to be set
        """

        set_config = set_config or {}
        cur_config = {}
        try:
            with open(config_file) as fh:
                cur_config = yaml.safe_load(fh)
        except IOError as e:
            # Not no such file
            if e.errno != 2:
                raise
            pass

        clouds_config = cur_config.get('clouds', {})
        cloud_config = _auth_update(clouds_config.get(cloud, {}), set_config)
        clouds_config[cloud] = cloud_config
        cur_config['clouds'] = clouds_config

        with open(config_file, 'w') as fh:
            yaml.safe_dump(cur_config, fh, default_flow_style=False)

if __name__ == '__main__':
    config = OpenStackConfig().get_all_clouds()
    for cloud in config:
        print(cloud.name, cloud.region, cloud.config)
