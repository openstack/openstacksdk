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

from openstack import resource
from openstack import utils


class Instance(resource.Resource):
    resource_key = 'instance'
    resources_key = 'instances'
    base_path = '/instances'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The flavor of the instance
    flavor = resource.Body('flavor')
    #: Links associated with the instance
    links = resource.Body('links')
    #: The name of the instance
    name = resource.Body('name')
    #: The status of the instance
    status = resource.Body('status')
    #: The size of the volume
    volume = resource.Body('volume')
    #: A dictionary of datastore details, often including 'type' and 'version'
    #: keys
    datastore = resource.Body('datastore', type=dict)
    #: The ID of this instance
    id = resource.Body('id')
    #: The region this instance resides in
    region = resource.Body('region')
    #: The name of the host
    hostname = resource.Body('hostname')
    #: The timestamp when this instance was created
    created_at = resource.Body('created')
    #: The timestamp when this instance was updated
    updated_at = resource.Body('updated')

    def enable_root_user(self, session):
        """Enable login for the root user.

        This operation enables login from any host for the root user
        and provides the user with a generated root password.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :returns: A dictionary with keys ``name`` and ``password`` specifying
            the login credentials.
        """
        url = utils.urljoin(self.base_path, self.id, 'root')
        resp = session.post(
            url,
        )
        return resp.json()['user']

    def is_root_enabled(self, session):
        """Determine if root is enabled on an instance.

        Determine if root is enabled on this particular instance.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :returns: ``True`` if root user is enabled for a specified database
            instance or ``False`` otherwise.
        """
        url = utils.urljoin(self.base_path, self.id, 'root')
        resp = session.get(
            url,
        )
        return resp.json()['rootEnabled']

    def restart(self, session):
        """Restart the database instance

        :returns: ``None``
        """
        body = {'restart': None}
        url = utils.urljoin(self.base_path, self.id, 'action')
        session.post(url, json=body)

    def resize(self, session, flavor_reference):
        """Resize the database instance

        :returns: ``None``
        """
        body = {'resize': {'flavorRef': flavor_reference}}
        url = utils.urljoin(self.base_path, self.id, 'action')
        session.post(url, json=body)

    def resize_volume(self, session, volume_size):
        """Resize the volume attached to the instance

        :returns: ``None``
        """
        body = {'resize': {'volume': volume_size}}
        url = utils.urljoin(self.base_path, self.id, 'action')
        session.post(url, json=body)
