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

from openstack.identity.v3 import credential
from openstack.identity.v3 import domain
from openstack.identity.v3 import endpoint
from openstack.identity.v3 import group
from openstack.identity.v3 import policy
from openstack.identity.v3 import project
from openstack.identity.v3 import service
from openstack.identity.v3 import user
from openstack import proxy


class Proxy(proxy.BaseProxy):

    def create_credential(self, **data):
        return credential.Credential(data).create(self.session)

    def delete_credential(self, value, ignore_missing=True):
        """Delete a credential

        :param value: The value can be either the ID of a credential or a
               :class:`~openstack.identity.v3.credential.Credential` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the credential does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        self._delete(credential.Credential, value, ignore_missing)

    def find_credential(self, name_or_id):
        return credential.Credential.find(self.session, name_or_id)

    def get_credential(self, **data):
        return credential.Credential(data).get(self.session)

    def list_credentials(self):
        return credential.Credential.list(self.session)

    def update_credential(self, **data):
        return credential.Credential(data).update(self.session)

    def create_domain(self, **data):
        return domain.Domain(data).create(self.session)

    def delete_domain(self, value, ignore_missing=True):
        """Delete a domain

        :param value: The value can be either the ID of a domain or a
                      :class:`~openstack.identity.v3.domain.Domain` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the domain does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        self._delete(domain.Domain, value, ignore_missing)

    def find_domain(self, name_or_id):
        return domain.Domain.find(self.session, name_or_id)

    def get_domain(self, **data):
        return domain.Domain(data).get(self.session)

    def list_domains(self):
        return domain.Domain.list(self.session)

    def update_domain(self, **data):
        return domain.Domain(data).update(self.session)

    def create_endpoint(self, **data):
        return endpoint.Endpoint(data).create(self.session)

    def delete_endpoint(self, value, ignore_missing=True):
        """Delete an endpoint

        :param value: The value can be either the ID of an endpoint or a
               :class:`~openstack.identity.v3.endpoint.Endpoint` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the endpoint does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        self._delete(endpoint.Endpoint, value, ignore_missing)

    def find_endpoint(self, name_or_id):
        return endpoint.Endpoint.find(self.session, name_or_id)

    def get_endpoint(self, **data):
        return endpoint.Endpoint(data).get(self.session)

    def list_endpoints(self):
        return endpoint.Endpoint.list(self.session)

    def update_endpoint(self, **data):
        return endpoint.Endpoint(data).update(self.session)

    def create_group(self, **data):
        return group.Group(data).create(self.session)

    def delete_group(self, value, ignore_missing=True):
        """Delete a group

        :param value: The value can be either the ID of a group or a
                      :class:`~openstack.identity.v3.group.Group` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the group does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        self._delete(group.Group, value, ignore_missing)

    def find_group(self, name_or_id):
        return group.Group.find(self.session, name_or_id)

    def get_group(self, **data):
        return group.Group(data).get(self.session)

    def list_groups(self):
        return group.Group.list(self.session)

    def update_group(self, **data):
        return group.Group(data).update(self.session)

    def create_policy(self, **data):
        return policy.Policy(data).create(self.session)

    def delete_policy(self, value, ignore_missing=True):
        """Delete a policy

        :param value: The value can be either the ID of a policy or a
                      :class:`~openstack.identity.v3.policy.Policy` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the policy does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        self._delete(policy.Policy, value, ignore_missing)

    def find_policy(self, name_or_id):
        return policy.Policy.find(self.session, name_or_id)

    def get_policy(self, **data):
        return policy.Policy(data).get(self.session)

    def list_policys(self):
        return policy.Policy.list(self.session)

    def update_policy(self, **data):
        return policy.Policy(data).update(self.session)

    def create_project(self, **data):
        return project.Project(data).create(self.session)

    def delete_project(self, value, ignore_missing=True):
        """Delete a project

        :param value: The value can be either the ID of a project or a
                      :class:`~openstack.identity.v3.project.Project` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the project does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        self._delete(project.Project, value, ignore_missing)

    def find_project(self, name_or_id):
        return project.Project.find(self.session, name_or_id)

    def get_project(self, **data):
        return project.Project(data).get(self.session)

    def list_projects(self):
        return project.Project.list(self.session)

    def update_project(self, **data):
        return project.Project(data).update(self.session)

    def create_service(self, **data):
        return service.Service(data).create(self.session)

    def delete_service(self, value, ignore_missing=True):
        """Delete a service

        :param value: The value can be either the ID of a service or a
                      :class:`~openstack.identity.v3.service.Service` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the service does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        self._delete(service.Service, value, ignore_missing)

    def find_service(self, name_or_id):
        return service.Service.find(self.session, name_or_id)

    def get_service(self, **data):
        return service.Service(data).get(self.session)

    def list_services(self):
        return service.Service.list(self.session)

    def update_service(self, **data):
        return service.Service(data).update(self.session)

    def create_user(self, **data):
        return user.User(data).create(self.session)

    def delete_user(self, value, ignore_missing=True):
        """Delete a user

        :param value: The value can be either the ID of a user or a
                      :class:`~openstack.identity.v3.user.User` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the user does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        self._delete(user.User, value, ignore_missing)

    def find_user(self, name_or_id):
        return user.User.find(self.session, name_or_id)

    def get_user(self, **data):
        return user.User(data).get(self.session)

    def list_users(self):
        return user.User.list(self.session)

    def update_user(self, **data):
        return user.User(data).update(self.session)
