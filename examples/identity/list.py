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

"""
List resources from the Identity service.

For a full guide see TODO(etoews):link to docs on developer.openstack.org
"""


def list_users(conn):
    print("List Users:")

    for user in conn.identity.users():
        print(user)


def list_credentials(conn):
    print("List Credentials:")

    for credential in conn.identity.credentials():
        print(credential)


def list_projects(conn):
    print("List Projects:")

    for project in conn.identity.projects():
        print(project)


def list_domains(conn):
    print("List Domains:")

    for domain in conn.identity.domains():
        print(domain)


def list_groups(conn):
    print("List Groups:")

    for group in conn.identity.groups():
        print(group)


def list_services(conn):
    print("List Services:")

    for service in conn.identity.services():
        print(service)


def list_endpoints(conn):
    print("List Endpoints:")

    for endpoint in conn.identity.endpoints():
        print(endpoint)


def list_regions(conn):
    print("List Regions:")

    for region in conn.identity.regions():
        print(region)


def list_roles(conn):
    print("List Roles:")

    for role in conn.identity.roles():
        print(role)


def list_role_domain_group_assignments(conn):
    print("List Roles assignments for a group on domain:")

    for role in conn.identity.role_domain_group_assignments():
        print(role)


def list_role_domain_user_assignments(conn):
    print("List Roles assignments for a user on domain:")

    for role in conn.identity.role_project_user_assignments():
        print(role)


def list_role_project_group_assignments(conn):
    print("List Roles assignments for a group on project:")

    for role in conn.identity.role_project_group_assignments():
        print(role)


def list_role_project_user_assignments(conn):
    print("List Roles assignments for a user on project:")

    for role in conn.identity.role_project_user_assignments():
        print(role)
