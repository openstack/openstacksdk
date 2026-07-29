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

from keystoneauth1 import adapter

from openstack import exceptions
from openstack import resource
from openstack import utils


class EndpointGroup(resource.Resource):
    resource_key = 'endpoint_group'
    resources_key = 'endpoint_groups'
    base_path = '/OS-EP-FILTER/endpoint_groups'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    commit_method = 'PATCH'

    _query_mapping = resource.QueryParameters(
        'name', include_pagination_defaults=False
    )

    #: The description of the endpoint group. *Type: string*
    description = resource.Body('description')
    #: Describes the filtering performed by the endpoint group.
    #: The filter used must be an endpoint property, namely
    #: interface, service_id, or region.
    #: *Type: dict*
    filters = resource.Body('filters')
    #: The links for the endpoint group resource.
    links = resource.Body('links')
    #: The name of the endpoint group. *Type: string*
    name = resource.Body('name')

    def associate_project(
        self, session: adapter.Adapter, project_id: str
    ) -> None:
        """Associate project with endpoint group.

        :param session: The session to use for making this request.
        :param project_id: The ID of a project.
        :returns: None
        """
        url = utils.urljoin(
            '/OS-EP-FILTER/endpoint_groups',
            self.id,
            'projects',
            project_id,
        )
        response = session.put(url)
        exceptions.raise_from_response(response)

    def disassociate_project(
        self, session: adapter.Adapter, project_id: str
    ) -> None:
        """Disassociate project from endpoint group.

        :param session: The session to use for making this request.
        :param endpoint_id: The ID of a project.
        :returns: None
        """
        url = utils.urljoin(
            '/OS-EP-FILTER/endpoint_groups',
            self.id,
            'projects',
            project_id,
        )
        response = session.delete(url)
        exceptions.raise_from_response(response)


class ProjectEndpointGroup(EndpointGroup):
    base_path = '/OS-EP-FILTER/projects/%(project_id)s/endpoint_groups'

    #: The ID for the project from the URI of the resource
    project_id = resource.URI('project_id')

    # capabilities
    allow_create = False
    allow_fetch = False
    allow_commit = False
    allow_delete = False
    allow_list = True
