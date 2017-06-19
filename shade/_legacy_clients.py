# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import importlib
import warnings

from os_client_config import constructors

from shade import _utils


class LegacyClientFactoryMixin(object):
    """Mixin Class containing factory functions for legacy client objects.

    Methods in this class exist for backwards compatibility so will not go
    away any time - but they are all things whose use is discouraged. They're
    in a mixin to unclutter the main class file.
    """

    def _create_legacy_client(
            self, client, service, deprecated=True,
            module_name=None, **kwargs):
        if client not in self._legacy_clients:
            if deprecated:
                self._deprecated_import_check(client)
            if module_name:
                constructors.get_constructor_mapping()[service] = module_name
            self._legacy_clients[client] = self._get_client(service, **kwargs)
        return self._legacy_clients[client]

    def _deprecated_import_check(self, client):
        module_name = '{client}client'.format(client=client)
        warnings.warn(
            'Using shade to get a {module_name} object is deprecated. If you'
            ' need a {module_name} object, please use make_legacy_client in'
            ' os-client-config instead'.format(module_name=module_name))
        try:
            importlib.import_module(module_name)
        except ImportError:
            self.log.error(
                '{module_name} is no longer a dependency of shade. You need to'
                ' install python-{module_name} directly.'.format(
                    module_name=module_name))
            raise

    @property
    def trove_client(self):
        return self._create_legacy_client('trove', 'database')

    @property
    def magnum_client(self):
        return self._create_legacy_client('magnum', 'container-infra')

    @property
    def neutron_client(self):
        return self._create_legacy_client('neutron', 'network')

    @property
    def nova_client(self):
        return self._create_legacy_client('nova', 'compute', version='2.0')

    @property
    def glance_client(self):
        return self._create_legacy_client('glance', 'image')

    @property
    def heat_client(self):
        return self._create_legacy_client('heat', 'orchestration')

    @property
    def swift_client(self):
        return self._create_legacy_client('swift', 'object-store')

    @property
    def cinder_client(self):
        return self._create_legacy_client('cinder', 'volume')

    @property
    def designate_client(self):
        return self._create_legacy_client('designate', 'dns')

    @property
    def keystone_client(self):
        # Trigger discovery from ksa
        self._identity_client

        # Skip broken discovery in ksc. We're good thanks.
        from keystoneclient.v2_0 import client as v2_client
        from keystoneclient.v3 import client as v3_client
        if self.cloud_config.config['identity_api_version'] == '3':
            client_class = v3_client
        else:
            client_class = v2_client

        return self._create_legacy_client(
            'keystone', 'identity',
            client_class=client_class.Client,
            deprecated=False,
            endpoint=self.cloud_config.config[
                'identity_endpoint_override'],
            endpoint_override=self.cloud_config.config[
                'identity_endpoint_override'])

    # Set the ironic API microversion to a known-good
    # supported/tested with the contents of shade.
    #
    # NOTE(TheJulia): Defaulted to version 1.6 as the ironic
    # state machine changes which will increment the version
    # and break an automatic transition of an enrolled node
    # to an available state. Locking the version is intended
    # to utilize the original transition until shade supports
    # calling for node inspection to allow the transition to
    # take place automatically.
    # NOTE(mordred): shade will handle microversions more
    # directly in the REST layer. This microversion property
    # will never change. When we implement REST, we should
    # start at 1.6 since that's what we've been requesting
    # via ironic_client
    @property
    def ironic_api_microversion(self):
        # NOTE(mordred) Abuse _legacy_clients to only show
        # this warning once
        if 'ironic-microversion' not in self._legacy_clients:
            warnings.warn(
                'shade is transitioning to direct REST calls which'
                ' will handle microversions with no action needed'
                ' on the part of the user. The ironic_api_microversion'
                ' property is only used by the legacy ironic_client'
                ' constructor and will never change. If you are using'
                ' it for any reason, either switch to just using'
                ' shade ironic-related API calls, or use os-client-config'
                ' make_legacy_client directly and pass os_ironic_api_version'
                ' to it as an argument. It is highly recommended to'
                ' stop using this property.')
            self._legacy_clients['ironic-microversion'] = True
        return self._get_legacy_ironic_microversion()

    def _get_legacy_ironic_microversion(self):
        return '1.6'

    @property
    def ironic_client(self):
        return self._create_legacy_client(
            'ironic', 'baremetal', deprecated=False,
            module_name='ironicclient.client.Client',
            os_ironic_api_version=self._get_legacy_ironic_microversion())

    def _get_swift_kwargs(self):
        auth_version = self.cloud_config.get_api_version('identity')
        auth_args = self.cloud_config.config.get('auth', {})
        os_options = {'auth_version': auth_version}
        if auth_version == '2.0':
            os_options['os_tenant_name'] = auth_args.get('project_name')
            os_options['os_tenant_id'] = auth_args.get('project_id')
        else:
            os_options['os_project_name'] = auth_args.get('project_name')
            os_options['os_project_id'] = auth_args.get('project_id')

        for key in (
                'username',
                'password',
                'auth_url',
                'user_id',
                'project_domain_id',
                'project_domain_name',
                'user_domain_id',
                'user_domain_name'):
            os_options['os_{key}'.format(key=key)] = auth_args.get(key)
        return os_options

    @property
    def swift_service(self):
        suppress_warning = 'swift-service' not in self._legacy_clients
        return self.make_swift_service_object(suppress_warning)

    def make_swift_service(self, suppress_warning=False):
        # NOTE(mordred): Not using helper functions because the
        #                error message needs to be different
        if not suppress_warning:
            warnings.warn(
                'Using shade to get a SwiftService object is deprecated. shade'
                ' will automatically do the things SwiftServices does as part'
                ' of the normal object resource calls. If you are having'
                ' trouble using those such that you still need to use'
                ' SwiftService, please file a bug with shade.'
                ' If you understand the issues and want to make this warning'
                ' go away, use cloud.make_swift_service(True) instead of'
                ' cloud.swift_service')
            # Abuse self._legacy_clients so that we only give the warning
            # once. We don't cache SwiftService objects.
            self._legacy_clients['swift-service'] = True
        try:
            import swiftclient.service
        except ImportError:
            self.log.error(
                'swiftclient is no longer a dependency of shade. You need to'
                ' install python-swiftclient directly.')
        with _utils.shade_exceptions("Error constructing SwiftService"):
            endpoint = self.get_session_endpoint(
                service_key='object-store')
            options = dict(os_auth_token=self.auth_token,
                           os_storage_url=endpoint,
                           os_region_name=self.region_name)
            options.update(self._get_swift_kwargs())
            return swiftclient.service.SwiftService(options=options)
