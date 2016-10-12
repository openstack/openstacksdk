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

import importlib
import warnings

from keystoneauth1 import adapter
import keystoneauth1.exceptions.catalog
from keystoneauth1 import plugin
from keystoneauth1 import session
import requestsexceptions

from os_client_config import _log
from os_client_config import constructors
from os_client_config import exceptions


def _get_client(service_key):
    class_mapping = constructors.get_constructor_mapping()
    if service_key not in class_mapping:
        raise exceptions.OpenStackConfigException(
            "Service {service_key} is unkown. Please pass in a client"
            " constructor or submit a patch to os-client-config".format(
                service_key=service_key))
    mod_name, ctr_name = class_mapping[service_key].rsplit('.', 1)
    lib_name = mod_name.split('.')[0]
    try:
        mod = importlib.import_module(mod_name)
    except ImportError:
        raise exceptions.OpenStackConfigException(
            "Client for '{service_key}' was requested, but"
            " {mod_name} was unable to be imported. Either import"
            " the module yourself and pass the constructor in as an argument,"
            " or perhaps you do not have python-{lib_name} installed.".format(
                service_key=service_key,
                mod_name=mod_name,
                lib_name=lib_name))
    try:
        ctr = getattr(mod, ctr_name)
    except AttributeError:
        raise exceptions.OpenStackConfigException(
            "Client for '{service_key}' was requested, but although"
            " {mod_name} imported fine, the constructor at {fullname}"
            " as not found. Please check your installation, we have no"
            " clue what is wrong with your computer.".format(
                service_key=service_key,
                mod_name=mod_name,
                fullname=class_mapping[service_key]))
    return ctr


def _make_key(key, service_type):
    if not service_type:
        return key
    else:
        service_type = service_type.lower().replace('-', '_')
        return "_".join([service_type, key])


class CloudConfig(object):
    def __init__(self, name, region, config,
                 force_ipv4=False, auth_plugin=None,
                 openstack_config=None, session_constructor=None):
        self.name = name
        self.region = region
        self.config = config
        self.log = _log.setup_logging(__name__)
        self._force_ipv4 = force_ipv4
        self._auth = auth_plugin
        self._openstack_config = openstack_config
        self._keystone_session = None
        self._session_constructor = session_constructor or session.Session

    def __getattr__(self, key):
        """Return arbitrary attributes."""

        if key.startswith('os_'):
            key = key[3:]

        if key in [attr.replace('-', '_') for attr in self.config]:
            return self.config[key]
        else:
            return None

    def __iter__(self):
        return self.config.__iter__()

    def __eq__(self, other):
        return (self.name == other.name and self.region == other.region
                and self.config == other.config)

    def __ne__(self, other):
        return not self == other

    def set_session_constructor(self, session_constructor):
        """Sets the Session constructor."""
        self._session_constructor = session_constructor

    def get_requests_verify_args(self):
        """Return the verify and cert values for the requests library."""
        if self.config['verify'] and self.config['cacert']:
            verify = self.config['cacert']
        else:
            verify = self.config['verify']
            if self.config['cacert']:
                warnings.warn(
                    "You are specifying a cacert for the cloud {0} but "
                    "also to ignore the host verification. The host SSL cert "
                    "will not be verified.".format(self.name))

        cert = self.config.get('cert', None)
        if cert:
            if self.config['key']:
                cert = (cert, self.config['key'])
        return (verify, cert)

    def get_services(self):
        """Return a list of service types we know something about."""
        services = []
        for key, val in self.config.items():
            if (key.endswith('api_version')
                    or key.endswith('service_type')
                    or key.endswith('service_name')):
                services.append("_".join(key.split('_')[:-2]))
        return list(set(services))

    def get_auth_args(self):
        return self.config['auth']

    def get_interface(self, service_type=None):
        key = _make_key('interface', service_type)
        interface = self.config.get('interface')
        return self.config.get(key, interface)

    def get_region_name(self, service_type=None):
        if not service_type:
            return self.region
        key = _make_key('region_name', service_type)
        return self.config.get(key, self.region)

    def get_api_version(self, service_type):
        key = _make_key('api_version', service_type)
        return self.config.get(key, None)

    def get_service_type(self, service_type):
        key = _make_key('service_type', service_type)
        # Cinder did an evil thing where they defined a second service
        # type in the catalog. Of course, that's insane, so let's hide this
        # atrocity from the as-yet-unsullied eyes of our users.
        # Of course, if the user requests a volumev2, that structure should
        # still work.
        if (service_type == 'volume' and
                self.get_api_version(service_type).startswith('2')):
            service_type = 'volumev2'
        return self.config.get(key, service_type)

    def get_service_name(self, service_type):
        key = _make_key('service_name', service_type)
        return self.config.get(key, None)

    def get_endpoint(self, service_type):
        key = _make_key('endpoint_override', service_type)
        old_key = _make_key('endpoint', service_type)
        return self.config.get(key, self.config.get(old_key, None))

    @property
    def prefer_ipv6(self):
        return not self._force_ipv4

    @property
    def force_ipv4(self):
        return self._force_ipv4

    def get_auth(self):
        """Return a keystoneauth plugin from the auth credentials."""
        return self._auth

    def get_session(self):
        """Return a keystoneauth session based on the auth credentials."""
        if self._keystone_session is None:
            if not self._auth:
                raise exceptions.OpenStackConfigException(
                    "Problem with auth parameters")
            (verify, cert) = self.get_requests_verify_args()
            # Turn off urllib3 warnings about insecure certs if we have
            # explicitly configured requests to tell it we do not want
            # cert verification
            if not verify:
                self.log.debug(
                    "Turning off SSL warnings for {cloud}:{region}"
                    " since verify=False".format(
                        cloud=self.name, region=self.region))
            requestsexceptions.squelch_warnings(insecure_requests=not verify)
            self._keystone_session = self._session_constructor(
                auth=self._auth,
                verify=verify,
                cert=cert,
                timeout=self.config['api_timeout'])
        return self._keystone_session

    def get_session_client(self, service_key):
        """Return a prepped requests adapter for a given service.

        This is useful for making direct requests calls against a
        'mounted' endpoint. That is, if you do:

          client = get_session_client('compute')

        then you can do:

          client.get('/flavors')

        and it will work like you think.
        """

        return adapter.Adapter(
            session=self.get_session(),
            service_type=self.get_service_type(service_key),
            service_name=self.get_service_name(service_key),
            interface=self.get_interface(service_key),
            region_name=self.region)

    def get_session_endpoint(self, service_key):
        """Return the endpoint from config or the catalog.

        If a configuration lists an explicit endpoint for a service,
        return that. Otherwise, fetch the service catalog from the
        keystone session and return the appropriate endpoint.

        :param service_key: Generic key for service, such as 'compute' or
                            'network'

        :returns: Endpoint for the service, or None if not found
        """

        override_endpoint = self.get_endpoint(service_key)
        if override_endpoint:
            return override_endpoint
        # keystone is a special case in keystone, because what?
        session = self.get_session()
        if service_key == 'identity':
            endpoint = session.get_endpoint(interface=plugin.AUTH_INTERFACE)
        else:
            args = {
                'service_type': self.get_service_type(service_key),
                'service_name': self.get_service_name(service_key),
                'interface': self.get_interface(service_key),
                'region_name': self.region
            }
            try:
                endpoint = session.get_endpoint(**args)
            except keystoneauth1.exceptions.catalog.EndpointNotFound:
                self.log.warning("Keystone catalog entry not found (%s)",
                                 args)
                endpoint = None
        return endpoint

    def get_legacy_client(
            self, service_key, client_class=None, interface_key=None,
            pass_version_arg=True, version=None, **kwargs):
        """Return a legacy OpenStack client object for the given config.

        Most of the OpenStack python-*client libraries have the same
        interface for their client constructors, but there are several
        parameters one wants to pass given a :class:`CloudConfig` object.

        In the future, OpenStack API consumption should be done through
        the OpenStack SDK, but that's not ready yet. This is for getting
        Client objects from python-*client only.

        :param service_key: Generic key for service, such as 'compute' or
                            'network'
        :param client_class: Class of the client to be instantiated. This
                             should be the unversioned version if there
                             is one, such as novaclient.client.Client, or
                             the versioned one, such as
                             neutronclient.v2_0.client.Client if there isn't
        :param interface_key: (optional) Some clients, such as glanceclient
                              only accept the parameter 'interface' instead
                              of 'endpoint_type' - this is a get-out-of-jail
                              parameter for those until they can be aligned.
                              os-client-config understands this to be the
                              case if service_key is image, so this is really
                              only for use with other unknown broken clients.
        :param pass_version_arg: (optional) If a versioned Client constructor
                                 was passed to client_class, set this to
                                 False, which will tell get_client to not
                                 pass a version parameter. os-client-config
                                 already understand that this is the
                                 case for network, so it can be omitted in
                                 that case.
        :param version: (optional) Version string to override the configured
                                   version string.
        :param kwargs: (optional) keyword args are passed through to the
                       Client constructor, so this is in case anything
                       additional needs to be passed in.
        """
        if not client_class:
            client_class = _get_client(service_key)

        # Because of course swift is different
        if service_key == 'object-store':
            return self._get_swift_client(client_class=client_class, **kwargs)
        interface = self.get_interface(service_key)
        # trigger exception on lack of service
        endpoint = self.get_session_endpoint(service_key)
        endpoint_override = self.get_endpoint(service_key)

        if not interface_key:
            if service_key in ('image', 'key-manager'):
                interface_key = 'interface'
            else:
                interface_key = 'endpoint_type'

        constructor_kwargs = dict(
            session=self.get_session(),
            service_name=self.get_service_name(service_key),
            service_type=self.get_service_type(service_key),
            endpoint_override=endpoint_override,
            region_name=self.region)

        if service_key == 'image':
            # os-client-config does not depend on glanceclient, but if
            # the user passed in glanceclient.client.Client, which they
            # would need to do if they were requesting 'image' - then
            # they necessarily have glanceclient installed
            from glanceclient.common import utils as glance_utils
            endpoint, detected_version = glance_utils.strip_version(endpoint)
            # If the user has passed in a version, that's explicit, use it
            if not version:
                version = detected_version
            # If the user has passed in or configured an override, use it.
            # Otherwise, ALWAYS pass in an endpoint_override becuase
            # we've already done version stripping, so we don't want version
            # reconstruction to happen twice
            if not endpoint_override:
                constructor_kwargs['endpoint_override'] = endpoint
        constructor_kwargs.update(kwargs)
        constructor_kwargs[interface_key] = interface
        if pass_version_arg:
            if not version:
                version = self.get_api_version(service_key)
            # Temporary workaround while we wait for python-openstackclient
            # to be able to handle 2.0 which is what neutronclient expects
            if service_key == 'network' and version == '2':
                version = '2.0'
            if service_key == 'identity':
                # Workaround for bug#1513839
                if 'endpoint' not in constructor_kwargs:
                    endpoint = self.get_session_endpoint('identity')
                    constructor_kwargs['endpoint'] = endpoint
            if service_key == 'network':
                constructor_kwargs['api_version'] = version
            else:
                constructor_kwargs['version'] = version
        if service_key == 'database':
            # TODO(mordred) Remove when https://review.openstack.org/314032
            # has landed and released. We're passing in a Session, but the
            # trove Client object has username and password as required
            # args
            constructor_kwargs['username'] = None
            constructor_kwargs['password'] = None

        return client_class(**constructor_kwargs)

    def _get_swift_client(self, client_class, **kwargs):
        auth_args = self.get_auth_args()
        auth_version = self.get_api_version('identity')
        session = self.get_session()
        token = session.get_token()
        endpoint = self.get_session_endpoint(service_key='object-store')
        if not endpoint:
            return None
        # If we have a username/password, we want to pass them to
        # swift - because otherwise it will not re-up tokens appropriately
        # However, if we only have non-password auth, then get a token
        # and pass it in
        swift_kwargs = dict(
            auth_version=auth_version,
            preauthurl=endpoint,
            preauthtoken=token,
            os_options=dict(
                region_name=self.get_region_name(),
                auth_token=token,
                object_storage_url=endpoint,
                service_type=self.get_service_type('object-store'),
                endpoint_type=self.get_interface('object-store'),

            ))
        if self.config['api_timeout'] is not None:
            swift_kwargs['timeout'] = float(self.config['api_timeout'])

        # create with password
        swift_kwargs['user'] = auth_args.get('username')
        swift_kwargs['key'] = auth_args.get('password')
        swift_kwargs['authurl'] = auth_args.get('auth_url')
        os_options = {}
        if auth_version == '2.0':
            os_options['tenant_name'] = auth_args.get('project_name')
            os_options['tenant_id'] = auth_args.get('project_id')
        else:
            os_options['project_name'] = auth_args.get('project_name')
            os_options['project_id'] = auth_args.get('project_id')

        for key in (
                'user_id',
                'project_domain_id',
                'project_domain_name',
                'user_domain_id',
                'user_domain_name'):
            os_options[key] = auth_args.get(key)
        swift_kwargs['os_options'].update(os_options)

        return client_class(**swift_kwargs)

    def get_cache_expiration_time(self):
        if self._openstack_config:
            return self._openstack_config.get_cache_expiration_time()

    def get_cache_path(self):
        if self._openstack_config:
            return self._openstack_config.get_cache_path()

    def get_cache_class(self):
        if self._openstack_config:
            return self._openstack_config.get_cache_class()

    def get_cache_arguments(self):
        if self._openstack_config:
            return self._openstack_config.get_cache_arguments()

    def get_cache_expiration(self):
        if self._openstack_config:
            return self._openstack_config.get_cache_expiration()

    def get_cache_resource_expiration(self, resource, default=None):
        """Get expiration time for a resource

        :param resource: Name of the resource type
        :param default: Default value to return if not found (optional,
                        defaults to None)

        :returns: Expiration time for the resource type as float or default
        """
        if self._openstack_config:
            expiration = self._openstack_config.get_cache_expiration()
            if resource not in expiration:
                return default
            return float(expiration[resource])

    def get_external_networks(self):
        """Get list of network names for external networks."""
        return [
            net['name'] for net in self.config['networks']
            if net['routes_externally']]

    def get_external_ipv4_networks(self):
        """Get list of network names for external IPv4 networks."""
        return [
            net['name'] for net in self.config['networks']
            if net['routes_ipv4_externally']]

    def get_external_ipv6_networks(self):
        """Get list of network names for external IPv6 networks."""
        return [
            net['name'] for net in self.config['networks']
            if net['routes_ipv6_externally']]

    def get_internal_networks(self):
        """Get list of network names for internal networks."""
        return [
            net['name'] for net in self.config['networks']
            if not net['routes_externally']]

    def get_internal_ipv4_networks(self):
        """Get list of network names for internal IPv4 networks."""
        return [
            net['name'] for net in self.config['networks']
            if not net['routes_ipv4_externally']]

    def get_internal_ipv6_networks(self):
        """Get list of network names for internal IPv6 networks."""
        return [
            net['name'] for net in self.config['networks']
            if not net['routes_ipv6_externally']]

    def get_default_network(self):
        """Get network used for default interactions."""
        for net in self.config['networks']:
            if net['default_interface']:
                return net['name']
        return None

    def get_nat_destination(self):
        """Get network used for NAT destination."""
        for net in self.config['networks']:
            if net['nat_destination']:
                return net['name']
        return None
