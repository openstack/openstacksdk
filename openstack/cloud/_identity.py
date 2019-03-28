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

# import types so that we can reference ListType in sphinx param declarations.
# We can't just use list, because sphinx gets confused by
# openstack.resource.Resource.list and openstack.resource2.Resource.list
import types  # noqa

import munch

from openstack.cloud import exc
from openstack.cloud import _normalize
from openstack.cloud import _utils
from openstack import utils


class IdentityCloudMixin(_normalize.Normalizer):

    @property
    def _identity_client(self):
        if 'identity' not in self._raw_clients:
            self._raw_clients['identity'] = self._get_versioned_client(
                'identity', min_version=2, max_version='3.latest')
        return self._raw_clients['identity']

    @_utils.cache_on_arguments()
    def list_projects(self, domain_id=None, name_or_id=None, filters=None):
        """List projects.

        With no parameters, returns a full listing of all visible projects.

        :param domain_id: domain ID to scope the searched projects.
        :param name_or_id: project name or ID.
        :param filters: a dict containing additional filters to use
            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: a list of ``munch.Munch`` containing the projects

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        kwargs = dict(
            filters=filters,
            domain_id=domain_id)
        if self._is_client_version('identity', 3):
            kwargs['obj_name'] = 'project'

        pushdown, filters = _normalize._split_filters(**kwargs)

        try:
            if self._is_client_version('identity', 3):
                key = 'projects'
            else:
                key = 'tenants'
            data = self._identity_client.get(
                '/{endpoint}'.format(endpoint=key), params=pushdown)
            projects = self._normalize_projects(
                self._get_and_munchify(key, data))
        except Exception as e:
            self.log.debug("Failed to list projects", exc_info=True)
            raise exc.OpenStackCloudException(str(e))
        return _utils._filter_list(projects, name_or_id, filters)

    def search_projects(self, name_or_id=None, filters=None, domain_id=None):
        '''Backwards compatibility method for search_projects

        search_projects originally had a parameter list that was name_or_id,
        filters and list had domain_id first. This method exists in this form
        to allow code written with positional parameter to still work. But
        really, use keyword arguments.
        '''
        return self.list_projects(
            domain_id=domain_id, name_or_id=name_or_id, filters=filters)

    def get_project(self, name_or_id, filters=None, domain_id=None):
        """Get exactly one project.

        :param name_or_id: project name or ID.
        :param filters: a dict containing additional filters to use.
        :param domain_id: domain ID (identity v3 only).

        :returns: a list of ``munch.Munch`` containing the project description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        return _utils._get_entity(self, 'project', name_or_id, filters,
                                  domain_id=domain_id)

    @_utils.valid_kwargs('description')
    def update_project(self, name_or_id, enabled=None, domain_id=None,
                       **kwargs):
        with _utils.shade_exceptions(
                "Error in updating project {project}".format(
                    project=name_or_id)):
            proj = self.get_project(name_or_id, domain_id=domain_id)
            if not proj:
                raise exc.OpenStackCloudException(
                    "Project %s not found." % name_or_id)
            if enabled is not None:
                kwargs.update({'enabled': enabled})
            # NOTE(samueldmq): Current code only allow updates of description
            # or enabled fields.
            if self._is_client_version('identity', 3):
                data = self._identity_client.patch(
                    '/projects/' + proj['id'], json={'project': kwargs})
                project = self._get_and_munchify('project', data)
            else:
                data = self._identity_client.post(
                    '/tenants/' + proj['id'], json={'tenant': kwargs})
                project = self._get_and_munchify('tenant', data)
            project = self._normalize_project(project)
        self.list_projects.invalidate(self)
        return project

    def create_project(
            self, name, description=None, domain_id=None, enabled=True):
        """Create a project."""
        with _utils.shade_exceptions(
                "Error in creating project {project}".format(project=name)):
            project_ref = self._get_domain_id_param_dict(domain_id)
            project_ref.update({'name': name,
                                'description': description,
                                'enabled': enabled})
            endpoint, key = ('tenants', 'tenant')
            if self._is_client_version('identity', 3):
                endpoint, key = ('projects', 'project')
            data = self._identity_client.post(
                '/{endpoint}'.format(endpoint=endpoint),
                json={key: project_ref})
            project = self._normalize_project(
                self._get_and_munchify(key, data))
        self.list_projects.invalidate(self)
        return project

    def delete_project(self, name_or_id, domain_id=None):
        """Delete a project.

        :param string name_or_id: Project name or ID.
        :param string domain_id: Domain ID containing the project(identity v3
            only).

        :returns: True if delete succeeded, False if the project was not found.

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the OpenStack API call
        """

        with _utils.shade_exceptions(
                "Error in deleting project {project}".format(
                    project=name_or_id)):
            project = self.get_project(name_or_id, domain_id=domain_id)
            if project is None:
                self.log.debug(
                    "Project %s not found for deleting", name_or_id)
                return False

            if self._is_client_version('identity', 3):
                self._identity_client.delete('/projects/' + project['id'])
            else:
                self._identity_client.delete('/tenants/' + project['id'])

        return True

    @_utils.valid_kwargs('domain_id')
    @_utils.cache_on_arguments()
    def list_users(self, **kwargs):
        """List users.

        :param domain_id: Domain ID. (v3)

        :returns: a list of ``munch.Munch`` containing the user description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        data = self._identity_client.get('/users', params=kwargs)
        return _utils.normalize_users(
            self._get_and_munchify('users', data))

    @_utils.valid_kwargs('domain_id')
    def search_users(self, name_or_id=None, filters=None, **kwargs):
        """Search users.

        :param string name_or_id: user name or ID.
        :param domain_id: Domain ID. (v3)
        :param filters: a dict containing additional filters to use.
            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: a list of ``munch.Munch`` containing the users

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        users = self.list_users(**kwargs)
        return _utils._filter_list(users, name_or_id, filters)

    @_utils.valid_kwargs('domain_id')
    def get_user(self, name_or_id, filters=None, **kwargs):
        """Get exactly one user.

        :param string name_or_id: user name or ID.
        :param domain_id: Domain ID. (v3)
        :param filters: a dict containing additional filters to use.
            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: a single ``munch.Munch`` containing the user description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        return _utils._get_entity(self, 'user', name_or_id, filters, **kwargs)

    def get_user_by_id(self, user_id, normalize=True):
        """Get a user by ID.

        :param string user_id: user ID
        :param bool normalize: Flag to control dict normalization

        :returns: a single ``munch.Munch`` containing the user description
        """
        data = self._identity_client.get(
            '/users/{user}'.format(user=user_id),
            error_message="Error getting user with ID {user_id}".format(
                user_id=user_id))

        user = self._get_and_munchify('user', data)
        if user and normalize:
            user = _utils.normalize_users(user)
        return user

    # NOTE(Shrews): Keystone v2 supports updating only name, email and enabled.
    @_utils.valid_kwargs('name', 'email', 'enabled', 'domain_id', 'password',
                         'description', 'default_project')
    def update_user(self, name_or_id, **kwargs):
        self.list_users.invalidate(self)
        user_kwargs = {}
        if 'domain_id' in kwargs and kwargs['domain_id']:
            user_kwargs['domain_id'] = kwargs['domain_id']
        user = self.get_user(name_or_id, **user_kwargs)

        # TODO(mordred) When this changes to REST, force interface=admin
        # in the adapter call if it's an admin force call (and figure out how
        # to make that disctinction)
        if self._is_client_version('identity', 2):
            # Do not pass v3 args to a v2 keystone.
            kwargs.pop('domain_id', None)
            kwargs.pop('description', None)
            kwargs.pop('default_project', None)
            password = kwargs.pop('password', None)
            if password is not None:
                with _utils.shade_exceptions(
                        "Error updating password for {user}".format(
                            user=name_or_id)):
                    error_msg = "Error updating password for user {}".format(
                        name_or_id)
                    data = self._identity_client.put(
                        '/users/{u}/OS-KSADM/password'.format(u=user['id']),
                        json={'user': {'password': password}},
                        error_message=error_msg)

            # Identity v2.0 implements PUT. v3 PATCH. Both work as PATCH.
            data = self._identity_client.put(
                '/users/{user}'.format(user=user['id']), json={'user': kwargs},
                error_message="Error in updating user {}".format(name_or_id))
        else:
            # NOTE(samueldmq): now this is a REST call and domain_id is dropped
            # if None. keystoneclient drops keys with None values.
            if 'domain_id' in kwargs and kwargs['domain_id'] is None:
                del kwargs['domain_id']
            data = self._identity_client.patch(
                '/users/{user}'.format(user=user['id']), json={'user': kwargs},
                error_message="Error in updating user {}".format(name_or_id))

        user = self._get_and_munchify('user', data)
        self.list_users.invalidate(self)
        return _utils.normalize_users([user])[0]

    def create_user(
            self, name, password=None, email=None, default_project=None,
            enabled=True, domain_id=None, description=None):
        """Create a user."""
        params = self._get_identity_params(domain_id, default_project)
        params.update({'name': name, 'password': password, 'email': email,
                       'enabled': enabled})
        if self._is_client_version('identity', 3):
            params['description'] = description
        elif description is not None:
            self.log.info(
                "description parameter is not supported on Keystone v2")

        error_msg = "Error in creating user {user}".format(user=name)
        data = self._identity_client.post('/users', json={'user': params},
                                          error_message=error_msg)
        user = self._get_and_munchify('user', data)

        self.list_users.invalidate(self)
        return _utils.normalize_users([user])[0]

    @_utils.valid_kwargs('domain_id')
    def delete_user(self, name_or_id, **kwargs):
        # TODO(mordred) Why are we invalidating at the TOP?
        self.list_users.invalidate(self)
        user = self.get_user(name_or_id, **kwargs)
        if not user:
            self.log.debug(
                "User {0} not found for deleting".format(name_or_id))
            return False

        # TODO(mordred) Extra GET only needed to support keystoneclient.
        #               Can be removed as a follow-on.
        user = self.get_user_by_id(user['id'], normalize=False)
        self._identity_client.delete(
            '/users/{user}'.format(user=user['id']),
            error_message="Error in deleting user {user}".format(
                user=name_or_id))

        self.list_users.invalidate(self)
        return True

    def _get_user_and_group(self, user_name_or_id, group_name_or_id):
        user = self.get_user(user_name_or_id)
        if not user:
            raise exc.OpenStackCloudException(
                'User {user} not found'.format(user=user_name_or_id))

        group = self.get_group(group_name_or_id)
        if not group:
            raise exc.OpenStackCloudException(
                'Group {user} not found'.format(user=group_name_or_id))

        return (user, group)

    def add_user_to_group(self, name_or_id, group_name_or_id):
        """Add a user to a group.

        :param string name_or_id: User name or ID
        :param string group_name_or_id: Group name or ID

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the OpenStack API call
        """
        user, group = self._get_user_and_group(name_or_id, group_name_or_id)

        error_msg = "Error adding user {user} to group {group}".format(
            user=name_or_id, group=group_name_or_id)
        self._identity_client.put(
            '/groups/{g}/users/{u}'.format(g=group['id'], u=user['id']),
            error_message=error_msg)

    def is_user_in_group(self, name_or_id, group_name_or_id):
        """Check to see if a user is in a group.

        :param string name_or_id: User name or ID
        :param string group_name_or_id: Group name or ID

        :returns: True if user is in the group, False otherwise

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the OpenStack API call
        """
        user, group = self._get_user_and_group(name_or_id, group_name_or_id)

        try:
            self._identity_client.head(
                '/groups/{g}/users/{u}'.format(g=group['id'], u=user['id']))
            return True
        except exc.OpenStackCloudURINotFound:
            # NOTE(samueldmq): knowing this URI exists, let's interpret this as
            # user not found in group rather than URI not found.
            return False

    def remove_user_from_group(self, name_or_id, group_name_or_id):
        """Remove a user from a group.

        :param string name_or_id: User name or ID
        :param string group_name_or_id: Group name or ID

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the OpenStack API call
        """
        user, group = self._get_user_and_group(name_or_id, group_name_or_id)

        error_msg = "Error removing user {user} from group {group}".format(
            user=name_or_id, group=group_name_or_id)
        self._identity_client.delete(
            '/groups/{g}/users/{u}'.format(g=group['id'], u=user['id']),
            error_message=error_msg)

    @_utils.valid_kwargs('type', 'service_type', 'description')
    def create_service(self, name, enabled=True, **kwargs):
        """Create a service.

        :param name: Service name.
        :param type: Service type. (type or service_type required.)
        :param service_type: Service type. (type or service_type required.)
        :param description: Service description (optional).
        :param enabled: Whether the service is enabled (v3 only)

        :returns: a ``munch.Munch`` containing the services description,
            i.e. the following attributes::
            - id: <service id>
            - name: <service name>
            - type: <service type>
            - service_type: <service type>
            - description: <service description>

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            OpenStack API call.

        """
        type_ = kwargs.pop('type', None)
        service_type = kwargs.pop('service_type', None)

        # TODO(mordred) When this changes to REST, force interface=admin
        # in the adapter call
        if self._is_client_version('identity', 2):
            url, key = '/OS-KSADM/services', 'OS-KSADM:service'
            kwargs['type'] = type_ or service_type
        else:
            url, key = '/services', 'service'
            kwargs['type'] = type_ or service_type
            kwargs['enabled'] = enabled
        kwargs['name'] = name

        msg = 'Failed to create service {name}'.format(name=name)
        data = self._identity_client.post(
            url, json={key: kwargs}, error_message=msg)
        service = self._get_and_munchify(key, data)
        return _utils.normalize_keystone_services([service])[0]

    @_utils.valid_kwargs('name', 'enabled', 'type', 'service_type',
                         'description')
    def update_service(self, name_or_id, **kwargs):
        # NOTE(SamYaple): Service updates are only available on v3 api
        if self._is_client_version('identity', 2):
            raise exc.OpenStackCloudUnavailableFeature(
                'Unavailable Feature: Service update requires Identity v3'
            )

        # NOTE(SamYaple): Keystone v3 only accepts 'type' but shade accepts
        #                 both 'type' and 'service_type' with a preference
        #                 towards 'type'
        type_ = kwargs.pop('type', None)
        service_type = kwargs.pop('service_type', None)
        if type_ or service_type:
            kwargs['type'] = type_ or service_type

        if self._is_client_version('identity', 2):
            url, key = '/OS-KSADM/services', 'OS-KSADM:service'
        else:
            url, key = '/services', 'service'

        service = self.get_service(name_or_id)
        msg = 'Error in updating service {service}'.format(service=name_or_id)
        data = self._identity_client.patch(
            '{url}/{id}'.format(url=url, id=service['id']), json={key: kwargs},
            error_message=msg)
        service = self._get_and_munchify(key, data)
        return _utils.normalize_keystone_services([service])[0]

    def list_services(self):
        """List all Keystone services.

        :returns: a list of ``munch.Munch`` containing the services description

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            OpenStack API call.
        """
        if self._is_client_version('identity', 2):
            url, key = '/OS-KSADM/services', 'OS-KSADM:services'
            endpoint_filter = {'interface': 'admin'}
        else:
            url, key = '/services', 'services'
            endpoint_filter = {}

        data = self._identity_client.get(
            url, endpoint_filter=endpoint_filter,
            error_message="Failed to list services")
        services = self._get_and_munchify(key, data)
        return _utils.normalize_keystone_services(services)

    def search_services(self, name_or_id=None, filters=None):
        """Search Keystone services.

        :param name_or_id: Name or id of the desired service.
        :param filters: a dict containing additional filters to use. e.g.
                        {'type': 'network'}.

        :returns: a list of ``munch.Munch`` containing the services description

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            OpenStack API call.
        """
        services = self.list_services()
        return _utils._filter_list(services, name_or_id, filters)

    def get_service(self, name_or_id, filters=None):
        """Get exactly one Keystone service.

        :param name_or_id: Name or id of the desired service.
        :param filters: a dict containing additional filters to use. e.g.
                {'type': 'network'}

        :returns: a ``munch.Munch`` containing the services description,
            i.e. the following attributes::
            - id: <service id>
            - name: <service name>
            - type: <service type>
            - description: <service description>

        :raises: ``OpenStackCloudException`` if something goes wrong during the
            OpenStack API call or if multiple matches are found.
        """
        return _utils._get_entity(self, 'service', name_or_id, filters)

    def delete_service(self, name_or_id):
        """Delete a Keystone service.

        :param name_or_id: Service name or id.

        :returns: True if delete succeeded, False otherwise.

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the OpenStack API call
        """
        service = self.get_service(name_or_id=name_or_id)
        if service is None:
            self.log.debug("Service %s not found for deleting", name_or_id)
            return False

        if self._is_client_version('identity', 2):
            url = '/OS-KSADM/services'
            endpoint_filter = {'interface': 'admin'}
        else:
            url = '/services'
            endpoint_filter = {}

        error_msg = 'Failed to delete service {id}'.format(id=service['id'])
        self._identity_client.delete(
            '{url}/{id}'.format(url=url, id=service['id']),
            endpoint_filter=endpoint_filter, error_message=error_msg)

        return True

    @_utils.valid_kwargs('public_url', 'internal_url', 'admin_url')
    def create_endpoint(self, service_name_or_id, url=None, interface=None,
                        region=None, enabled=True, **kwargs):
        """Create a Keystone endpoint.

        :param service_name_or_id: Service name or id for this endpoint.
        :param url: URL of the endpoint
        :param interface: Interface type of the endpoint
        :param public_url: Endpoint public URL.
        :param internal_url: Endpoint internal URL.
        :param admin_url: Endpoint admin URL.
        :param region: Endpoint region.
        :param enabled: Whether the endpoint is enabled

        NOTE: Both v2 (public_url, internal_url, admin_url) and v3
              (url, interface) calling semantics are supported. But
              you can only use one of them at a time.

        :returns: a list of ``munch.Munch`` containing the endpoint description

        :raises: OpenStackCloudException if the service cannot be found or if
            something goes wrong during the OpenStack API call.
        """
        public_url = kwargs.pop('public_url', None)
        internal_url = kwargs.pop('internal_url', None)
        admin_url = kwargs.pop('admin_url', None)

        if (url or interface) and (public_url or internal_url or admin_url):
            raise exc.OpenStackCloudException(
                "create_endpoint takes either url and interface OR"
                " public_url, internal_url, admin_url")

        service = self.get_service(name_or_id=service_name_or_id)
        if service is None:
            raise exc.OpenStackCloudException(
                "service {service} not found".format(
                    service=service_name_or_id))

        if self._is_client_version('identity', 2):
            if url:
                # v2.0 in use, v3-like arguments, one endpoint created
                if interface != 'public':
                    raise exc.OpenStackCloudException(
                        "Error adding endpoint for service {service}."
                        " On a v2 cloud the url/interface API may only be"
                        " used for public url. Try using the public_url,"
                        " internal_url, admin_url parameters instead of"
                        " url and interface".format(
                            service=service_name_or_id))
                endpoint_args = {'publicurl': url}
            else:
                # v2.0 in use, v2.0-like arguments, one endpoint created
                endpoint_args = {}
                if public_url:
                    endpoint_args.update({'publicurl': public_url})
                if internal_url:
                    endpoint_args.update({'internalurl': internal_url})
                if admin_url:
                    endpoint_args.update({'adminurl': admin_url})

            # keystone v2.0 requires 'region' arg even if it is None
            endpoint_args.update(
                {'service_id': service['id'], 'region': region})

            data = self._identity_client.post(
                '/endpoints', json={'endpoint': endpoint_args},
                endpoint_filter={'interface': 'admin'},
                error_message=("Failed to create endpoint for service"
                               " {service}".format(service=service['name'])))
            return [self._get_and_munchify('endpoint', data)]
        else:
            endpoints_args = []
            if url:
                # v3 in use, v3-like arguments, one endpoint created
                endpoints_args.append(
                    {'url': url, 'interface': interface,
                     'service_id': service['id'], 'enabled': enabled,
                     'region': region})
            else:
                # v3 in use, v2.0-like arguments, one endpoint created for each
                # interface url provided
                endpoint_args = {'region': region, 'enabled': enabled,
                                 'service_id': service['id']}
                if public_url:
                    endpoint_args.update({'url': public_url,
                                          'interface': 'public'})
                    endpoints_args.append(endpoint_args.copy())
                if internal_url:
                    endpoint_args.update({'url': internal_url,
                                          'interface': 'internal'})
                    endpoints_args.append(endpoint_args.copy())
                if admin_url:
                    endpoint_args.update({'url': admin_url,
                                          'interface': 'admin'})
                    endpoints_args.append(endpoint_args.copy())

            endpoints = []
            error_msg = ("Failed to create endpoint for service"
                         " {service}".format(service=service['name']))
            for args in endpoints_args:
                data = self._identity_client.post(
                    '/endpoints', json={'endpoint': args},
                    error_message=error_msg)
                endpoints.append(self._get_and_munchify('endpoint', data))
            return endpoints

    @_utils.valid_kwargs('enabled', 'service_name_or_id', 'url', 'interface',
                         'region')
    def update_endpoint(self, endpoint_id, **kwargs):
        # NOTE(SamYaple): Endpoint updates are only available on v3 api
        if self._is_client_version('identity', 2):
            raise exc.OpenStackCloudUnavailableFeature(
                'Unavailable Feature: Endpoint update'
            )

        service_name_or_id = kwargs.pop('service_name_or_id', None)
        if service_name_or_id is not None:
            kwargs['service_id'] = service_name_or_id

        data = self._identity_client.patch(
            '/endpoints/{}'.format(endpoint_id), json={'endpoint': kwargs},
            error_message="Failed to update endpoint {}".format(endpoint_id))
        return self._get_and_munchify('endpoint', data)

    def list_endpoints(self):
        """List Keystone endpoints.

        :returns: a list of ``munch.Munch`` containing the endpoint description

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        # Force admin interface if v2.0 is in use
        v2 = self._is_client_version('identity', 2)
        kwargs = {'endpoint_filter': {'interface': 'admin'}} if v2 else {}

        data = self._identity_client.get(
            '/endpoints', error_message="Failed to list endpoints", **kwargs)
        endpoints = self._get_and_munchify('endpoints', data)

        return endpoints

    def search_endpoints(self, id=None, filters=None):
        """List Keystone endpoints.

        :param id: endpoint id.
        :param filters: a dict containing additional filters to use. e.g.
                {'region': 'region-a.geo-1'}

        :returns: a list of ``munch.Munch`` containing the endpoint
            description. Each dict contains the following attributes::
            - id: <endpoint id>
            - region: <endpoint region>
            - public_url: <endpoint public url>
            - internal_url: <endpoint internal url> (optional)
            - admin_url: <endpoint admin url> (optional)

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        # NOTE(SamYaple): With keystone v3 we can filter directly via the
        # the keystone api, but since the return of all the endpoints even in
        # large environments is small, we can continue to filter in shade just
        # like the v2 api.
        endpoints = self.list_endpoints()
        return _utils._filter_list(endpoints, id, filters)

    def get_endpoint(self, id, filters=None):
        """Get exactly one Keystone endpoint.

        :param id: endpoint id.
        :param filters: a dict containing additional filters to use. e.g.
                {'region': 'region-a.geo-1'}

        :returns: a ``munch.Munch`` containing the endpoint description.
            i.e. a ``munch.Munch`` containing the following attributes::
            - id: <endpoint id>
            - region: <endpoint region>
            - public_url: <endpoint public url>
            - internal_url: <endpoint internal url> (optional)
            - admin_url: <endpoint admin url> (optional)
        """
        return _utils._get_entity(self, 'endpoint', id, filters)

    def delete_endpoint(self, id):
        """Delete a Keystone endpoint.

        :param id: Id of the endpoint to delete.

        :returns: True if delete succeeded, False otherwise.

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the OpenStack API call.
        """
        endpoint = self.get_endpoint(id=id)
        if endpoint is None:
            self.log.debug("Endpoint %s not found for deleting", id)
            return False

        # Force admin interface if v2.0 is in use
        v2 = self._is_client_version('identity', 2)
        kwargs = {'endpoint_filter': {'interface': 'admin'}} if v2 else {}

        error_msg = "Failed to delete endpoint {id}".format(id=id)
        self._identity_client.delete('/endpoints/{id}'.format(id=id),
                                     error_message=error_msg, **kwargs)

        return True

    def create_domain(self, name, description=None, enabled=True):
        """Create a domain.

        :param name: The name of the domain.
        :param description: A description of the domain.
        :param enabled: Is the domain enabled or not (default True).

        :returns: a ``munch.Munch`` containing the domain representation.

        :raise OpenStackCloudException: if the domain cannot be created.
        """
        domain_ref = {'name': name, 'enabled': enabled}
        if description is not None:
            domain_ref['description'] = description
        msg = 'Failed to create domain {name}'.format(name=name)
        data = self._identity_client.post(
            '/domains', json={'domain': domain_ref}, error_message=msg)
        domain = self._get_and_munchify('domain', data)
        return _utils.normalize_domains([domain])[0]

    def update_domain(
            self, domain_id=None, name=None, description=None,
            enabled=None, name_or_id=None):
        if domain_id is None:
            if name_or_id is None:
                raise exc.OpenStackCloudException(
                    "You must pass either domain_id or name_or_id value"
                )
            dom = self.get_domain(None, name_or_id)
            if dom is None:
                raise exc.OpenStackCloudException(
                    "Domain {0} not found for updating".format(name_or_id)
                )
            domain_id = dom['id']

        domain_ref = {}
        domain_ref.update({'name': name} if name else {})
        domain_ref.update({'description': description} if description else {})
        domain_ref.update({'enabled': enabled} if enabled is not None else {})

        error_msg = "Error in updating domain {id}".format(id=domain_id)
        data = self._identity_client.patch(
            '/domains/{id}'.format(id=domain_id),
            json={'domain': domain_ref}, error_message=error_msg)
        domain = self._get_and_munchify('domain', data)
        return _utils.normalize_domains([domain])[0]

    def delete_domain(self, domain_id=None, name_or_id=None):
        """Delete a domain.

        :param domain_id: ID of the domain to delete.
        :param name_or_id: Name or ID of the domain to delete.

        :returns: True if delete succeeded, False otherwise.

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the OpenStack API call.
        """
        if domain_id is None:
            if name_or_id is None:
                raise exc.OpenStackCloudException(
                    "You must pass either domain_id or name_or_id value"
                )
            dom = self.get_domain(name_or_id=name_or_id)
            if dom is None:
                self.log.debug(
                    "Domain %s not found for deleting", name_or_id)
                return False
            domain_id = dom['id']

        # A domain must be disabled before deleting
        self.update_domain(domain_id, enabled=False)
        error_msg = "Failed to delete domain {id}".format(id=domain_id)
        self._identity_client.delete('/domains/{id}'.format(id=domain_id),
                                     error_message=error_msg)

        return True

    def list_domains(self, **filters):
        """List Keystone domains.

        :returns: a list of ``munch.Munch`` containing the domain description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        data = self._identity_client.get(
            '/domains', params=filters, error_message="Failed to list domains")
        domains = self._get_and_munchify('domains', data)
        return _utils.normalize_domains(domains)

    def search_domains(self, filters=None, name_or_id=None):
        """Search Keystone domains.

        :param name_or_id: domain name or id
        :param dict filters: A dict containing additional filters to use.
             Keys to search on are id, name, enabled and description.

        :returns: a list of ``munch.Munch`` containing the domain description.
            Each ``munch.Munch`` contains the following attributes::
            - id: <domain id>
            - name: <domain name>
            - description: <domain description>

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        if filters is None:
            filters = {}
        if name_or_id is not None:
            domains = self.list_domains()
            return _utils._filter_list(domains, name_or_id, filters)
        else:
            return self.list_domains(**filters)

    def get_domain(self, domain_id=None, name_or_id=None, filters=None):
        """Get exactly one Keystone domain.

        :param domain_id: domain id.
        :param name_or_id: domain name or id.
        :param dict filters: A dict containing additional filters to use.
             Keys to search on are id, name, enabled and description.

        :returns: a ``munch.Munch`` containing the domain description, or None
            if not found. Each ``munch.Munch`` contains the following
            attributes::
            - id: <domain id>
            - name: <domain name>
            - description: <domain description>

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        if domain_id is None:
            # NOTE(SamYaple): search_domains() has filters and name_or_id
            # in the wrong positional order which prevents _get_entity from
            # being able to return quickly if passing a domain object so we
            # duplicate that logic here
            if hasattr(name_or_id, 'id'):
                return name_or_id
            return _utils._get_entity(self, 'domain', filters, name_or_id)
        else:
            error_msg = 'Failed to get domain {id}'.format(id=domain_id)
            data = self._identity_client.get(
                '/domains/{id}'.format(id=domain_id),
                error_message=error_msg)
            domain = self._get_and_munchify('domain', data)
            return _utils.normalize_domains([domain])[0]

    @_utils.valid_kwargs('domain_id')
    @_utils.cache_on_arguments()
    def list_groups(self, **kwargs):
        """List Keystone Groups.

        :param domain_id: domain id.

        :returns: A list of ``munch.Munch`` containing the group description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        data = self._identity_client.get(
            '/groups', params=kwargs, error_message="Failed to list groups")
        return _utils.normalize_groups(self._get_and_munchify('groups', data))

    @_utils.valid_kwargs('domain_id')
    def search_groups(self, name_or_id=None, filters=None, **kwargs):
        """Search Keystone groups.

        :param name: Group name or id.
        :param filters: A dict containing additional filters to use.
        :param domain_id: domain id.

        :returns: A list of ``munch.Munch`` containing the group description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        groups = self.list_groups(**kwargs)
        return _utils._filter_list(groups, name_or_id, filters)

    @_utils.valid_kwargs('domain_id')
    def get_group(self, name_or_id, filters=None, **kwargs):
        """Get exactly one Keystone group.

        :param id: Group name or id.
        :param filters: A dict containing additional filters to use.
        :param domain_id: domain id.

        :returns: A ``munch.Munch`` containing the group description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        return _utils._get_entity(self, 'group', name_or_id, filters, **kwargs)

    def create_group(self, name, description, domain=None):
        """Create a group.

        :param string name: Group name.
        :param string description: Group description.
        :param string domain: Domain name or ID for the group.

        :returns: A ``munch.Munch`` containing the group description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        group_ref = {'name': name}
        if description:
            group_ref['description'] = description
        if domain:
            dom = self.get_domain(domain)
            if not dom:
                raise exc.OpenStackCloudException(
                    "Creating group {group} failed: Invalid domain "
                    "{domain}".format(group=name, domain=domain)
                )
            group_ref['domain_id'] = dom['id']

        error_msg = "Error creating group {group}".format(group=name)
        data = self._identity_client.post(
            '/groups', json={'group': group_ref}, error_message=error_msg)
        group = self._get_and_munchify('group', data)
        self.list_groups.invalidate(self)
        return _utils.normalize_groups([group])[0]

    @_utils.valid_kwargs('domain_id')
    def update_group(self, name_or_id, name=None, description=None,
                     **kwargs):
        """Update an existing group

        :param string name: New group name.
        :param string description: New group description.
        :param domain_id: domain id.

        :returns: A ``munch.Munch`` containing the group description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        self.list_groups.invalidate(self)
        group = self.get_group(name_or_id, **kwargs)
        if group is None:
            raise exc.OpenStackCloudException(
                "Group {0} not found for updating".format(name_or_id)
            )

        group_ref = {}
        if name:
            group_ref['name'] = name
        if description:
            group_ref['description'] = description

        error_msg = "Unable to update group {name}".format(name=name_or_id)
        data = self._identity_client.patch(
            '/groups/{id}'.format(id=group['id']),
            json={'group': group_ref}, error_message=error_msg)
        group = self._get_and_munchify('group', data)
        self.list_groups.invalidate(self)
        return _utils.normalize_groups([group])[0]

    @_utils.valid_kwargs('domain_id')
    def delete_group(self, name_or_id, **kwargs):
        """Delete a group

        :param name_or_id: ID or name of the group to delete.
        :param domain_id: domain id.

        :returns: True if delete succeeded, False otherwise.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        group = self.get_group(name_or_id, **kwargs)
        if group is None:
            self.log.debug(
                "Group %s not found for deleting", name_or_id)
            return False

        error_msg = "Unable to delete group {name}".format(name=name_or_id)
        self._identity_client.delete('/groups/{id}'.format(id=group['id']),
                                     error_message=error_msg)

        self.list_groups.invalidate(self)
        return True

    @_utils.valid_kwargs('domain_id')
    def list_roles(self, **kwargs):
        """List Keystone roles.

        :param domain_id: domain id for listing roles (v3)

        :returns: a list of ``munch.Munch`` containing the role description.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        v2 = self._is_client_version('identity', 2)
        url = '/OS-KSADM/roles' if v2 else '/roles'
        data = self._identity_client.get(
            url, params=kwargs, error_message="Failed to list roles")
        return self._normalize_roles(self._get_and_munchify('roles', data))

    @_utils.valid_kwargs('domain_id')
    def search_roles(self, name_or_id=None, filters=None, **kwargs):
        """Seach Keystone roles.

        :param string name: role name or id.
        :param dict filters: a dict containing additional filters to use.
        :param domain_id: domain id (v3)

        :returns: a list of ``munch.Munch`` containing the role description.
            Each ``munch.Munch`` contains the following attributes::

                - id: <role id>
                - name: <role name>
                - description: <role description>

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        roles = self.list_roles(**kwargs)
        return _utils._filter_list(roles, name_or_id, filters)

    @_utils.valid_kwargs('domain_id')
    def get_role(self, name_or_id, filters=None, **kwargs):
        """Get exactly one Keystone role.

        :param id: role name or id.
        :param filters: a dict containing additional filters to use.
        :param domain_id: domain id (v3)

        :returns: a single ``munch.Munch`` containing the role description.
            Each ``munch.Munch`` contains the following attributes::

                - id: <role id>
                - name: <role name>
                - description: <role description>

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        return _utils._get_entity(self, 'role', name_or_id, filters, **kwargs)

    def _keystone_v2_role_assignments(self, user, project=None,
                                      role=None, **kwargs):
        data = self._identity_client.get(
            "/tenants/{tenant}/users/{user}/roles".format(
                tenant=project, user=user),
            error_message="Failed to list role assignments")

        roles = self._get_and_munchify('roles', data)

        ret = []
        for tmprole in roles:
            if role is not None and role != tmprole.id:
                continue
            ret.append({
                'role': {
                    'id': tmprole.id
                },
                'scope': {
                    'project': {
                        'id': project,
                    }
                },
                'user': {
                    'id': user,
                }
            })
        return ret

    def _keystone_v3_role_assignments(self, **filters):
        # NOTE(samueldmq): different parameters have different representation
        # patterns as query parameters in the call to the list role assignments
        # API. The code below handles each set of patterns separately and
        # renames the parameters names accordingly, ignoring 'effective',
        # 'include_names' and 'include_subtree' whose do not need any renaming.
        for k in ('group', 'role', 'user'):
            if k in filters:
                filters[k + '.id'] = filters[k]
                del filters[k]
        for k in ('project', 'domain'):
            if k in filters:
                filters['scope.' + k + '.id'] = filters[k]
                del filters[k]
        if 'os_inherit_extension_inherited_to' in filters:
            filters['scope.OS-INHERIT:inherited_to'] = (
                filters['os_inherit_extension_inherited_to'])
            del filters['os_inherit_extension_inherited_to']

        data = self._identity_client.get(
            '/role_assignments', params=filters,
            error_message="Failed to list role assignments")
        return self._get_and_munchify('role_assignments', data)

    def list_role_assignments(self, filters=None):
        """List Keystone role assignments

        :param dict filters: Dict of filter conditions. Acceptable keys are:

            * 'user' (string) - User ID to be used as query filter.
            * 'group' (string) - Group ID to be used as query filter.
            * 'project' (string) - Project ID to be used as query filter.
            * 'domain' (string) - Domain ID to be used as query filter.
            * 'role' (string) - Role ID to be used as query filter.
            * 'os_inherit_extension_inherited_to' (string) - Return inherited
              role assignments for either 'projects' or 'domains'
            * 'effective' (boolean) - Return effective role assignments.
            * 'include_subtree' (boolean) - Include subtree

            'user' and 'group' are mutually exclusive, as are 'domain' and
            'project'.

            NOTE: For keystone v2, only user, project, and role are used.
                  Project and user are both required in filters.

        :returns: a list of ``munch.Munch`` containing the role assignment
            description. Contains the following attributes::

                - id: <role id>
                - user|group: <user or group id>
                - project|domain: <project or domain id>

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        # NOTE(samueldmq): although 'include_names' is a valid query parameter
        # in the keystone v3 list role assignments API, it would have NO effect
        # on shade due to normalization. It is not documented as an acceptable
        # filter in the docs above per design!

        if not filters:
            filters = {}

        # NOTE(samueldmq): the docs above say filters are *IDs*, though if
        # munch.Munch objects are passed, this still works for backwards
        # compatibility as keystoneclient allows either IDs or objects to be
        # passed in.
        # TODO(samueldmq): fix the docs above to advertise munch.Munch objects
        # can be provided as parameters too
        for k, v in filters.items():
            if isinstance(v, munch.Munch):
                filters[k] = v['id']

        if self._is_client_version('identity', 2):
            if filters.get('project') is None or filters.get('user') is None:
                raise exc.OpenStackCloudException(
                    "Must provide project and user for keystone v2"
                )
            assignments = self._keystone_v2_role_assignments(**filters)
        else:
            assignments = self._keystone_v3_role_assignments(**filters)

        return _utils.normalize_role_assignments(assignments)

    @_utils.valid_kwargs('domain_id')
    def create_role(self, name, **kwargs):
        """Create a Keystone role.

        :param string name: The name of the role.
        :param domain_id: domain id (v3)

        :returns: a ``munch.Munch`` containing the role description

        :raise OpenStackCloudException: if the role cannot be created
        """
        v2 = self._is_client_version('identity', 2)
        url = '/OS-KSADM/roles' if v2 else '/roles'
        kwargs['name'] = name
        msg = 'Failed to create role {name}'.format(name=name)
        data = self._identity_client.post(
            url, json={'role': kwargs}, error_message=msg)
        role = self._get_and_munchify('role', data)
        return self._normalize_role(role)

    @_utils.valid_kwargs('domain_id')
    def update_role(self, name_or_id, name, **kwargs):
        """Update a Keystone role.

        :param name_or_id: Name or id of the role to update
        :param string name: The new role name
        :param domain_id: domain id

        :returns: a ``munch.Munch`` containing the role description

        :raise OpenStackCloudException: if the role cannot be created
        """
        if self._is_client_version('identity', 2):
            raise exc.OpenStackCloudUnavailableFeature(
                'Unavailable Feature: Role update requires Identity v3'
            )
        kwargs['name_or_id'] = name_or_id
        role = self.get_role(**kwargs)
        if role is None:
            self.log.debug(
                "Role %s not found for updating", name_or_id)
            return False
        msg = 'Failed to update role {name}'.format(name=name_or_id)
        json_kwargs = {'role_id': role.id, 'role': {'name': name}}
        data = self._identity_client.patch('/roles', error_message=msg,
                                           json=json_kwargs)
        role = self._get_and_munchify('role', data)
        return self._normalize_role(role)

    @_utils.valid_kwargs('domain_id')
    def delete_role(self, name_or_id, **kwargs):
        """Delete a Keystone role.

        :param string id: Name or id of the role to delete.
        :param domain_id: domain id (v3)

        :returns: True if delete succeeded, False otherwise.

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the OpenStack API call.
        """
        role = self.get_role(name_or_id, **kwargs)
        if role is None:
            self.log.debug(
                "Role %s not found for deleting", name_or_id)
            return False

        v2 = self._is_client_version('identity', 2)
        url = '{preffix}/{id}'.format(
            preffix='/OS-KSADM/roles' if v2 else '/roles', id=role['id'])
        error_msg = "Unable to delete role {name}".format(name=name_or_id)
        self._identity_client.delete(url, error_message=error_msg)

        return True

    def _get_grant_revoke_params(self, role, user=None, group=None,
                                 project=None, domain=None):
        role = self.get_role(role)
        if role is None:
            return {}
        data = {'role': role.id}

        # domain and group not available in keystone v2.0
        is_keystone_v2 = self._is_client_version('identity', 2)

        filters = {}
        if not is_keystone_v2 and domain:
            filters['domain_id'] = data['domain'] = \
                self.get_domain(domain)['id']

        if user:
            if domain:
                data['user'] = self.get_user(user,
                                             domain_id=filters['domain_id'],
                                             filters=filters)
            else:
                data['user'] = self.get_user(user, filters=filters)

        if project:
            # drop domain in favor of project
            data.pop('domain', None)
            data['project'] = self.get_project(project, filters=filters)

        if not is_keystone_v2 and group:
            data['group'] = self.get_group(group, filters=filters)

        return data

    def grant_role(self, name_or_id, user=None, group=None,
                   project=None, domain=None, wait=False, timeout=60):
        """Grant a role to a user.

        :param string name_or_id: The name or id of the role.
        :param string user: The name or id of the user.
        :param string group: The name or id of the group. (v3)
        :param string project: The name or id of the project.
        :param string domain: The id of the domain. (v3)
        :param bool wait: Wait for role to be granted
        :param int timeout: Timeout to wait for role to be granted

        NOTE: domain is a required argument when the grant is on a project,
            user or group specified by name. In that situation, they are all
            considered to be in that domain. If different domains are in use
            in the same role grant, it is required to specify those by ID.

        NOTE: for wait and timeout, sometimes granting roles is not
              instantaneous.

        NOTE: project is required for keystone v2

        :returns: True if the role is assigned, otherwise False

        :raise OpenStackCloudException: if the role cannot be granted
        """
        data = self._get_grant_revoke_params(name_or_id, user, group,
                                             project, domain)
        filters = data.copy()
        if not data:
            raise exc.OpenStackCloudException(
                'Role {0} not found.'.format(name_or_id))

        if data.get('user') is not None and data.get('group') is not None:
            raise exc.OpenStackCloudException(
                'Specify either a group or a user, not both')
        if data.get('user') is None and data.get('group') is None:
            raise exc.OpenStackCloudException(
                'Must specify either a user or a group')
        if self._is_client_version('identity', 2) and \
                data.get('project') is None:
            raise exc.OpenStackCloudException(
                'Must specify project for keystone v2')

        if self.list_role_assignments(filters=filters):
            self.log.debug('Assignment already exists')
            return False

        error_msg = "Error granting access to role: {0}".format(data)
        if self._is_client_version('identity', 2):
            # For v2.0, only tenant/project assignment is supported
            url = "/tenants/{t}/users/{u}/roles/OS-KSADM/{r}".format(
                t=data['project']['id'], u=data['user']['id'], r=data['role'])

            self._identity_client.put(url, error_message=error_msg,
                                      endpoint_filter={'interface': 'admin'})
        else:
            if data.get('project') is None and data.get('domain') is None:
                raise exc.OpenStackCloudException(
                    'Must specify either a domain or project')

            # For v3, figure out the assignment type and build the URL
            if data.get('domain'):
                url = "/domains/{}".format(data['domain'])
            else:
                url = "/projects/{}".format(data['project']['id'])
            if data.get('group'):
                url += "/groups/{}".format(data['group']['id'])
            else:
                url += "/users/{}".format(data['user']['id'])
            url += "/roles/{}".format(data.get('role'))

            self._identity_client.put(url, error_message=error_msg)

        if wait:
            for count in utils.iterate_timeout(
                    timeout,
                    "Timeout waiting for role to be granted"):
                if self.list_role_assignments(filters=filters):
                    break
        return True

    def revoke_role(self, name_or_id, user=None, group=None,
                    project=None, domain=None, wait=False, timeout=60):
        """Revoke a role from a user.

        :param string name_or_id: The name or id of the role.
        :param string user: The name or id of the user.
        :param string group: The name or id of the group. (v3)
        :param string project: The name or id of the project.
        :param string domain: The id of the domain. (v3)
        :param bool wait: Wait for role to be revoked
        :param int timeout: Timeout to wait for role to be revoked

        NOTE: for wait and timeout, sometimes revoking roles is not
              instantaneous.

        NOTE: project is required for keystone v2

        :returns: True if the role is revoke, otherwise False

        :raise OpenStackCloudException: if the role cannot be removed
        """
        data = self._get_grant_revoke_params(name_or_id, user, group,
                                             project, domain)
        filters = data.copy()

        if not data:
            raise exc.OpenStackCloudException(
                'Role {0} not found.'.format(name_or_id))

        if data.get('user') is not None and data.get('group') is not None:
            raise exc.OpenStackCloudException(
                'Specify either a group or a user, not both')
        if data.get('user') is None and data.get('group') is None:
            raise exc.OpenStackCloudException(
                'Must specify either a user or a group')
        if self._is_client_version('identity', 2) and \
                data.get('project') is None:
            raise exc.OpenStackCloudException(
                'Must specify project for keystone v2')

        if not self.list_role_assignments(filters=filters):
            self.log.debug('Assignment does not exist')
            return False

        error_msg = "Error revoking access to role: {0}".format(data)
        if self._is_client_version('identity', 2):
            # For v2.0, only tenant/project assignment is supported
            url = "/tenants/{t}/users/{u}/roles/OS-KSADM/{r}".format(
                t=data['project']['id'], u=data['user']['id'], r=data['role'])

            self._identity_client.delete(
                url, error_message=error_msg,
                endpoint_filter={'interface': 'admin'})
        else:
            if data.get('project') is None and data.get('domain') is None:
                raise exc.OpenStackCloudException(
                    'Must specify either a domain or project')

            # For v3, figure out the assignment type and build the URL
            if data.get('domain'):
                url = "/domains/{}".format(data['domain'])
            else:
                url = "/projects/{}".format(data['project']['id'])
            if data.get('group'):
                url += "/groups/{}".format(data['group']['id'])
            else:
                url += "/users/{}".format(data['user']['id'])
            url += "/roles/{}".format(data.get('role'))

            self._identity_client.delete(url, error_message=error_msg)

        if wait:
            for count in utils.iterate_timeout(
                    timeout,
                    "Timeout waiting for role to be revoked"):
                if not self.list_role_assignments(filters=filters):
                    break
        return True

    def _get_project_id_param_dict(self, name_or_id):
        if name_or_id:
            project = self.get_project(name_or_id)
            if not project:
                return {}
            if self._is_client_version('identity', 3):
                return {'default_project_id': project['id']}
            else:
                return {'tenant_id': project['id']}
        else:
            return {}

    def _get_domain_id_param_dict(self, domain_id):
        """Get a useable domain."""

        # Keystone v3 requires domains for user and project creation. v2 does
        # not. However, keystone v2 does not allow user creation by non-admin
        # users, so we can throw an error to the user that does not need to
        # mention api versions
        if self._is_client_version('identity', 3):
            if not domain_id:
                raise exc.OpenStackCloudException(
                    "User or project creation requires an explicit"
                    " domain_id argument.")
            else:
                return {'domain_id': domain_id}
        else:
            return {}

    def _get_identity_params(self, domain_id=None, project=None):
        """Get the domain and project/tenant parameters if needed.

        keystone v2 and v3 are divergent enough that we need to pass or not
        pass project or tenant_id or domain or nothing in a sane manner.
        """
        ret = {}
        ret.update(self._get_domain_id_param_dict(domain_id))
        ret.update(self._get_project_id_param_dict(project))
        return ret
