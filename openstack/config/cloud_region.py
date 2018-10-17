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

import copy
import warnings

from keystoneauth1 import adapter
from keystoneauth1 import discover
import keystoneauth1.exceptions.catalog
from keystoneauth1 import session as ks_session
import os_service_types
import requestsexceptions
from six.moves import urllib

from openstack import version as openstack_version
from openstack import _log
from openstack.config import _util
from openstack.config import defaults as config_defaults
from openstack import exceptions


def _make_key(key, service_type):
    if not service_type:
        return key
    else:
        service_type = service_type.lower().replace('-', '_')
        return "_".join([service_type, key])


def _get_implied_microversion(version):
    if not version:
        return
    if '.' in version:
        # Some services historically had a .0 in their normal api version.
        # Neutron springs to mind with version "2.0". If a user has "2.0"
        # set in a variable or config file just because history, we don't
        # need to send any microversion headers.
        if version.split('.')[1] != "0":
            return version


def from_session(session, name=None, region_name=None,
                 force_ipv4=False,
                 app_name=None, app_version=None, **kwargs):
    """Construct a CloudRegion from an existing `keystoneauth1.session.Session`

    When a Session already exists, we don't actually even need to go through
    the OpenStackConfig.get_one_cloud dance. We have a Session with Auth info.
    The only parameters that are really needed are adapter/catalog related.

    :param keystoneauth1.session.session session:
        An existing authenticated Session to use.
    :param str name:
        A name to use for this cloud region in logging. If left empty, the
        hostname of the auth_url found in the Session will be used.
    :param str region_name:
        The region name to connect to.
    :param bool force_ipv4:
        Whether or not to disable IPv6 support. Defaults to False.
    :param str app_name:
        Name of the application to be added to User Agent.
    :param str app_version:
        Version of the application to be added to User Agent.
    :param kwargs:
        Config settings for this cloud region.
    """
    config_dict = config_defaults.get_defaults()
    config_dict.update(**kwargs)
    return CloudRegion(
        name=name, session=session, config=config_dict,
        region_name=region_name, force_ipv4=force_ipv4,
        app_name=app_name, app_version=app_version)


class CloudRegion(object):
    """The configuration for a Region of an OpenStack Cloud.

    A CloudRegion encapsulates the config information needed for connections
    to all of the services in a Region of a Cloud.
    """
    def __init__(self, name=None, region_name=None, config=None,
                 force_ipv4=False, auth_plugin=None,
                 openstack_config=None, session_constructor=None,
                 app_name=None, app_version=None, session=None,
                 discovery_cache=None, extra_config=None,
                 cache_expiration_time=0, cache_expirations=None,
                 cache_path=None, cache_class='dogpile.cache.null',
                 cache_arguments=None, password_callback=None):
        self._name = name
        self.region_name = region_name
        self.config = _util.normalize_keys(config)
        self._extra_config = extra_config or {}
        self.log = _log.setup_logging('openstack.config')
        self._force_ipv4 = force_ipv4
        self._auth = auth_plugin
        self._openstack_config = openstack_config
        self._keystone_session = session
        self._session_constructor = session_constructor or ks_session.Session
        self._app_name = app_name
        self._app_version = app_version
        self._discovery_cache = discovery_cache or None
        self._cache_expiration_time = cache_expiration_time
        self._cache_expirations = cache_expirations or {}
        self._cache_path = cache_path
        self._cache_class = cache_class
        self._cache_arguments = cache_arguments
        self._password_callback = password_callback

        self._service_type_manager = os_service_types.ServiceTypes()

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
        return (
            self.name == other.name
            and self.region_name == other.region_name
            and self.config == other.config)

    def __ne__(self, other):
        return not self == other

    @property
    def name(self):
        if self._name is None:
            try:
                self._name = urllib.parse.urlparse(
                    self.get_session().auth.auth_url).hostname
            except Exception:
                self._name = self._app_name or ''
        return self._name

    @property
    def full_name(self):
        """Return a string that can be used as an identifier.

        Always returns a valid string. It will have name and region_name
        or just one of the two if only one is set, or else 'unknown'.
        """
        if self.name and self.region_name:
            return ":".join([self.name, self.region_name])
        elif self.name and not self.region_name:
            return self.name
        elif not self.name and self.region_name:
            return self.region_name
        else:
            return 'unknown'

    def set_session_constructor(self, session_constructor):
        """Sets the Session constructor."""
        self._session_constructor = session_constructor

    def get_requests_verify_args(self):
        """Return the verify and cert values for the requests library."""
        insecure = self.config.get('insecure', False)
        verify = self.config.get('verify', True)
        cacert = self.config.get('cacert')
        # Insecure is the most aggressive setting, so it wins
        if insecure:
            verify = False
        if verify and cacert:
            verify = cacert
        else:
            if cacert:
                warnings.warn(
                    "You are specifying a cacert for the cloud {full_name}"
                    " but also to ignore the host verification. The host SSL"
                    " cert will not be verified.".format(
                        full_name=self.full_name))

        cert = self.config.get('cert')
        if cert:
            if self.config.get('key'):
                cert = (cert, self.config.get('key'))
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
        return self.config.get('auth', {})

    def _get_config(
            self, key, service_type,
            default=None,
            fallback_to_unprefixed=False,
            converter=None):
        '''Get a config value for a service_type.

        Finds the config value for a key, looking first for it prefixed by
        the given service_type, then by any known aliases of that service_type.
        Finally, if fallback_to_unprefixed is True, a value will be looked
        for without a prefix to support the config values where a global
        default makes sense.

        For instance, ``_get_config('example', 'block-storage', True)`` would
        first look for ``block_storage_example``, then ``volumev3_example``,
        ``volumev2_example`` and ``volume_example``. If no value was found, it
        would look for ``example``.

        If none of that works, it returns the value in ``default``.
        '''
        if service_type is None:
            return self.config.get(key)

        for st in self._service_type_manager.get_all_types(service_type):
            value = self.config.get(_make_key(key, st))
            if value is not None:
                break
        else:
            if fallback_to_unprefixed:
                value = self.config.get(key)

        if value is None:
            return default
        else:
            if converter is not None:
                value = converter(value)
            return value

    def get_interface(self, service_type=None):
        return self._get_config(
            'interface', service_type, fallback_to_unprefixed=True)

    def get_api_version(self, service_type):
        version = self._get_config('api_version', service_type)
        if version:
            try:
                float(version)
            except ValueError:
                if 'latest' in version:
                    warnings.warn(
                        "You have a configured API_VERSION with 'latest' in"
                        " it. In the context of openstacksdk this doesn't make"
                        " any sense.")
                return None
        return version

    def get_default_microversion(self, service_type):
        return self._get_config('default_microversion', service_type)

    def get_service_type(self, service_type):
        # People requesting 'volume' are doing so because os-client-config
        # let them. What they want is block-storage, not explicitly the
        # v1 of cinder. If someone actually wants v1, they'll have api_version
        # set to 1, in which case block-storage will still work properly.
        # Use service-types-manager to grab the official type name. _get_config
        # will still look for config by alias, but starting with the official
        # type will get us things in the right order.
        if self._service_type_manager.is_known(service_type):
            service_type = self._service_type_manager.get_service_type(
                service_type)
        return self._get_config(
            'service_type', service_type, default=service_type)

    def get_service_name(self, service_type):
        return self._get_config('service_name', service_type)

    def get_endpoint(self, service_type):
        value = self._get_config('endpoint_override', service_type)
        if not value:
            value = self._get_config('endpoint', service_type)
        if not value and self.config.get('auth_type') == 'none':
            # If endpoint is given and we're using the none auth type,
            # then the endpoint value is the endpoint_override for every
            # service.
            value = self.config.get('auth', {}).get('endpoint')
        return value

    def get_connect_retries(self, service_type):
        return self._get_config('connect_retries', service_type,
                                fallback_to_unprefixed=True,
                                converter=int)

    def get_status_code_retries(self, service_type):
        return self._get_config('status_code_retries', service_type,
                                fallback_to_unprefixed=True,
                                converter=int)

    @property
    def prefer_ipv6(self):
        return not self._force_ipv4

    @property
    def force_ipv4(self):
        return self._force_ipv4

    def get_auth(self):
        """Return a keystoneauth plugin from the auth credentials."""
        return self._auth

    def insert_user_agent(self):
        """Set sdk information into the user agent of the Session.

        .. warning::
            This method is here to be used by os-client-config. It exists
            as a hook point so that os-client-config can provice backwards
            compatibility and still be in the User Agent for people using
            os-client-config directly.

        Normal consumers of SDK should use app_name and app_version. However,
        if someone else writes a subclass of
        :class:`~openstack.config.cloud_region.CloudRegion` it may be
        desirable.
        """
        self._keystone_session.additional_user_agent.append(
            ('openstacksdk', openstack_version.__version__))

    def get_session(self):
        """Return a keystoneauth session based on the auth credentials."""
        if self._keystone_session is None:
            if not self._auth:
                raise exceptions.ConfigException(
                    "Problem with auth parameters")
            (verify, cert) = self.get_requests_verify_args()
            # Turn off urllib3 warnings about insecure certs if we have
            # explicitly configured requests to tell it we do not want
            # cert verification
            if not verify:
                self.log.debug(
                    "Turning off SSL warnings for {full_name}"
                    " since verify=False".format(full_name=self.full_name))
            requestsexceptions.squelch_warnings(insecure_requests=not verify)
            self._keystone_session = self._session_constructor(
                auth=self._auth,
                verify=verify,
                cert=cert,
                timeout=self.config.get('api_timeout'),
                discovery_cache=self._discovery_cache)
            self.insert_user_agent()
            # Using old keystoneauth with new os-client-config fails if
            # we pass in app_name and app_version. Those are not essential,
            # nor a reason to bump our minimum, so just test for the session
            # having the attribute post creation and set them then.
            if hasattr(self._keystone_session, 'app_name'):
                self._keystone_session.app_name = self._app_name
            if hasattr(self._keystone_session, 'app_version'):
                self._keystone_session.app_version = self._app_version
        return self._keystone_session

    def get_service_catalog(self):
        """Helper method to grab the service catalog."""
        return self._auth.get_access(self.get_session()).service_catalog

    def _get_version_request(self, service_type, version):
        """Translate OCC version args to those needed by ksa adapter.

        If no version is requested explicitly and we have a configured version,
        set the version parameter and let ksa deal with expanding that to
        min=ver.0, max=ver.latest.

        If version is set, pass it through.

        If version is not set and we don't have a configured version, default
        to latest.

        If version is set, contains a '.', and default_microversion is not
        set, also pass it as a default microversion.
        """
        version_request = _util.VersionRequest()
        if version == 'latest':
            version_request.max_api_version = 'latest'
            return version_request

        if not version:
            version = self.get_api_version(service_type)

        # Octavia doens't have a version discovery document. Hard-code an
        # exception to this logic for now.
        if not version and service_type not in ('load-balancer',):
            version_request.max_api_version = 'latest'
        else:
            version_request.version = version

        default_microversion = self.get_default_microversion(service_type)
        implied_microversion = _get_implied_microversion(version)
        if (implied_microversion and default_microversion
                and implied_microversion != default_microversion):
            raise exceptions.ConfigException(
                "default_microversion of {default_microversion} was given"
                " for {service_type}, but api_version looks like a"
                " microversion as well. Please set api_version to just the"
                " desired major version, or omit default_microversion".format(
                    default_microversion=default_microversion,
                    service_type=service_type))
        if implied_microversion:
            default_microversion = implied_microversion
            # If we're inferring a microversion, don't pass the whole
            # string in as api_version, since that tells keystoneauth
            # we're looking for a major api version.
            version_request.version = version[0]

        version_request.default_microversion = default_microversion

        return version_request

    def get_all_version_data(self, service_type):
        # Seriously. Don't think about the existential crisis
        # that is the next line. You'll wind up in cthulhu's lair.
        service_type = self.get_service_type(service_type)
        versions = self.get_session().get_all_version_data(
            service_type=service_type,
            interface=self.get_interface(service_type),
            region_name=self.region_name,
        )
        region_versions = versions.get(self.region_name, {})
        interface_versions = region_versions.get(
            self.get_interface(service_type), {})
        return interface_versions.get(service_type, [])

    def get_session_client(
            self, service_type, version=None, constructor=adapter.Adapter,
            **kwargs):
        """Return a prepped keystoneauth Adapter for a given service.

        This is useful for making direct requests calls against a
        'mounted' endpoint. That is, if you do:

          client = get_session_client('compute')

        then you can do:

          client.get('/flavors')

        and it will work like you think.
        """
        version_request = self._get_version_request(service_type, version)

        kwargs.setdefault('connect_retries',
                          self.get_connect_retries(service_type))
        kwargs.setdefault('status_code_retries',
                          self.get_status_code_retries(service_type))
        endpoint_override = self.get_endpoint(service_type)
        version = version_request.version
        min_api_version = (
            kwargs.pop('min_version', None) or version_request.min_api_version)
        max_api_version = (
            kwargs.pop('max_version', None) or version_request.max_api_version)
        # Older neutron has inaccessible discovery document. Nobody noticed
        # because neutronclient hard-codes an append of v2.0. YAY!
        if service_type == 'network':
            version = None
            min_api_version = None
            max_api_version = None
            if endpoint_override is None:
                network_adapter = constructor(
                    session=self.get_session(),
                    service_type=self.get_service_type(service_type),
                    service_name=self.get_service_name(service_type),
                    interface=self.get_interface(service_type),
                    region_name=self.region_name,
                )
                network_endpoint = network_adapter.get_endpoint()
                if not network_endpoint.rstrip().rsplit('/')[1] == 'v2.0':
                    if not network_endpoint.endswith('/'):
                        network_endpoint += '/'
                    network_endpoint = urllib.parse.urljoin(
                        network_endpoint, 'v2.0')
                endpoint_override = network_endpoint

        client = constructor(
            session=self.get_session(),
            service_type=self.get_service_type(service_type),
            service_name=self.get_service_name(service_type),
            interface=self.get_interface(service_type),
            region_name=self.region_name,
            version=version,
            min_version=min_api_version,
            max_version=max_api_version,
            endpoint_override=endpoint_override,
            default_microversion=version_request.default_microversion,
            **kwargs)
        if version_request.default_microversion:
            default_microversion = version_request.default_microversion
            info = client.get_endpoint_data()
            if not discover.version_between(
                    info.min_microversion,
                    info.max_microversion,
                    default_microversion
            ):
                if self.get_default_microversion(service_type):
                    raise exceptions.ConfigException(
                        "A default microversion for service {service_type} of"
                        " {default_microversion} was requested, but the cloud"
                        " only supports a minimum of {min_microversion} and"
                        " a maximum of {max_microversion}.".format(
                            service_type=service_type,
                            default_microversion=default_microversion,
                            min_microversion=discover.version_to_string(
                                info.min_microversion),
                            max_microversion=discover.version_to_string(
                                info.max_microversion)))
                else:
                    raise exceptions.ConfigException(
                        "A default microversion for service {service_type} of"
                        " {default_microversion} was requested, but the cloud"
                        " only supports a maximum of"
                        " only supports a minimum of {min_microversion} and"
                        " a maximum of {max_microversion}. The default"
                        " microversion was set because a microversion"
                        " formatted version string, '{api_version}', was"
                        " passed for the api_version of the service. If it"
                        " was not intended to set a default microversion"
                        " please remove anything other than an integer major"
                        " version from the version setting for"
                        " the service.".format(
                            service_type=service_type,
                            api_version=self.get_api_version(service_type),
                            default_microversion=default_microversion,
                            min_microversion=discover.version_to_string(
                                info.min_microversion),
                            max_microversion=discover.version_to_string(
                                info.max_microversion)))
        return client

    def get_session_endpoint(
            self, service_type, min_version=None, max_version=None):
        """Return the endpoint from config or the catalog.

        If a configuration lists an explicit endpoint for a service,
        return that. Otherwise, fetch the service catalog from the
        keystone session and return the appropriate endpoint.

        :param service_type: Official service type of service
        """

        override_endpoint = self.get_endpoint(service_type)
        if override_endpoint:
            return override_endpoint

        service_name = self.get_service_name(service_type)
        interface = self.get_interface(service_type)
        session = self.get_session()
        # Do this as kwargs because of os-client-config unittest mocking
        version_kwargs = {}
        if min_version:
            version_kwargs['min_version'] = min_version
        if max_version:
            version_kwargs['max_version'] = max_version
        try:
            # Return the highest version we find that matches
            # the request
            endpoint = session.get_endpoint(
                service_type=service_type,
                region_name=self.region_name,
                interface=interface,
                service_name=service_name,
                **version_kwargs
            )
        except keystoneauth1.exceptions.catalog.EndpointNotFound:
            endpoint = None
        if not endpoint:
            self.log.warning(
                "Keystone catalog entry not found ("
                "service_type=%s,service_name=%s"
                "interface=%s,region_name=%s)",
                service_type,
                service_name,
                interface,
                self.region_name,
            )
        return endpoint

    def get_cache_expiration_time(self):
        # TODO(mordred) We should be validating/transforming this on input
        return int(self._cache_expiration_time)

    def get_cache_path(self):
        return self._cache_path

    def get_cache_class(self):
        return self._cache_class

    def get_cache_arguments(self):
        return copy.deepcopy(self._cache_arguments)

    def get_cache_expirations(self):
        return copy.deepcopy(self._cache_expirations)

    def get_cache_resource_expiration(self, resource, default=None):
        """Get expiration time for a resource

        :param resource: Name of the resource type
        :param default: Default value to return if not found (optional,
                        defaults to None)

        :returns: Expiration time for the resource type as float or default
        """
        if resource not in self._cache_expirations:
            return default
        return float(self._cache_expirations[resource])

    def requires_floating_ip(self):
        """Return whether or not this cloud requires floating ips.


        :returns: True of False if know, None if discovery is needed.
                  If requires_floating_ip is not configured but the cloud is
                  known to not provide floating ips, will return False.
        """
        if self.config['floating_ip_source'] == "None":
            return False
        return self.config.get('requires_floating_ip')

    def get_external_networks(self):
        """Get list of network names for external networks."""
        return [
            net['name'] for net in self.config.get('networks', [])
            if net['routes_externally']]

    def get_external_ipv4_networks(self):
        """Get list of network names for external IPv4 networks."""
        return [
            net['name'] for net in self.config.get('networks', [])
            if net['routes_ipv4_externally']]

    def get_external_ipv6_networks(self):
        """Get list of network names for external IPv6 networks."""
        return [
            net['name'] for net in self.config.get('networks', [])
            if net['routes_ipv6_externally']]

    def get_internal_networks(self):
        """Get list of network names for internal networks."""
        return [
            net['name'] for net in self.config.get('networks', [])
            if not net['routes_externally']]

    def get_internal_ipv4_networks(self):
        """Get list of network names for internal IPv4 networks."""
        return [
            net['name'] for net in self.config.get('networks', [])
            if not net['routes_ipv4_externally']]

    def get_internal_ipv6_networks(self):
        """Get list of network names for internal IPv6 networks."""
        return [
            net['name'] for net in self.config.get('networks', [])
            if not net['routes_ipv6_externally']]

    def get_default_network(self):
        """Get network used for default interactions."""
        for net in self.config.get('networks', []):
            if net['default_interface']:
                return net['name']
        return None

    def get_nat_destination(self):
        """Get network used for NAT destination."""
        for net in self.config.get('networks', []):
            if net['nat_destination']:
                return net['name']
        return None

    def get_nat_source(self):
        """Get network used for NAT source."""
        for net in self.config.get('networks', []):
            if net.get('nat_source'):
                return net['name']
        return None

    def _get_extra_config(self, key, defaults=None):
        """Fetch an arbitrary extra chunk of config, laying in defaults.

        :param string key: name of the config section to fetch
        :param dict defaults: (optional) default values to merge under the
                                         found config
        """
        defaults = _util.normalize_keys(defaults or {})
        if not key:
            return defaults
        return _util.merge_clouds(
            defaults,
            _util.normalize_keys(self._extra_config.get(key, {})))

    def get_client_config(self, name=None, defaults=None):
        """Get config settings for a named client.

        Settings will also be looked for in a section called 'client'.
        If settings are found in both, they will be merged with the settings
        from the named section winning over the settings from client section,
        and both winning over provided defaults.

        :param string name:
            Name of the config section to look for.
        :param dict defaults:
            Default settings to use.

        :returns:
            A dict containing merged settings from the named section, the
            client section and the defaults.
        """
        return self._get_extra_config(
            name, self._get_extra_config('client', defaults))

    def get_password_callback(self):
        return self._password_callback
