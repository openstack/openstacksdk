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

import warnings

from openstack.cloud import _utils
from openstack.cloud import openstackcloud
from openstack import exceptions
from openstack import utils
from openstack import warnings as os_warnings


class IdentityCloudMixin(openstackcloud._OpenStackCloudMixin):
    def _get_project_id_param_dict(self, name_or_id):
        if name_or_id:
            project = self.get_project(name_or_id)
            if not project:
                return {}
            if utils.supports_version(self.identity, '3'):
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
        if utils.supports_version(self.identity, '3'):
            if not domain_id:
                raise exceptions.SDKException(
                    "User or project creation requires an explicit domain_id "
                    "argument."
                )
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

    def list_projects(self, domain_id=None, name_or_id=None, filters=None):
        """List projects.

        With no parameters, returns a full listing of all visible projects.

        :param domain_id: Domain ID to scope the searched projects.
        :param name_or_id: Name or ID of the project(s).
        :param filters: A dictionary of meta data to use for further filtering.
            Elements of this dictionary may, themselves, be dictionaries.
            Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR

            A string containing a jmespath expression for further filtering.
            Example::

                "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A list of identity ``Project`` objects.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        if not filters:
            filters = {}
        query = dict(**filters)
        if name_or_id:
            query['name'] = name_or_id
        if domain_id:
            query['domain_id'] = domain_id

        return list(self.identity.projects(**query))

    def search_projects(self, name_or_id=None, filters=None, domain_id=None):
        """Backwards compatibility method for search_projects

        search_projects originally had a parameter list that was name_or_id,
        filters and list had domain_id first. This method exists in this form
        to allow code written with positional parameter to still work. But
        really, use keyword arguments.

        :param name_or_id: Name or ID of the project(s).
        :param filters: dictionary of meta data to use for further filtering.
            Elements of this dictionary may, themselves, be dictionaries.
            Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR

            A string containing a jmespath expression for further filtering.
            Example::

                "[?last_name==`Smith`] | [?other.gender]==`Female`]"
        :param domain_id: Domain ID to scope the searched projects.
        :returns: A list of identity ``Project`` objects.
        """
        projects = self.list_projects(domain_id=domain_id, filters=filters)
        return _utils._filter_list(projects, name_or_id, filters)

    def get_project(self, name_or_id, filters=None, domain_id=None):
        """Get exactly one project.

        :param name_or_id: Name or unique ID of the project.
        :param filters: **DEPRECATED** A dictionary of meta data to use for
            further filtering. Elements of this dictionary may, themselves, be
            dictionaries. Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR

            A string containing a jmespath expression for further filtering.
            Example::

                "[?last_name==`Smith`] | [?other.gender]==`Female`]"
        :param domain_id: Domain ID to scope the retrieved project.

        :returns: An identity ``Project`` object.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        if filters is not None:
            warnings.warn(
                "the 'filters' argument is deprecated; use "
                "'search_projects' instead",
                os_warnings.RemovedInSDK60Warning,
            )
            entities = self.search_projects(
                name_or_id, filters, domain_id=domain_id
            )
            if not entities:
                return None

            if len(entities) > 1:
                raise exceptions.SDKException(
                    f"Multiple matches found for {name_or_id}",
                )

            return entities[0]

        return self.identity.find_project(
            name_or_id=name_or_id, domain_id=domain_id
        )

    def update_project(
        self,
        name_or_id,
        enabled=None,
        domain_id=None,
        **kwargs,
    ):
        """Update a project

        :param name_or_id: Name or unique ID of the project.
        :param enabled: Whether the project is enabled or not.
        :param domain_id: Domain ID to scope the retrieved project.
        :returns: An identity ``Project`` object.
        """
        project = self.identity.find_project(
            name_or_id=name_or_id,
            domain_id=domain_id,
            ignore_missing=False,
        )
        if not project:
            raise exceptions.SDKException(f"Project {name_or_id} not found.")
        if enabled is not None:
            kwargs.update({'enabled': enabled})
        project = self.identity.update_project(project, **kwargs)
        return project

    def create_project(
        self,
        name,
        domain_id,
        description=None,
        enabled=True,
        **kwargs,
    ):
        """Create a project.

        :param name:
        :param domain_id:
        :param description:
        :param enabled:
        :returns: An identity ``Project`` object.
        """
        attrs = dict(
            name=name,
            description=description,
            domain_id=domain_id,
            is_enabled=enabled,
        )
        if kwargs:
            attrs.update(kwargs)
        return self.identity.create_project(**attrs)

    def delete_project(self, name_or_id, domain_id=None):
        """Delete a project.

        :param name_or_id: Name or unique ID of the project.
        :param domain_id: Domain ID to scope the retrieved project.

        :returns: True if delete succeeded, False if the project was not found.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call
        """
        try:
            project = self.identity.find_project(
                name_or_id=name_or_id, domain_id=domain_id, ignore_missing=True
            )
            if not project:
                self.log.debug("Project %s not found for deleting", name_or_id)
                return False
            self.identity.delete_project(project)
            return True
        except exceptions.SDKException:
            self.log.exception(f"Error in deleting project {name_or_id}")
            return False

    @_utils.valid_kwargs('domain_id', 'name')
    def list_users(self, **kwargs):
        """List users.

        :param name:
        :param domain_id: Domain ID to scope the retrieved users.

        :returns: A list of identity ``User`` objects.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        return list(self.identity.users(**kwargs))

    def search_users(self, name_or_id=None, filters=None, domain_id=None):
        """Search users.

        :param name_or_id: Name or ID of the user(s).
        :param domain_id: Domain ID to scope the retrieved users.
        :param filters: dictionary of meta data to use for further filtering.
            Elements of this dictionary may, themselves, be dictionaries.
            Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR

            A string containing a jmespath expression for further filtering.
            Example::

                "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A list of identity ``User`` objects
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        kwargs = {}
        # NOTE(jdwidari) if name_or_id isn't UUID like then make use of server-
        # side filter for user name https://bit.ly/2qh0Ijk
        # especially important when using LDAP and using page to limit results
        if name_or_id and not _utils._is_uuid_like(name_or_id):
            kwargs['name'] = name_or_id
        if domain_id:
            kwargs['domain_id'] = domain_id
        users = self.list_users(**kwargs)
        return _utils._filter_list(users, name_or_id, filters)

    # TODO(stephenfin): Remove 'filters' in a future major version
    def get_user(self, name_or_id, filters=None, domain_id=None):
        """Get exactly one user.

        :param name_or_id: Name or unique ID of the user.
        :param filters: **DEPRECATED** A dictionary of meta data to use for
            further filtering. Elements of this dictionary may, themselves, be
            dictionaries. Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR

            A string containing a jmespath expression for further filtering.
            Example::

                "[?last_name==`Smith`] | [?other.gender]==`Female`]"
        :param domain_id: Domain ID to scope the retrieved user.

        :returns: an identity ``User`` object
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        if filters is not None:
            warnings.warn(
                "the 'filters' argument is deprecated; use "
                "'search_user' instead",
                os_warnings.RemovedInSDK60Warning,
            )
            entities = self.search_users(
                name_or_id, filters, domain_id=domain_id
            )
            if not entities:
                return None

            if len(entities) > 1:
                raise exceptions.SDKException(
                    f"Multiple matches found for {name_or_id}",
                )

        return self.identity.find_user(name_or_id, domain_id=domain_id)

    # TODO(stephenfin): Remove normalize since it doesn't do anything
    def get_user_by_id(self, user_id, normalize=None):
        """Get a user by ID.

        :param string user_id: user ID
        :returns: an identity ``User`` object
        """
        if normalize is not None:
            warnings.warn(
                "The 'normalize' field is unnecessary and will be removed in "
                "a future release.",
                os_warnings.RemovedInSDK60Warning,
            )

        return self.identity.get_user(user_id)

    @_utils.valid_kwargs(
        'name',
        'email',
        'enabled',
        'domain_id',
        'password',
        'description',
        'default_project',
    )
    def update_user(self, name_or_id, **kwargs):
        user_kwargs = {}
        if 'domain_id' in kwargs and kwargs['domain_id']:
            user_kwargs['domain_id'] = kwargs['domain_id']
        user = self.get_user(name_or_id, **user_kwargs)

        # TODO(mordred) When this changes to REST, force interface=admin
        # in the adapter call if it's an admin force call (and figure out how
        # to make that disctinction)
        # NOTE(samueldmq): now this is a REST call and domain_id is dropped
        # if None. keystoneclient drops keys with None values.
        if 'domain_id' in kwargs and kwargs['domain_id'] is None:
            del kwargs['domain_id']
        user = self.identity.update_user(user, **kwargs)

        return user

    def create_user(
        self,
        name,
        password=None,
        email=None,
        default_project=None,
        enabled=True,
        domain_id=None,
        description=None,
    ):
        """Create a user."""
        params = self._get_identity_params(domain_id, default_project)
        params.update({'name': name, 'email': email, 'enabled': enabled})
        if password is not None:
            params['password'] = password
        if description is not None:
            params['description'] = description

        user = self.identity.create_user(**params)

        return user

    @_utils.valid_kwargs('domain_id')
    def delete_user(self, name_or_id, **kwargs):
        try:
            user = self.get_user(name_or_id, **kwargs)
            if not user:
                self.log.debug(f"User {name_or_id} not found for deleting")
                return False

            self.identity.delete_user(user)
            return True

        except exceptions.SDKException:
            self.log.exception(f"Error in deleting user {name_or_id}")
            return False

    def _get_user_and_group(self, user_name_or_id, group_name_or_id):
        user = self.get_user(user_name_or_id)
        if not user:
            raise exceptions.SDKException(f'User {user_name_or_id} not found')

        group = self.get_group(group_name_or_id)
        if not group:
            raise exceptions.SDKException(
                f'Group {group_name_or_id} not found'
            )

        return (user, group)

    def add_user_to_group(self, name_or_id, group_name_or_id):
        """Add a user to a group.

        :param name_or_id: Name or unique ID of the user.
        :param group_name_or_id: Group name or ID

        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call
        """
        user, group = self._get_user_and_group(name_or_id, group_name_or_id)

        self.identity.add_user_to_group(user, group)

    def is_user_in_group(self, name_or_id, group_name_or_id):
        """Check to see if a user is in a group.

        :param name_or_id: Name or unique ID of the user.
        :param group_name_or_id: Group name or ID

        :returns: True if user is in the group, False otherwise
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call
        """
        user, group = self._get_user_and_group(name_or_id, group_name_or_id)

        return self.identity.check_user_in_group(user, group)

    def remove_user_from_group(self, name_or_id, group_name_or_id):
        """Remove a user from a group.

        :param name_or_id: Name or unique ID of the user.
        :param group_name_or_id: Group name or ID

        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call
        """
        user, group = self._get_user_and_group(name_or_id, group_name_or_id)

        self.identity.remove_user_from_group(user, group)

    @_utils.valid_kwargs('type', 'service_type', 'description')
    def create_service(self, name, enabled=True, **kwargs):
        """Create a service.

        :param name: Service name.
        :param type: Service type. (type or service_type required.)
        :param service_type: Service type. (type or service_type required.)
        :param description: Service description (optional).
        :param enabled: Whether the service is enabled (v3 only)

        :returns: an identity ``Service`` object
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        type_ = kwargs.pop('type', None)
        service_type = kwargs.pop('service_type', None)

        # TODO(mordred) When this changes to REST, force interface=admin
        # in the adapter call
        kwargs['type'] = type_ or service_type
        kwargs['is_enabled'] = enabled
        kwargs['name'] = name

        return self.identity.create_service(**kwargs)

    @_utils.valid_kwargs(
        'name', 'enabled', 'type', 'service_type', 'description'
    )
    def update_service(self, name_or_id, **kwargs):
        # NOTE(SamYaple): Keystone v3 only accepts 'type' but shade accepts
        #                 both 'type' and 'service_type' with a preference
        #                 towards 'type'
        type_ = kwargs.pop('type', None)
        service_type = kwargs.pop('service_type', None)
        if type_ or service_type:
            kwargs['type'] = type_ or service_type

        service = self.get_service(name_or_id)
        return self.identity.update_service(service, **kwargs)

    def list_services(self):
        """List all Keystone services.

        :returns: A list of identity ``Service`` object
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        return list(self.identity.services())

    def search_services(self, name_or_id=None, filters=None):
        """Search Keystone services.

        :param name_or_id: Name or ID of the service(s).
        :param filters: dictionary of meta data to use for further filtering.
            Elements of this dictionary may, themselves, be dictionaries.
            Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR

            A string containing a jmespath expression for further filtering.
            Example::

                "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: a list of identity ``Service`` objects
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        services = self.list_services()
        return _utils._filter_list(services, name_or_id, filters)

    # TODO(stephenfin): Remove 'filters' in a future major version
    def get_service(self, name_or_id, filters=None):
        """Get exactly one Keystone service.

        :param name_or_id: Name or unique ID of the service.

        :returns: an identity ``Service`` object
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call or if multiple matches are
            found.
        """
        if filters is not None:
            warnings.warn(
                "the 'filters' argument is deprecated; use "
                "'search_services' instead",
                os_warnings.RemovedInSDK60Warning,
            )
            entities = self.search_services(name_or_id, filters)
            if not entities:
                return None

            if len(entities) > 1:
                raise exceptions.SDKException(
                    f"Multiple matches found for {name_or_id}",
                )

            return entities[0]

        return self.identity.find_service(name_or_id=name_or_id)

    def delete_service(self, name_or_id):
        """Delete a Keystone service.

        :param name_or_id: Name or unique ID of the service.

        :returns: True if delete succeeded, False otherwise.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call
        """
        service = self.get_service(name_or_id=name_or_id)
        if service is None:
            self.log.debug("Service %s not found for deleting", name_or_id)
            return False

        try:
            self.identity.delete_service(service)
            return True
        except exceptions.SDKException:
            self.log.exception(
                'Failed to delete service {id}'.format(id=service['id'])
            )
            return False

    @_utils.valid_kwargs('public_url', 'internal_url', 'admin_url')
    def create_endpoint(
        self,
        service_name_or_id,
        url=None,
        interface=None,
        region=None,
        enabled=True,
        **kwargs,
    ):
        """Create a Keystone endpoint.

        :param service_name_or_id: Service name or id for this endpoint.
        :param url: URL of the endpoint
        :param interface: Interface type of the endpoint
        :param public_url: Endpoint public URL.
        :param internal_url: Endpoint internal URL.
        :param admin_url: Endpoint admin URL.
        :param region: Endpoint region.
        :param enabled: Whether the endpoint is enabled

        :returns: A list of identity ``Endpoint`` objects
        :raises: :class:`~openstack.exceptions.SDKException` if the service
            cannot be found or if something goes wrong during the OpenStack API
            call.
        """
        public_url = kwargs.pop('public_url', None)
        internal_url = kwargs.pop('internal_url', None)
        admin_url = kwargs.pop('admin_url', None)

        if (url or interface) and (public_url or internal_url or admin_url):
            raise exceptions.SDKException(
                "create_endpoint takes either url and interface OR "
                "public_url, internal_url, admin_url"
            )

        service = self.get_service(name_or_id=service_name_or_id)
        if service is None:
            raise exceptions.SDKException(
                f"service {service_name_or_id} not found"
            )

        endpoints_args = []
        if url:
            # v3 in use, v3-like arguments, one endpoint created
            endpoints_args.append(
                {
                    'url': url,
                    'interface': interface,
                    'service_id': service['id'],
                    'enabled': enabled,
                    'region_id': region,
                }
            )
        else:
            # v3 in use, v2.0-like arguments, one endpoint created for each
            # interface url provided
            endpoint_args = {
                'region_id': region,
                'enabled': enabled,
                'service_id': service['id'],
            }
            if public_url:
                endpoint_args.update(
                    {'url': public_url, 'interface': 'public'}
                )
                endpoints_args.append(endpoint_args.copy())
            if internal_url:
                endpoint_args.update(
                    {'url': internal_url, 'interface': 'internal'}
                )
                endpoints_args.append(endpoint_args.copy())
            if admin_url:
                endpoint_args.update({'url': admin_url, 'interface': 'admin'})
                endpoints_args.append(endpoint_args.copy())

        endpoints = []
        for args in endpoints_args:
            endpoints.append(self.identity.create_endpoint(**args))
        return endpoints

    @_utils.valid_kwargs(
        'enabled', 'service_name_or_id', 'url', 'interface', 'region'
    )
    def update_endpoint(self, endpoint_id, **kwargs):
        service_name_or_id = kwargs.pop('service_name_or_id', None)
        if service_name_or_id is not None:
            kwargs['service_id'] = service_name_or_id
        if 'region' in kwargs:
            kwargs['region_id'] = kwargs.pop('region')

        return self.identity.update_endpoint(endpoint_id, **kwargs)

    def list_endpoints(self):
        """List Keystone endpoints.

        :returns: A list of identity ``Endpoint`` objects
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        return list(self.identity.endpoints())

    def search_endpoints(self, id=None, filters=None):
        """List Keystone endpoints.

        :param id: ID of endpoint(s).
        :param filters: dictionary of meta data to use for further filtering.
            Elements of this dictionary may, themselves, be dictionaries.
            Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR

            A string containing a jmespath expression for further filtering.
            Example::

                "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A list of identity ``Endpoint`` objects
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        # NOTE(SamYaple): With keystone v3 we can filter directly via the
        # the keystone api, but since the return of all the endpoints even in
        # large environments is small, we can continue to filter in shade just
        # like the v2 api.
        endpoints = self.list_endpoints()
        return _utils._filter_list(endpoints, id, filters)

    # TODO(stephenfin): Remove 'filters' since it's a noop
    def get_endpoint(self, id, filters=None):
        """Get exactly one Keystone endpoint.

        :param id: ID of endpoint.
        :returns: An identity ``Endpoint`` object
        """
        if filters is not None:
            warnings.warn(
                "the 'filters' argument is deprecated; use "
                "'search_endpoints' instead",
                os_warnings.RemovedInSDK60Warning,
            )
            entities = self.search_endpoints(id, filters)
            if not entities:
                return None

            if len(entities) > 1:
                raise exceptions.SDKException(
                    f"Multiple matches found for {id}",
                )

            return entities[0]

        return self.identity.find_endpoint(name_or_id=id)

    def delete_endpoint(self, id):
        """Delete a Keystone endpoint.

        :param id: ID of the endpoint to delete.

        :returns: True if delete succeeded, False otherwise.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        endpoint = self.get_endpoint(id=id)
        if endpoint is None:
            self.log.debug("Endpoint %s not found for deleting", id)
            return False

        try:
            self.identity.delete_endpoint(id)
            return True
        except exceptions.SDKException:
            self.log.exception(f"Failed to delete endpoint {id}")
            return False

    def create_domain(self, name, description=None, enabled=True):
        """Create a domain.

        :param name: The name of the domain.
        :param description: A description of the domain.
        :param enabled: Is the domain enabled or not (default True).
        :returns: The created identity ``Endpoint`` object.
        :raises: :class:`~openstack.exceptions.SDKException` if the domain
            cannot be created.
        """
        domain_ref = {'name': name, 'enabled': enabled}
        if description is not None:
            domain_ref['description'] = description
        return self.identity.create_domain(**domain_ref)

    # TODO(stephenfin): domain_id and name_or_id are the same thing now;
    # deprecate one of them
    def update_domain(
        self,
        domain_id=None,
        name=None,
        description=None,
        enabled=None,
        name_or_id=None,
    ):
        """Update a Keystone domain

        :param domain_id:
        :param name:
        :param description:
        :param enabled:
        :param name_or_id: Name or unique ID of the domain.
        :returns: The updated identity ``Domain`` object.
        :raises: :class:`~openstack.exceptions.SDKException` if the domain
            cannot be updated
        """
        if domain_id is None:
            if name_or_id is None:
                raise exceptions.SDKException(
                    "You must pass either domain_id or name_or_id value"
                )
            dom = self.get_domain(None, name_or_id)
            if dom is None:
                raise exceptions.SDKException(
                    f"Domain {name_or_id} not found for updating"
                )
            domain_id = dom['id']

        domain_ref = {}
        domain_ref.update({'name': name} if name else {})
        domain_ref.update({'description': description} if description else {})
        domain_ref.update({'enabled': enabled} if enabled is not None else {})
        return self.identity.update_domain(domain_id, **domain_ref)

    # TODO(stephenfin): domain_id and name_or_id are the same thing now;
    # deprecate one of them
    def delete_domain(self, domain_id=None, name_or_id=None):
        """Delete a Keystone domain.

        :param domain_id: ID of the domain to delete.
        :param name_or_id: Name or unique ID of the domain.

        :returns: True if delete succeeded, False otherwise.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        try:
            if domain_id is None:
                if name_or_id is None:
                    raise exceptions.SDKException(
                        "You must pass either domain_id or name_or_id value"
                    )
                dom = self.get_domain(name_or_id=name_or_id)
                if dom is None:
                    self.log.debug(
                        "Domain %s not found for deleting", name_or_id
                    )
                    return False
                domain_id = dom['id']

            # A domain must be disabled before deleting
            self.identity.update_domain(domain_id, is_enabled=False)
            self.identity.delete_domain(domain_id, ignore_missing=False)

            return True
        except exceptions.SDKException:
            self.log.exception(f"Failed to delete domain {domain_id}")
            raise

    def list_domains(self, **filters):
        """List Keystone domains.

        :returns: A list of identity ``Domain`` objects.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        return list(self.identity.domains(**filters))

    # TODO(stephenfin): These arguments are backwards from everything else.
    def search_domains(self, filters=None, name_or_id=None):
        """Search Keystone domains.

        :param name_or_id: Name or ID of the domain(s).
        :param filters: dictionary of meta data to use for further filtering.
            Elements of this dictionary may, themselves, be dictionaries.
            Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR

            A string containing a jmespath expression for further filtering.
            Example::

                "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: a list of identity ``Domain`` objects
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        if filters is None:
            filters = {}
        if name_or_id is not None:
            domains = self.list_domains()
            return _utils._filter_list(domains, name_or_id, filters)
        else:
            return self.list_domains(**filters)

    # TODO(stephenfin): domain_id and name_or_id are the same thing now;
    # deprecate one of them
    # TODO(stephenfin): Remove 'filters' in a future major version
    def get_domain(self, domain_id=None, name_or_id=None, filters=None):
        """Get exactly one Keystone domain.

        :param domain_id: ID of the domain.
        :param name_or_id: Name or unique ID of the domain.
        :param filters: **DEPRECATED** A dictionary of meta data to use for
            further filtering. Elements of this dictionary may, themselves, be
            dictionaries. Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR

            A string containing a jmespath expression for further filtering.
            Example::

                "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: an identity ``Domain`` object
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        if filters is not None:
            warnings.warn(
                "The 'filters' argument is deprecated for removal. It is a "
                "no-op and can be safely removed.",
                os_warnings.RemovedInSDK60Warning,
            )

        if domain_id is None:
            return self.identity.find_domain(name_or_id, ignore_missing=True)
        else:
            return self.identity.get_domain(domain_id)

    @_utils.valid_kwargs('domain_id')
    def list_groups(self, **kwargs):
        """List Keystone groups.

        :param domain_id: Domain ID.

        :returns: A list of identity ``Group`` objects
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        return list(self.identity.groups(**kwargs))

    def search_groups(self, name_or_id=None, filters=None, domain_id=None):
        """Search Keystone groups.

        :param name_or_id: Name or ID of the group(s).
        :param filters: dictionary of meta data to use for further filtering.
            Elements of this dictionary may, themselves, be dictionaries.
            Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR

            A string containing a jmespath expression for further filtering.
            Example::

                "[?last_name==`Smith`] | [?other.gender]==`Female`]"
        :param domain_id: Domain ID to scope the searched groups.

        :returns: A list of identity ``Group`` objects
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        groups = self.list_groups(domain_id=domain_id)
        return _utils._filter_list(groups, name_or_id, filters)

    # TODO(stephenfin): Remove 'filters' in a future major version
    def get_group(self, name_or_id, filters=None, domain_id=None):
        """Get exactly one Keystone group.

        :param name_or_id: Name or unique ID of the group(s).
        :param domain_id: Domain ID to scope the retrieved group.

        :returns: An identity ``Group`` object
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        if filters is not None:
            warnings.warn(
                "the 'filters' argument is deprecated; use "
                "'search_projects' instead",
                os_warnings.RemovedInSDK60Warning,
            )
            entities = self.search_groups(
                name_or_id, filters, domain_id=domain_id
            )
            if not entities:
                return None

            if len(entities) > 1:
                raise exceptions.SDKException(
                    f"Multiple matches found for {name_or_id}",
                )

            return entities[0]

        return self.identity.find_group(
            name_or_id=name_or_id, domain_id=domain_id
        )

    def create_group(self, name, description, domain=None):
        """Create a group.

        :param string name: Group name.
        :param string description: Group description.
        :param string domain: Domain name or ID for the group.

        :returns: An identity ``Group`` object
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        group_ref = {'name': name}
        if description:
            group_ref['description'] = description
        if domain:
            dom = self.get_domain(domain)
            if not dom:
                raise exceptions.SDKException(
                    f"Creating group {name} failed: Invalid domain {domain}"
                )
            group_ref['domain_id'] = dom['id']

        group = self.identity.create_group(**group_ref)

        return group

    def update_group(
        self,
        name_or_id,
        name=None,
        description=None,
        **kwargs,
    ):
        """Update an existing group

        :param name_or_id: Name or unique ID of the group.
        :param name: New group name.
        :param description: New group description.

        :returns: The updated identity ``Group`` object.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        group = self.identity.find_group(
            name_or_id, ignore_missing=False, **kwargs
        )

        group_ref = {}
        if name:
            group_ref['name'] = name
        if description:
            group_ref['description'] = description

        group = self.identity.update_group(group, **group_ref)

        return group

    def delete_group(self, name_or_id):
        """Delete a group

        :param name_or_id: Name or unique ID of the group.

        :returns: True if delete succeeded, False otherwise.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        try:
            group = self.identity.find_group(name_or_id, ignore_missing=True)
            if group is None:
                self.log.debug("Group %s not found for deleting", name_or_id)
                return False

            self.identity.delete_group(group)

            return True

        except exceptions.SDKException:
            self.log.exception(f"Unable to delete group {name_or_id}")
            return False

    def list_roles(self, **kwargs):
        """List Keystone roles.

        :returns: A list of identity ``Role`` objects
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        return list(self.identity.roles(**kwargs))

    def search_roles(self, name_or_id=None, filters=None, domain_id=None):
        """Seach Keystone roles.

        :param name: Name or ID of the role(s).
        :param filters: dictionary of meta data to use for further filtering.
            Elements of this dictionary may, themselves, be dictionaries.
            Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR

            A string containing a jmespath expression for further filtering.
            Example::

                "[?last_name==`Smith`] | [?other.gender]==`Female`]"
        :param domain_id: Domain ID to scope the searched roles.

        :returns: a list of identity ``Role`` objects
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        roles = self.list_roles(domain_id=domain_id)
        return _utils._filter_list(roles, name_or_id, filters)

    # TODO(stephenfin): Remove 'filters' in a future major version
    def get_role(self, name_or_id, filters=None, domain_id=None):
        """Get a Keystone role.

        :param name_or_id: Name or unique ID of the role.
        :param domain_id: Domain ID to scope the retrieved role.

        :returns: An identity ``Role`` object if found, else None.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        if filters is not None:
            warnings.warn(
                "the 'filters' argument is deprecated; use "
                "'search_roles' instead",
                os_warnings.RemovedInSDK60Warning,
            )
            entities = self.search_roles(
                name_or_id, filters, domain_id=domain_id
            )
            if not entities:
                return None

            if len(entities) > 1:
                raise exceptions.SDKException(
                    f"Multiple matches found for {name_or_id}",
                )

            return entities[0]

        return self.identity.find_role(
            name_or_id=name_or_id, domain_id=domain_id
        )

    def _keystone_v3_role_assignments(self, **filters):
        # NOTE(samueldmq): different parameters have different representation
        # patterns as query parameters in the call to the list role assignments
        # API. The code below handles each set of patterns separately and
        # renames the parameters names accordingly, ignoring 'effective',
        # 'include_names' and 'include_subtree' whose do not need any renaming.
        for k in ('group', 'role', 'user'):
            if k in filters:
                try:
                    filters[k + '.id'] = filters[k].id
                except AttributeError:
                    # Also this goes away in next patches
                    filters[k + '.id'] = filters[k]
                del filters[k]
        for k in ('project', 'domain'):
            if k in filters:
                try:
                    filters['scope.' + k + '.id'] = filters[k].id
                except AttributeError:
                    # NOTE(gtema): will be dropped once domains are switched to
                    # proxy
                    filters['scope.' + k + '.id'] = filters[k]
                del filters[k]
        if 'inherited_to' in filters:
            filters['scope.OS-INHERIT:inherited_to'] = filters['inherited_to']
            del filters['inherited_to']
        elif 'os_inherit_extension_inherited_to' in filters:
            warnings.warn(
                "os_inherit_extension_inherited_to is deprecated. Use "
                "inherited_to instead.",
                os_warnings.RemovedInSDK50Warning,
            )
            filters['scope.OS-INHERIT:inherited_to'] = filters[
                'os_inherit_extension_inherited_to'
            ]
            del filters['os_inherit_extension_inherited_to']

        return list(self.identity.role_assignments(**filters))

    def list_role_assignments(self, filters=None):
        """List Keystone role assignments

        :param dict filters: Dict of filter conditions. Acceptable keys are:

            * 'user' (string) - User ID to be used as query filter.
            * 'group' (string) - Group ID to be used as query filter.
            * 'project' (string) - Project ID to be used as query filter.
            * 'domain' (string) - Domain ID to be used as query filter.
            * 'system' (string) - System name to be used as query filter.
            * 'role' (string) - Role ID to be used as query filter.
            * 'inherited_to' (string) - Return inherited
              role assignments for either 'projects' or 'domains'.
            * 'os_inherit_extension_inherited_to' (string) - Deprecated; use
              'inherited_to' instead.
            * 'effective' (boolean) - Return effective role assignments.
            * 'include_subtree' (boolean) - Include subtree

              'user' and 'group' are mutually exclusive, as are 'domain' and
              'project'.

        :returns: A list of identity
            :class:`openstack.identity.v3.role_assignment.RoleAssignment`
            objects
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        # NOTE(samueldmq): although 'include_names' is a valid query parameter
        # in the keystone v3 list role assignments API, it would have NO effect
        # on shade due to normalization. It is not documented as an acceptable
        # filter in the docs above per design!

        if not filters:
            filters = {}

        # NOTE(samueldmq): the docs above say filters are *IDs*, though if
        # dict or Resource objects are passed, this still works for backwards
        # compatibility as keystoneclient allows either IDs or objects to be
        # passed in.
        # TODO(samueldmq): fix the docs above to advertise Resource objects
        # can be provided as parameters too
        for k, v in filters.items():
            if isinstance(v, dict):
                filters[k] = v['id']

        for k in ['role', 'group', 'user']:
            if k in filters:
                filters[f'{k}_id'] = filters.pop(k)

        for k in ['domain', 'project']:
            if k in filters:
                filters[f'scope_{k}_id'] = filters.pop(k)

        if 'system' in filters:
            system_scope = filters.pop('system')
            filters['scope.system'] = system_scope

        if 'os_inherit_extension_inherited_to' in filters:
            warnings.warn(
                "os_inherit_extension_inherited_to is deprecated. Use "
                "inherited_to instead.",
                os_warnings.RemovedInSDK50Warning,
            )
            filters['inherited_to'] = filters.pop(
                'os_inherit_extension_inherited_to'
            )

        return list(self.identity.role_assignments(**filters))

    @_utils.valid_kwargs('domain_id')
    def create_role(self, name, **kwargs):
        """Create a Keystone role.

        :param string name: The name of the role.
        :param domain_id: domain id (v3)
        :returns: an identity ``Role`` object
        :raises: :class:`~openstack.exceptions.SDKException` if the role cannot
            be created
        """
        kwargs['name'] = name
        return self.identity.create_role(**kwargs)

    @_utils.valid_kwargs('domain_id')
    def update_role(self, name_or_id, name, **kwargs):
        """Update a Keystone role.

        :param name_or_id: Name or unique ID of the role.
        :param string name: The new role name
        :param domain_id: domain id
        :returns: an identity ``Role`` object
        :raises: :class:`~openstack.exceptions.SDKException` if the role cannot
            be created
        """
        role = self.get_role(name_or_id, **kwargs)
        if role is None:
            self.log.debug("Role %s not found for updating", name_or_id)
            return False

        return self.identity.update_role(role, name=name, **kwargs)

    @_utils.valid_kwargs('domain_id')
    def delete_role(self, name_or_id, **kwargs):
        """Delete a Keystone role.

        :param name_or_id: Name or unique ID of the role.
        :param domain_id: domain id (v3)

        :returns: True if delete succeeded, False otherwise.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        role = self.get_role(name_or_id, **kwargs)
        if role is None:
            self.log.debug("Role %s not found for deleting", name_or_id)
            return False

        try:
            self.identity.delete_role(role)
            return True
        except exceptions.SDKException:
            self.log.exception(f"Unable to delete role {name_or_id}")
            raise

    def _get_grant_revoke_params(
        self,
        role,
        user=None,
        group=None,
        project=None,
        domain=None,
        system=None,
    ):
        data = {}
        search_args = {}
        if domain:
            data['domain'] = self.identity.find_domain(
                domain, ignore_missing=False
            )
            # We have domain. We should use it for further searching user,
            # group, role, project
            search_args['domain_id'] = data['domain'].id

        data['role'] = self.identity.find_role(role, ignore_missing=False)

        if user and group:
            raise exceptions.SDKException(
                'Specify either a group or a user, not both'
            )
        if user is None and group is None:
            raise exceptions.SDKException(
                'Must specify either a user or a group'
            )
        if project is None and domain is None and system is None:
            raise exceptions.SDKException(
                'Must specify either a domain, project or system'
            )

        if user:
            data['user'] = self.identity.find_user(
                user, ignore_missing=False, **search_args
            )
        if group:
            data['group'] = self.identity.find_group(
                group, ignore_missing=False, **search_args
            )
        if project:
            data['project'] = self.identity.find_project(
                project, ignore_missing=False, **search_args
            )

        return data

    def grant_role(
        self,
        name_or_id,
        user=None,
        group=None,
        project=None,
        domain=None,
        system=None,
        inherited=False,
        wait=False,
        timeout=60,
    ):
        """Grant a role to a user.

        :param string name_or_id: Name or unique ID of the role.
        :param string user: The name or id of the user.
        :param string group: The name or id of the group. (v3)
        :param string project: The name or id of the project.
        :param string domain: The id of the domain. (v3)
        :param bool system: The name of the system. (v3)
        :param bool inherited: Whether the role assignment is inherited. (v3)
        :param bool wait: Wait for role to be granted
        :param int timeout: Timeout to wait for role to be granted

         NOTE: domain is a required argument when the grant is on a project,
         user or group specified by name. In that situation, they are all
         considered to be in that domain. If different domains are in use in
         the same role grant, it is required to specify those by ID.

         NOTE: for wait and timeout, sometimes granting roles is not
         instantaneous.

        NOTE: precedence is given first to project, then domain, then system

        :returns: True if the role is assigned, otherwise False
        :raises: :class:`~openstack.exceptions.SDKException` if the role cannot
            be granted
        """
        data = self._get_grant_revoke_params(
            name_or_id,
            user=user,
            group=group,
            project=project,
            domain=domain,
            system=system,
        )

        user = data.get('user')
        group = data.get('group')
        project = data.get('project')
        domain = data.get('domain')
        role = data.get('role')

        if project:
            # Proceed with project - precedence over domain and system
            if user:
                has_role = self.identity.validate_user_has_project_role(
                    project, user, role, inherited=inherited
                )
                if has_role:
                    self.log.debug('Assignment already exists')
                    return False
                self.identity.assign_project_role_to_user(
                    project, user, role, inherited=inherited
                )
            else:
                has_role = self.identity.validate_group_has_project_role(
                    project, group, role, inherited=inherited
                )
                if has_role:
                    self.log.debug('Assignment already exists')
                    return False
                self.identity.assign_project_role_to_group(
                    project, group, role, inherited=inherited
                )
        elif domain:
            # Proceed with domain - precedence over system
            if user:
                has_role = self.identity.validate_user_has_domain_role(
                    domain, user, role, inherited=inherited
                )
                if has_role:
                    self.log.debug('Assignment already exists')
                    return False
                self.identity.assign_domain_role_to_user(
                    domain, user, role, inherited=inherited
                )
            else:
                has_role = self.identity.validate_group_has_domain_role(
                    domain, group, role, inherited=inherited
                )
                if has_role:
                    self.log.debug('Assignment already exists')
                    return False
                self.identity.assign_domain_role_to_group(
                    domain, group, role, inherited=inherited
                )
        else:
            # Proceed with system
            # System name must be 'all' due to checks performed in
            # _get_grant_revoke_params
            if user:
                has_role = self.identity.validate_user_has_system_role(
                    user, role, system
                )
                if has_role:
                    self.log.debug('Assignment already exists')
                    return False
                self.identity.assign_system_role_to_user(user, role, system)
            else:
                has_role = self.identity.validate_group_has_system_role(
                    group, role, system
                )
                if has_role:
                    self.log.debug('Assignment already exists')
                    return False
                self.identity.assign_system_role_to_group(group, role, system)
        return True

    def revoke_role(
        self,
        name_or_id,
        user=None,
        group=None,
        project=None,
        domain=None,
        system=None,
        inherited=False,
        wait=False,
        timeout=60,
    ):
        """Revoke a role from a user.

        :param string name_or_id: Name or unique ID of the role.
        :param string user: The name or id of the user.
        :param string group: The name or id of the group. (v3)
        :param string project: The name or id of the project.
        :param string domain: The id of the domain. (v3)
        :param bool system: The name of the system. (v3)
        :param bool inherited: Whether the role assignment is inherited.
        :param bool wait: Wait for role to be revoked
        :param int timeout: Timeout to wait for role to be revoked

            NOTE: for wait and timeout, sometimes revoking roles is not
            instantaneous.

            NOTE: project is required for keystone v2

        NOTE: precedence is given first to project, then domain, then system

        :returns: True if the role is revoke, otherwise False
        :raises: :class:`~openstack.exceptions.SDKException` if the role cannot
            be removed
        """
        data = self._get_grant_revoke_params(
            name_or_id,
            user=user,
            group=group,
            project=project,
            domain=domain,
            system=system,
        )

        user = data.get('user')
        group = data.get('group')
        project = data.get('project')
        domain = data.get('domain')
        role = data.get('role')

        if project:
            # Proceed with project - precedence over domain and system
            if user:
                has_role = self.identity.validate_user_has_project_role(
                    project, user, role, inherited=inherited
                )
                if not has_role:
                    self.log.debug('Assignment does not exists')
                    return False
                self.identity.unassign_project_role_from_user(
                    project, user, role, inherited=inherited
                )
            else:
                has_role = self.identity.validate_group_has_project_role(
                    project, group, role, inherited=inherited
                )
                if not has_role:
                    self.log.debug('Assignment does not exists')
                    return False
                self.identity.unassign_project_role_from_group(
                    project, group, role, inherited=inherited
                )
        elif domain:
            # Proceed with domain - precedence over system
            if user:
                has_role = self.identity.validate_user_has_domain_role(
                    domain, user, role, inherited=inherited
                )
                if not has_role:
                    self.log.debug('Assignment does not exists')
                    return False
                self.identity.unassign_domain_role_from_user(
                    domain, user, role, inherited=inherited
                )
            else:
                has_role = self.identity.validate_group_has_domain_role(
                    domain, group, role, inherited=inherited
                )
                if not has_role:
                    self.log.debug('Assignment does not exists')
                    return False
                self.identity.unassign_domain_role_from_group(
                    domain, group, role, inherited=inherited
                )
        else:
            # Proceed with system
            # System name must be 'all' due to checks performed in
            # _get_grant_revoke_params
            if user:
                has_role = self.identity.validate_user_has_system_role(
                    user, role, system
                )
                if not has_role:
                    self.log.debug('Assignment does not exist')
                    return False
                self.identity.unassign_system_role_from_user(
                    user, role, system
                )
            else:
                has_role = self.identity.validate_group_has_system_role(
                    group, role, system
                )
                if not has_role:
                    self.log.debug('Assignment does not exist')
                    return False
                self.identity.unassign_system_role_from_group(
                    group, role, system
                )
        return True
