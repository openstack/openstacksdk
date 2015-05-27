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

from openstack.database import database_service
from openstack import resource
from openstack import utils


class Instance(resource.Resource):
    resource_key = 'instance'
    resources_key = 'instances'
    base_path = '/instances'
    service = database_service.DatabaseService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The flavor of the instance
    flavor = resource.prop('flavor')
    #: Links associated with the instance
    links = resource.prop('links')
    #: The name of the instance
    name = resource.prop('name')
    #: The status of the instance
    status = resource.prop('status')
    #: The size of the volume
    volume = resource.prop('volume')

    def enable_root_user(self, session):
        """Enable login for the root user.

        This operation enables login from any host for the root user
        and provides the user with a generated root password.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :returns: A dictionary with keys ``name`` and ``password`` specifying
            the login credentials.
        """
        url = utils.urljoin(self.base_path, self.id, 'root')
        resp = session.post(url, endpoint_filter=self.service)
        return resp.json()['user']

    def is_root_enabled(self, session):
        """Determine if root is enabled on an instance.

        Determine if root is enabled on this particular instance.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :returns: ``True`` if root user is enabled for a specified database
            instance or ``False`` otherwise.
        """
        url = utils.urljoin(self.base_path, self.id, 'root')
        resp = session.get(url, endpoint_filter=self.service)
        return resp.json()['rootEnabled']

    def restart(self, session):
        """Restart the database instance

        :returns: ``None``
        """
        body = {'restart': {}}
        url = utils.urljoin(self.base_path, self.id, 'action')
        session.post(url, endpoint_filter=self.service, json=body)

    def resize(self, session, flavor_reference):
        """Resize the database instance

        :returns: ``None``
        """
        body = {'resize': {'flavorRef': flavor_reference}}
        url = utils.urljoin(self.base_path, self.id, 'action')
        session.post(url, endpoint_filter=self.service, json=body)

    def resize_volume(self, session, volume_size):
        """Resize the volume attached to the instance

        :returns: ``None``
        """
        body = {'resize': {'volume': volume_size}}
        url = utils.urljoin(self.base_path, self.id, 'action')
        session.post(url, endpoint_filter=self.service, json=body)
