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

from openstack import exceptions
from openstack import resource
from openstack import utils


class GroupType(resource.Resource):
    resource_key = "group_type"
    resources_key = "group_types"
    base_path = "/group_types"

    # capabilities
    allow_fetch = True
    allow_create = True
    allow_delete = True
    allow_commit = True
    allow_list = True

    _max_microversion = "3.11"

    #: Properties
    #: The group type description.
    description = resource.Body("description")
    #: Contains the specifications for a group type.
    group_specs = resource.Body("group_specs", type=dict, default={})
    #: Whether the group type is publicly visible.
    is_public = resource.Body("is_public", type=bool)

    def fetch_group_specs(self, session):
        """Fetch group_specs of the group type.

        These are returned by default if the user has suitable permissions
        (i.e. you're an admin) but by default you also need the same
        permissions to access this API. That means this function is kind of
        useless. However, that is how the API was designed and it is
        theoretically possible that people will have modified their policy to
        allow this but not the other so we provide this anyway.

        :param session: The session to use for making this request.
        :returns: An updated version of this object.
        """
        url = utils.urljoin(GroupType.base_path, self.id, 'group_specs')
        microversion = self._get_microversion(session)
        response = session.get(url, microversion=microversion)
        exceptions.raise_from_response(response)
        specs = response.json().get('group_specs', {})
        self._update(group_specs=specs)
        return self

    def create_group_specs(self, session, specs):
        """Creates group specs for the group type.

        This will override whatever specs are already present on the group
        type.

        :param session: The session to use for making this request.
        :param specs: A dict of group specs to set on the group type.
        :returns: An updated version of this object.
        """
        url = utils.urljoin(GroupType.base_path, self.id, 'group_specs')
        microversion = self._get_microversion(session)
        response = session.post(
            url,
            json={'group_specs': specs},
            microversion=microversion,
        )
        exceptions.raise_from_response(response)
        specs = response.json().get('group_specs', {})
        self._update(group_specs=specs)
        return self

    def get_group_specs_property(self, session, prop):
        """Retrieve a group spec property of the group type.

        :param session: The session to use for making this request.
        :param prop: The name of the group spec property to update.
        :returns: The value of the group spec property.
        """
        url = utils.urljoin(GroupType.base_path, self.id, 'group_specs', prop)
        microversion = self._get_microversion(session)
        response = session.get(url, microversion=microversion)
        exceptions.raise_from_response(response)
        val = response.json().get(prop)
        return val

    def update_group_specs_property(self, session, prop, val):
        """Update a group spec property of the group type.

        :param session: The session to use for making this request.
        :param prop: The name of the group spec property to update.
        :param val: The value to set for the group spec property.
        :returns: The updated value of the group spec property.
        """
        url = utils.urljoin(GroupType.base_path, self.id, 'group_specs', prop)
        microversion = self._get_microversion(session)
        response = session.put(
            url, json={prop: val}, microversion=microversion
        )
        exceptions.raise_from_response(response)
        val = response.json().get(prop)
        return val

    def delete_group_specs_property(self, session, prop):
        """Delete a group spec property from the group type.

        :param session: The session to use for making this request.
        :param prop: The name of the group spec property to delete.
        :returns: None
        """
        url = utils.urljoin(GroupType.base_path, self.id, 'group_specs', prop)
        microversion = self._get_microversion(session)
        response = session.delete(url, microversion=microversion)
        exceptions.raise_from_response(response)
