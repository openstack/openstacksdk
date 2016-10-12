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


# alias because we already had an option named argparse
import argparse as argparse_mod
import collections
import copy
import json
import os
import sys
import warnings

import appdirs
from keystoneauth1 import adapter
from keystoneauth1 import loading
import yaml

from os_client_config import _log
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
JSON_SUFFIXES = ('.json',)
CONFIG_FILES = [
    os.path.join(d, 'clouds' + s)
    for d in CONFIG_SEARCH_PATH
    for s in YAML_SUFFIXES + JSON_SUFFIXES
]
SECURE_FILES = [
    os.path.join(d, 'secure' + s)
    for d in CONFIG_SEARCH_PATH
    for s in YAML_SUFFIXES + JSON_SUFFIXES
]
VENDOR_FILES = [
    os.path.join(d, 'clouds-public' + s)
    for d in CONFIG_SEARCH_PATH
    for s in YAML_SUFFIXES + JSON_SUFFIXES
]

BOOL_KEYS = ('insecure', 'cache')


# NOTE(dtroyer): This turns out to be not the best idea so let's move
#                overriding defaults to a kwarg to OpenStackConfig.__init__()
#                Remove this sometime in June 2015 once OSC is comfortably
#                changed-over and global-defaults is updated.
def set_default(key, value):
    warnings.warn(
        "Use of set_default() is deprecated. Defaults should be set with the "
        "`override_defaults` parameter of OpenStackConfig."
    )
    defaults.get_defaults()  # make sure the dict is initialized
    defaults._defaults[key] = value


def get_boolean(value):
    if value is None:
        return False
    if type(value) is bool:
        return value
    if value.lower() == 'true':
        return True
    return False


def _get_os_environ(envvar_prefix=None):
    ret = defaults.get_defaults()
    if not envvar_prefix:
        # This makes the or below be OS_ or OS_ which is a no-op
        envvar_prefix = 'OS_'
    environkeys = [k for k in os.environ.keys()
                   if (k.startswith('OS_') or k.startswith(envvar_prefix))
                   and not k.startswith('OS_TEST')  # infra CI var
                   and not k.startswith('OS_STD')   # infra CI var
                   ]
    for k in environkeys:
        newkey = k.split('_', 1)[-1].lower()
        ret[newkey] = os.environ[k]
    # If the only environ keys are cloud and region_name, don't return anything
    # because they are cloud selectors
    if set(environkeys) - set(['OS_CLOUD', 'OS_REGION_NAME']):
        return ret
    return None


def _merge_clouds(old_dict, new_dict):
    """Like dict.update, except handling nested dicts."""
    ret = old_dict.copy()
    for (k, v) in new_dict.items():
        if isinstance(v, dict):
            if k in ret:
                ret[k] = _merge_clouds(ret[k], v)
            else:
                ret[k] = v.copy()
        else:
            ret[k] = v
    return ret


def _auth_update(old_dict, new_dict_source):
    """Like dict.update, except handling the nested dict called auth."""
    new_dict = copy.deepcopy(new_dict_source)
    for (k, v) in new_dict.items():
        if k == 'auth':
            if k in old_dict:
                old_dict[k].update(v)
            else:
                old_dict[k] = v.copy()
        else:
            old_dict[k] = v
    return old_dict


def _fix_argv(argv):
    # Transform any _ characters in arg names to - so that we don't
    # have to throw billions of compat argparse arguments around all
    # over the place.
    processed = collections.defaultdict(list)
    for index in range(0, len(argv)):
        if argv[index].startswith('--'):
            split_args = argv[index].split('=')
            orig = split_args[0]
            new = orig.replace('_', '-')
            if orig != new:
                split_args[0] = new
                argv[index] = "=".join(split_args)
            # Save both for later so we can throw an error about dupes
            processed[new].append(orig)
    overlap = []
    for new, old in processed.items():
        if len(old) > 1:
            overlap.extend(old)
    if overlap:
        raise exceptions.OpenStackConfigException(
            "The following options were given: '{options}' which contain"
            " duplicates except that one has _ and one has -. There is"
            " no sane way for us to know what you're doing. Remove the"
            " duplicate option and try again".format(
                options=','.join(overlap)))


class OpenStackConfig(object):

    def __init__(self, config_files=None, vendor_files=None,
                 override_defaults=None, force_ipv4=None,
                 envvar_prefix=None, secure_files=None,
                 pw_func=None, session_constructor=None):
        self.log = _log.setup_logging(__name__)
        self._session_constructor = session_constructor

        self._config_files = config_files or CONFIG_FILES
        self._secure_files = secure_files or SECURE_FILES
        self._vendor_files = vendor_files or VENDOR_FILES

        config_file_override = os.environ.pop('OS_CLIENT_CONFIG_FILE', None)
        if config_file_override:
            self._config_files.insert(0, config_file_override)

        secure_file_override = os.environ.pop('OS_CLIENT_SECURE_FILE', None)
        if secure_file_override:
            self._secure_files.insert(0, secure_file_override)

        self.defaults = defaults.get_defaults()
        if override_defaults:
            self.defaults.update(override_defaults)

        # First, use a config file if it exists where expected
        self.config_filename, self.cloud_config = self._load_config_file()
        _, secure_config = self._load_secure_file()
        if secure_config:
            self.cloud_config = _merge_clouds(
                self.cloud_config, secure_config)

        if not self.cloud_config:
            self.cloud_config = {'clouds': {}}
        if 'clouds' not in self.cloud_config:
            self.cloud_config['clouds'] = {}

        # Grab ipv6 preference settings from env
        client_config = self.cloud_config.get('client', {})

        if force_ipv4 is not None:
            # If it's passed in to the constructor, honor it.
            self.force_ipv4 = force_ipv4
        else:
            # Get the backwards compat value
            prefer_ipv6 = get_boolean(
                os.environ.pop(
                    'OS_PREFER_IPV6', client_config.get(
                        'prefer_ipv6', client_config.get(
                            'prefer-ipv6', True))))
            force_ipv4 = get_boolean(
                os.environ.pop(
                    'OS_FORCE_IPV4', client_config.get(
                        'force_ipv4', client_config.get(
                            'broken-ipv6', False))))

            self.force_ipv4 = force_ipv4
            if not prefer_ipv6:
                # this will only be false if someone set it explicitly
                # honor their wishes
                self.force_ipv4 = True

        # Next, process environment variables and add them to the mix
        self.envvar_key = os.environ.pop('OS_CLOUD_NAME', 'envvars')
        if self.envvar_key in self.cloud_config['clouds']:
            raise exceptions.OpenStackConfigException(
                '"{0}" defines a cloud named "{1}", but'
                ' OS_CLOUD_NAME is also set to "{1}". Please rename'
                ' either your environment based cloud, or one of your'
                ' file-based clouds.'.format(self.config_filename,
                                             self.envvar_key))
        # Pull out OS_CLOUD so that if it's the only thing set, do not
        # make an envvars cloud
        self.default_cloud = os.environ.pop('OS_CLOUD', None)

        envvars = _get_os_environ(envvar_prefix=envvar_prefix)
        if envvars:
            self.cloud_config['clouds'][self.envvar_key] = envvars
            if not self.default_cloud:
                self.default_cloud = self.envvar_key

        # Finally, fall through and make a cloud that starts with defaults
        # because we need somewhere to put arguments, and there are neither
        # config files or env vars
        if not self.cloud_config['clouds']:
            self.cloud_config = dict(
                clouds=dict(defaults=dict(self.defaults)))
            self.default_cloud = 'defaults'

        self._cache_expiration_time = 0
        self._cache_path = CACHE_PATH
        self._cache_class = 'dogpile.cache.null'
        self._cache_arguments = {}
        self._cache_expiration = {}
        if 'cache' in self.cloud_config:
            cache_settings = self._normalize_keys(self.cloud_config['cache'])

            # expiration_time used to be 'max_age' but the dogpile setting
            # is expiration_time. Support max_age for backwards compat.
            self._cache_expiration_time = cache_settings.get(
                'expiration_time', cache_settings.get(
                    'max_age', self._cache_expiration_time))

            # If cache class is given, use that. If not, but if cache time
            # is given, default to memory. Otherwise, default to nothing.
            # to memory.
            if self._cache_expiration_time:
                self._cache_class = 'dogpile.cache.memory'
            self._cache_class = self.cloud_config['cache'].get(
                'class', self._cache_class)

            self._cache_path = os.path.expanduser(
                cache_settings.get('path', self._cache_path))
            self._cache_arguments = cache_settings.get(
                'arguments', self._cache_arguments)
            self._cache_expiration = cache_settings.get(
                'expiration', self._cache_expiration)

        # Flag location to hold the peeked value of an argparse timeout value
        self._argv_timeout = False

        # Save the password callback
        # password = self._pw_callback(prompt="Password: ")
        self._pw_callback = pw_func

    def get_extra_config(self, key, defaults=None):
        """Fetch an arbitrary extra chunk of config, laying in defaults.

        :param string key: name of the config section to fetch
        :param dict defaults: (optional) default values to merge under the
                                         found config
        """
        if not defaults:
            defaults = {}
        return _merge_clouds(
            self._normalize_keys(defaults),
            self._normalize_keys(self.cloud_config.get(key, {})))

    def _load_config_file(self):
        return self._load_yaml_json_file(self._config_files)

    def _load_secure_file(self):
        return self._load_yaml_json_file(self._secure_files)

    def _load_vendor_file(self):
        return self._load_yaml_json_file(self._vendor_files)

    def _load_yaml_json_file(self, filelist):
        for path in filelist:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    if path.endswith('json'):
                        return path, json.load(f)
                    else:
                        return path, yaml.safe_load(f)
        return (None, {})

    def _normalize_keys(self, config):
        new_config = {}
        for key, value in config.items():
            key = key.replace('-', '_')
            if isinstance(value, dict):
                new_config[key] = self._normalize_keys(value)
            elif isinstance(value, bool):
                new_config[key] = value
            elif isinstance(value, int) and key != 'verbose_level':
                new_config[key] = str(value)
            elif isinstance(value, float):
                new_config[key] = str(value)
            else:
                new_config[key] = value
        return new_config

    def get_cache_expiration_time(self):
        return int(self._cache_expiration_time)

    def get_cache_interval(self):
        return self.get_cache_expiration_time()

    def get_cache_max_age(self):
        return self.get_cache_expiration_time()

    def get_cache_path(self):
        return self._cache_path

    def get_cache_class(self):
        return self._cache_class

    def get_cache_arguments(self):
        return copy.deepcopy(self._cache_arguments)

    def get_cache_expiration(self):
        return copy.deepcopy(self._cache_expiration)

    def _expand_region_name(self, region_name):
        return {'name': region_name, 'values': {}}

    def _expand_regions(self, regions):
        ret = []
        for region in regions:
            if isinstance(region, dict):
                ret.append(copy.deepcopy(region))
            else:
                ret.append(self._expand_region_name(region))
        return ret

    def _get_regions(self, cloud):
        if cloud not in self.cloud_config['clouds']:
            return [self._expand_region_name('')]
        regions = self._get_known_regions(cloud)
        if not regions:
            # We don't know of any regions use a workable default.
            regions = [self._expand_region_name('')]
        return regions

    def _get_known_regions(self, cloud):
        config = self._normalize_keys(self.cloud_config['clouds'][cloud])
        if 'regions' in config:
            return self._expand_regions(config['regions'])
        elif 'region_name' in config:
            if isinstance(config['region_name'], list):
                regions = config['region_name']
            else:
                regions = config['region_name'].split(',')
            if len(regions) > 1:
                warnings.warn(
                    "Comma separated lists in region_name are deprecated."
                    " Please use a yaml list in the regions"
                    " parameter in {0} instead.".format(self.config_filename))
            return self._expand_regions(regions)
        else:
            # crappit. we don't have a region defined.
            new_cloud = dict()
            our_cloud = self.cloud_config['clouds'].get(cloud, dict())
            self._expand_vendor_profile(cloud, new_cloud, our_cloud)
            if 'regions' in new_cloud and new_cloud['regions']:
                return self._expand_regions(new_cloud['regions'])
            elif 'region_name' in new_cloud and new_cloud['region_name']:
                return [self._expand_region_name(new_cloud['region_name'])]

    def _get_region(self, cloud=None, region_name=''):
        if region_name is None:
            region_name = ''
        if not cloud:
            return self._expand_region_name(region_name)

        regions = self._get_known_regions(cloud)
        if not regions:
            return self._expand_region_name(region_name)

        if not region_name:
            return regions[0]

        for region in regions:
            if region['name'] == region_name:
                return region

        raise exceptions.OpenStackConfigException(
            'Region {region_name} is not a valid region name for cloud'
            ' {cloud}. Valid choices are {region_list}. Please note that'
            ' region names are case sensitive.'.format(
                region_name=region_name,
                region_list=','.join([r['name'] for r in regions]),
                cloud=cloud))

    def get_cloud_names(self):
        return self.cloud_config['clouds'].keys()

    def _get_base_cloud_config(self, name):
        cloud = dict()

        # Only validate cloud name if one was given
        if name and name not in self.cloud_config['clouds']:
            raise exceptions.OpenStackConfigException(
                "Cloud {name} was not found.".format(
                    name=name))

        our_cloud = self.cloud_config['clouds'].get(name, dict())

        # Get the defaults
        cloud.update(self.defaults)
        self._expand_vendor_profile(name, cloud, our_cloud)

        if 'auth' not in cloud:
            cloud['auth'] = dict()

        _auth_update(cloud, our_cloud)
        if 'cloud' in cloud:
            del cloud['cloud']

        return cloud

    def _expand_vendor_profile(self, name, cloud, our_cloud):
        # Expand a profile if it exists. 'cloud' is an old confusing name
        # for this.
        profile_name = our_cloud.get('profile', our_cloud.get('cloud', None))
        if profile_name and profile_name != self.envvar_key:
            if 'cloud' in our_cloud:
                warnings.warn(
                    "{0} use the keyword 'cloud' to reference a known "
                    "vendor profile. This has been deprecated in favor of the "
                    "'profile' keyword.".format(self.config_filename))
            vendor_filename, vendor_file = self._load_vendor_file()
            if vendor_file and profile_name in vendor_file['public-clouds']:
                _auth_update(cloud, vendor_file['public-clouds'][profile_name])
            else:
                profile_data = vendors.get_profile(profile_name)
                if profile_data:
                    status = profile_data.pop('status', 'active')
                    message = profile_data.pop('message', '')
                    if status == 'deprecated':
                        warnings.warn(
                            "{profile_name} is deprecated: {message}".format(
                                profile_name=profile_name, message=message))
                    elif status == 'shutdown':
                        raise exceptions.OpenStackConfigException(
                            "{profile_name} references a cloud that no longer"
                            " exists: {message}".format(
                                profile_name=profile_name, message=message))
                    _auth_update(cloud, profile_data)
                else:
                    # Can't find the requested vendor config, go about business
                    warnings.warn("Couldn't find the vendor profile '{0}', for"
                                  " the cloud '{1}'".format(profile_name,
                                                            name))

    def _project_scoped(self, cloud):
        return ('project_id' in cloud or 'project_name' in cloud
                or 'project_id' in cloud['auth']
                or 'project_name' in cloud['auth'])

    def _validate_networks(self, networks, key):
        value = None
        for net in networks:
            if value and net[key]:
                raise exceptions.OpenStackConfigException(
                    "Duplicate network entries for {key}: {net1} and {net2}."
                    " Only one network can be flagged with {key}".format(
                        key=key,
                        net1=value['name'],
                        net2=net['name']))
            if not value and net[key]:
                value = net

    def _fix_backwards_networks(self, cloud):
        # Leave the external_network and internal_network keys in the
        # dict because consuming code might be expecting them.
        networks = []
        # Normalize existing network entries
        for net in cloud.get('networks', []):
            name = net.get('name')
            if not name:
                raise exceptions.OpenStackConfigException(
                    'Entry in network list is missing required field "name".')
            network = dict(
                name=name,
                routes_externally=get_boolean(net.get('routes_externally')),
                nat_destination=get_boolean(net.get('nat_destination')),
                default_interface=get_boolean(net.get('default_interface')),
            )
            # routes_ipv4_externally defaults to the value of routes_externally
            network['routes_ipv4_externally'] = get_boolean(
                net.get(
                    'routes_ipv4_externally', network['routes_externally']))
            # routes_ipv6_externally defaults to the value of routes_externally
            network['routes_ipv6_externally'] = get_boolean(
                net.get(
                    'routes_ipv6_externally', network['routes_externally']))
            networks.append(network)

        for key in ('external_network', 'internal_network'):
            external = key.startswith('external')
            if key in cloud and 'networks' in cloud:
                raise exceptions.OpenStackConfigException(
                    "Both {key} and networks were specified in the config."
                    " Please remove {key} from the config and use the network"
                    " list to configure network behavior.".format(key=key))
            if key in cloud:
                warnings.warn(
                    "{key} is deprecated. Please replace with an entry in"
                    " a dict inside of the networks list with name: {name}"
                    " and routes_externally: {external}".format(
                        key=key, name=cloud[key], external=external))
                networks.append(dict(
                    name=cloud[key],
                    routes_externally=external,
                    nat_destination=not external,
                    default_interface=external))

        # Validate that we don't have duplicates
        self._validate_networks(networks, 'nat_destination')
        self._validate_networks(networks, 'default_interface')

        cloud['networks'] = networks
        return cloud

    def _handle_domain_id(self, cloud):
        # Allow people to just specify domain once if it's the same
        mappings = {
            'domain_id': ('user_domain_id', 'project_domain_id'),
            'domain_name': ('user_domain_name', 'project_domain_name'),
        }
        for target_key, possible_values in mappings.items():
            if not self._project_scoped(cloud):
                if target_key in cloud and target_key not in cloud['auth']:
                    cloud['auth'][target_key] = cloud.pop(target_key)
                continue
            for key in possible_values:
                if target_key in cloud['auth'] and key not in cloud['auth']:
                    cloud['auth'][key] = cloud['auth'][target_key]
            cloud.pop(target_key, None)
            cloud['auth'].pop(target_key, None)
        return cloud

    def _fix_backwards_project(self, cloud):
        # Do the lists backwards so that project_name is the ultimate winner
        # Also handle moving domain names into auth so that domain mapping
        # is easier
        mappings = {
            'domain_id': ('domain_id', 'domain-id'),
            'domain_name': ('domain_name', 'domain-name'),
            'user_domain_id': ('user_domain_id', 'user-domain-id'),
            'user_domain_name': ('user_domain_name', 'user-domain-name'),
            'project_domain_id': ('project_domain_id', 'project-domain-id'),
            'project_domain_name': (
                'project_domain_name', 'project-domain-name'),
            'token': ('auth-token', 'auth_token', 'token'),
        }
        if cloud.get('auth_type', None) == 'v2password':
            # If v2password is explcitly requested, this is to deal with old
            # clouds. That's fine - we need to map settings in the opposite
            # direction
            mappings['tenant_id'] = (
                'project_id', 'project-id', 'tenant_id', 'tenant-id')
            mappings['tenant_name'] = (
                'project_name', 'project-name', 'tenant_name', 'tenant-name')
        else:
            mappings['project_id'] = (
                'tenant_id', 'tenant-id', 'project_id', 'project-id')
            mappings['project_name'] = (
                'tenant_name', 'tenant-name', 'project_name', 'project-name')
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
        # Because we force alignment to v3 nouns, we want to force
        # use of the auth plugin that can do auto-selection and dealing
        # with that based on auth parameters. v2password is basically
        # completely broken
        return cloud

    def register_argparse_arguments(self, parser, argv, service_keys=None):
        """Register all of the common argparse options needed.

        Given an argparse parser, register the keystoneauth Session arguments,
        the keystoneauth Auth Plugin Options and os-cloud. Also, peek in the
        argv to see if all of the auth plugin options should be registered
        or merely the ones already configured.
        :param argparse.ArgumentParser: parser to attach argparse options to
        :param list argv: the arguments provided to the application
        :param string service_keys: Service or list of services this argparse
                                    should be specialized for, if known.
                                    The first item in the list will be used
                                    as the default value for service_type
                                    (optional)

        :raises exceptions.OpenStackConfigException if an invalid auth-type
                                                    is requested
        """

        if service_keys is None:
            service_keys = []

        # Fix argv in place - mapping any keys with embedded _ in them to -
        _fix_argv(argv)

        local_parser = argparse_mod.ArgumentParser(add_help=False)

        for p in (parser, local_parser):
            p.add_argument(
                '--os-cloud',
                metavar='<name>',
                default=os.environ.get('OS_CLOUD', None),
                help='Named cloud to connect to')

        # we need to peek to see if timeout was actually passed, since
        # the keystoneauth declaration of it has a default, which means
        # we have no clue if the value we get is from the ksa default
        # for from the user passing it explicitly. We'll stash it for later
        local_parser.add_argument('--timeout', metavar='<timeout>')

        # We need for get_one_cloud to be able to peek at whether a token
        # was passed so that we can swap the default from password to
        # token if it was. And we need to also peek for --os-auth-token
        # for novaclient backwards compat
        local_parser.add_argument('--os-token')
        local_parser.add_argument('--os-auth-token')

        # Peek into the future and see if we have an auth-type set in
        # config AND a cloud set, so that we know which command line
        # arguments to register and show to the user (the user may want
        # to say something like:
        #   openstack --os-cloud=foo --os-oidctoken=bar
        # although I think that user is the cause of my personal pain
        options, _args = local_parser.parse_known_args(argv)
        if options.timeout:
            self._argv_timeout = True

        # validate = False because we're not _actually_ loading here
        # we're only peeking, so it's the wrong time to assert that
        # the rest of the arguments given are invalid for the plugin
        # chosen (for instance, --help may be requested, so that the
        # user can see what options he may want to give
        cloud = self.get_one_cloud(argparse=options, validate=False)
        default_auth_type = cloud.config['auth_type']

        try:
            loading.register_auth_argparse_arguments(
                parser, argv, default=default_auth_type)
        except Exception:
            # Hidiing the keystoneauth exception because we're not actually
            # loading the auth plugin at this point, so the error message
            # from it doesn't actually make sense to os-client-config users
            options, _args = parser.parse_known_args(argv)
            plugin_names = loading.get_available_plugin_names()
            raise exceptions.OpenStackConfigException(
                "An invalid auth-type was specified: {auth_type}."
                " Valid choices are: {plugin_names}.".format(
                    auth_type=options.os_auth_type,
                    plugin_names=",".join(plugin_names)))

        if service_keys:
            primary_service = service_keys[0]
        else:
            primary_service = None
        loading.register_session_argparse_arguments(parser)
        adapter.register_adapter_argparse_arguments(
            parser, service_type=primary_service)
        for service_key in service_keys:
            # legacy clients have un-prefixed api-version options
            parser.add_argument(
                '--{service_key}-api-version'.format(
                    service_key=service_key.replace('_', '-'),
                    help=argparse_mod.SUPPRESS))
            adapter.register_service_adapter_argparse_arguments(
                parser, service_type=service_key)

        # Backwards compat options for legacy clients
        parser.add_argument('--http-timeout', help=argparse_mod.SUPPRESS)
        parser.add_argument('--os-endpoint-type', help=argparse_mod.SUPPRESS)
        parser.add_argument('--endpoint-type', help=argparse_mod.SUPPRESS)

    def _fix_backwards_interface(self, cloud):
        new_cloud = {}
        for key in cloud.keys():
            if key.endswith('endpoint_type'):
                target_key = key.replace('endpoint_type', 'interface')
            else:
                target_key = key
            new_cloud[target_key] = cloud[key]
        return new_cloud

    def _fix_backwards_api_timeout(self, cloud):
        new_cloud = {}
        # requests can only have one timeout, which means that in a single
        # cloud there is no point in different timeout values. However,
        # for some reason many of the legacy clients decided to shove their
        # service name in to the arg name for reasons surpassin sanity. If
        # we find any values that are not api_timeout, overwrite api_timeout
        # with the value
        service_timeout = None
        for key in cloud.keys():
            if key.endswith('timeout') and not (
                    key == 'timeout' or key == 'api_timeout'):
                service_timeout = cloud[key]
            else:
                new_cloud[key] = cloud[key]
        if service_timeout is not None:
            new_cloud['api_timeout'] = service_timeout
        # The common argparse arg from keystoneauth is called timeout, but
        # os-client-config expects it to be called api_timeout
        if self._argv_timeout:
            if 'timeout' in new_cloud and new_cloud['timeout']:
                new_cloud['api_timeout'] = new_cloud.pop('timeout')
        return new_cloud

    def get_all_clouds(self):

        clouds = []

        for cloud in self.get_cloud_names():
            for region in self._get_regions(cloud):
                if region:
                    clouds.append(self.get_one_cloud(
                        cloud, region_name=region['name']))
        return clouds

    def _fix_args(self, args=None, argparse=None):
        """Massage the passed-in options

        Replace - with _ and strip os_ prefixes.

        Convert an argparse Namespace object to a dict, removing values
        that are either None or ''.
        """
        if not args:
            args = {}

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
            if type(args[key]) == dict:
                # dive into the auth dict
                new_args[key] = self._fix_args(args[key])
                continue

            key = key.replace('-', '_')
            if key.startswith('os_'):
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
            deprecated = getattr(opt, 'deprecated', getattr(
                opt, 'deprecated_opts', []))
            for d_opt in deprecated:
                d_opt_name = d_opt.name.replace('-', '_')
                if d_opt_name in config:
                    return config[d_opt_name]

    def auth_config_hook(self, config):
        """Allow examination of config values before loading auth plugin

        OpenStackClient will override this to perform additional checks
        on auth_type.
        """
        return config

    def _get_auth_loader(self, config):
        # Re-use the admin_token plugin for the "None" plugin
        # since it does not look up endpoints or tokens but rather
        # does a passthrough. This is useful for things like Ironic
        # that have a keystoneless operational mode, but means we're
        # still dealing with a keystoneauth Session object, so all the
        # _other_ things (SSL arg handling, timeout) all work consistently
        if config['auth_type'] in (None, "None", ''):
            config['auth_type'] = 'admin_token'
            # Set to notused rather than None because validate_auth will
            # strip the value if it's actually python None
            config['auth']['token'] = 'notused'
        return loading.get_plugin_loader(config['auth_type'])

    def _validate_auth_ksc(self, config, cloud):
        try:
            import keystoneclient.auth as ksc_auth
        except ImportError:
            return config

        # May throw a keystoneclient.exceptions.NoMatchingPlugin
        plugin_options = ksc_auth.get_plugin_class(
            config['auth_type']).get_options()

        for p_opt in plugin_options:
            # if it's in config.auth, win, kill it from config dict
            # if it's in config and not in config.auth, move it
            # deprecated loses to current
            # provided beats default, deprecated or not
            winning_value = self._find_winning_auth_value(
                p_opt,
                config['auth'],
            )
            if not winning_value:
                winning_value = self._find_winning_auth_value(
                    p_opt,
                    config,
                )

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

    def _validate_auth(self, config, loader):
        # May throw a keystoneauth1.exceptions.NoMatchingPlugin

        plugin_options = loader.get_options()

        for p_opt in plugin_options:
            # if it's in config.auth, win, kill it from config dict
            # if it's in config and not in config.auth, move it
            # deprecated loses to current
            # provided beats default, deprecated or not
            winning_value = self._find_winning_auth_value(
                p_opt,
                config['auth'],
            )
            if not winning_value:
                winning_value = self._find_winning_auth_value(
                    p_opt,
                    config,
                )

            config = self._clean_up_after_ourselves(
                config,
                p_opt,
                winning_value,
            )

            # See if this needs a prompting
            config = self.option_prompt(config, p_opt)

        return config

    def _validate_auth_correctly(self, config, loader):
        # May throw a keystoneauth1.exceptions.NoMatchingPlugin

        plugin_options = loader.get_options()

        for p_opt in plugin_options:
            # if it's in config, win, move it and kill it from config dict
            # if it's in config.auth but not in config it's good
            # deprecated loses to current
            # provided beats default, deprecated or not
            winning_value = self._find_winning_auth_value(
                p_opt,
                config,
            )
            if not winning_value:
                winning_value = self._find_winning_auth_value(
                    p_opt,
                    config['auth'],
                )

            config = self._clean_up_after_ourselves(
                config,
                p_opt,
                winning_value,
            )

            # See if this needs a prompting
            config = self.option_prompt(config, p_opt)

        return config

    def option_prompt(self, config, p_opt):
        """Prompt user for option that requires a value"""
        if (
                p_opt.prompt is not None and
                p_opt.dest not in config['auth'] and
                self._pw_callback is not None
        ):
            config['auth'][p_opt.dest] = self._pw_callback(p_opt.prompt)
        return config

    def _clean_up_after_ourselves(self, config, p_opt, winning_value):

        # Clean up after ourselves
        for opt in [p_opt.name] + [o.name for o in p_opt.deprecated]:
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

    def magic_fixes(self, config):
        """Perform the set of magic argument fixups"""

        # Infer token plugin if a token was given
        if (('auth' in config and 'token' in config['auth']) or
                ('auth_token' in config and config['auth_token']) or
                ('token' in config and config['token'])):
            config.setdefault('token', config.pop('auth_token', None))

        # These backwards compat values are only set via argparse. If it's
        # there, it's because it was passed in explicitly, and should win
        config = self._fix_backwards_api_timeout(config)
        if 'endpoint_type' in config:
            config['interface'] = config.pop('endpoint_type')

        config = self._fix_backwards_auth_plugin(config)
        config = self._fix_backwards_project(config)
        config = self._fix_backwards_interface(config)
        config = self._fix_backwards_networks(config)
        config = self._handle_domain_id(config)

        for key in BOOL_KEYS:
            if key in config:
                if type(config[key]) is not bool:
                    config[key] = get_boolean(config[key])

        # TODO(mordred): Special casing auth_url here. We should
        #                come back to this betterer later so that it's
        #                more generalized
        if 'auth' in config and 'auth_url' in config['auth']:
            config['auth']['auth_url'] = config['auth']['auth_url'].format(
                **config)

        return config

    def get_one_cloud(self, cloud=None, validate=True,
                      argparse=None, **kwargs):
        """Retrieve a single cloud configuration and merge additional options

        :param string cloud:
            The name of the configuration to load from clouds.yaml
        :param boolean validate:
            Validate the config. Setting this to False causes no auth plugin
            to be created. It's really only useful for testing.
        :param Namespace argparse:
            An argparse Namespace object; allows direct passing in of
            argparse options to be added to the cloud config.  Values
            of None and '' will be removed.
        :param region_name: Name of the region of the cloud.
        :param kwargs: Additional configuration options

        :raises: keystoneauth1.exceptions.MissingRequiredOptions
            on missing required auth parameters
        """

        args = self._fix_args(kwargs, argparse=argparse)

        if cloud is None:
            if 'cloud' in args:
                cloud = args['cloud']
            else:
                cloud = self.default_cloud

        config = self._get_base_cloud_config(cloud)

        # Get region specific settings
        if 'region_name' not in args:
            args['region_name'] = ''
        region = self._get_region(cloud=cloud, region_name=args['region_name'])
        args['region_name'] = region['name']
        region_args = copy.deepcopy(region['values'])

        # Regions is a list that we can use to create a list of cloud/region
        # objects. It does not belong in the single-cloud dict
        config.pop('regions', None)

        # Can't just do update, because None values take over
        for arg_list in region_args, args:
            for (key, val) in iter(arg_list.items()):
                if val is not None:
                    if key == 'auth' and config[key] is not None:
                        config[key] = _auth_update(config[key], val)
                    else:
                        config[key] = val

        config = self.magic_fixes(config)

        # NOTE(dtroyer): OSC needs a hook into the auth args before the
        #                plugin is loaded in order to maintain backward-
        #                compatible behaviour
        config = self.auth_config_hook(config)

        if validate:
            try:
                loader = self._get_auth_loader(config)
                config = self._validate_auth(config, loader)
                auth_plugin = loader.load_from_options(**config['auth'])
            except Exception as e:
                # We WANT the ksa exception normally
                # but OSC can't handle it right now, so we try deferring
                # to ksc. If that ALSO fails, it means there is likely
                # a deeper issue, so we assume the ksa error was correct
                self.log.debug("Deferring keystone exception: {e}".format(e=e))
                auth_plugin = None
                try:
                    config = self._validate_auth_ksc(config, cloud)
                except Exception:
                    raise e
        else:
            auth_plugin = None

        # If any of the defaults reference other values, we need to expand
        for (key, value) in config.items():
            if hasattr(value, 'format'):
                config[key] = value.format(**config)

        force_ipv4 = config.pop('force_ipv4', self.force_ipv4)
        prefer_ipv6 = config.pop('prefer_ipv6', True)
        if not prefer_ipv6:
            force_ipv4 = True

        if cloud is None:
            cloud_name = ''
        else:
            cloud_name = str(cloud)
        return cloud_config.CloudConfig(
            name=cloud_name,
            region=config['region_name'],
            config=self._normalize_keys(config),
            force_ipv4=force_ipv4,
            auth_plugin=auth_plugin,
            openstack_config=self,
            session_constructor=self._session_constructor,
        )

    def get_one_cloud_osc(
        self,
        cloud=None,
        validate=True,
        argparse=None,
        **kwargs
    ):
        """Retrieve a single cloud configuration and merge additional options

        :param string cloud:
            The name of the configuration to load from clouds.yaml
        :param boolean validate:
            Validate the config. Setting this to False causes no auth plugin
            to be created. It's really only useful for testing.
        :param Namespace argparse:
            An argparse Namespace object; allows direct passing in of
            argparse options to be added to the cloud config.  Values
            of None and '' will be removed.
        :param region_name: Name of the region of the cloud.
        :param kwargs: Additional configuration options

        :raises: keystoneauth1.exceptions.MissingRequiredOptions
            on missing required auth parameters
        """

        args = self._fix_args(kwargs, argparse=argparse)

        if cloud is None:
            if 'cloud' in args:
                cloud = args['cloud']
            else:
                cloud = self.default_cloud

        config = self._get_base_cloud_config(cloud)

        # Get region specific settings
        if 'region_name' not in args:
            args['region_name'] = ''
        region = self._get_region(cloud=cloud, region_name=args['region_name'])
        args['region_name'] = region['name']
        region_args = copy.deepcopy(region['values'])

        # Regions is a list that we can use to create a list of cloud/region
        # objects. It does not belong in the single-cloud dict
        config.pop('regions', None)

        # Can't just do update, because None values take over
        for arg_list in region_args, args:
            for (key, val) in iter(arg_list.items()):
                if val is not None:
                    if key == 'auth' and config[key] is not None:
                        config[key] = _auth_update(config[key], val)
                    else:
                        config[key] = val

        config = self.magic_fixes(config)

        # NOTE(dtroyer): OSC needs a hook into the auth args before the
        #                plugin is loaded in order to maintain backward-
        #                compatible behaviour
        config = self.auth_config_hook(config)

        if validate:
            loader = self._get_auth_loader(config)
            config = self._validate_auth_correctly(config, loader)
            auth_plugin = loader.load_from_options(**config['auth'])
        else:
            auth_plugin = None

        # If any of the defaults reference other values, we need to expand
        for (key, value) in config.items():
            if hasattr(value, 'format'):
                config[key] = value.format(**config)

        force_ipv4 = config.pop('force_ipv4', self.force_ipv4)
        prefer_ipv6 = config.pop('prefer_ipv6', True)
        if not prefer_ipv6:
            force_ipv4 = True

        if cloud is None:
            cloud_name = ''
        else:
            cloud_name = str(cloud)
        return cloud_config.CloudConfig(
            name=cloud_name,
            region=config['region_name'],
            config=self._normalize_keys(config),
            force_ipv4=force_ipv4,
            auth_plugin=auth_plugin,
            openstack_config=self,
        )

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
        print_cloud = False
        if len(sys.argv) == 1:
            print_cloud = True
        elif len(sys.argv) == 3 and (
                sys.argv[1] == cloud.name and sys.argv[2] == cloud.region):
            print_cloud = True
        elif len(sys.argv) == 2 and (
                sys.argv[1] == cloud.name):
            print_cloud = True

        if print_cloud:
            print(cloud.name, cloud.region, cloud.config)
