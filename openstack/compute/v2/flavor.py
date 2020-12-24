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


class Flavor(resource.Resource):
    resource_key = 'flavor'
    resources_key = 'flavors'
    base_path = '/flavors'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_delete = True
    allow_list = True
    allow_commit = True

    _query_mapping = resource.QueryParameters(
        "sort_key", "sort_dir", "is_public",
        min_disk="minDisk",
        min_ram="minRam")

    # extra_specs introduced in 2.61
    _max_microversion = '2.61'

    # Properties
    #: Links pertaining to this flavor. This is a list of dictionaries,
    #: each including keys ``href`` and ``rel``.
    links = resource.Body('links')
    #: The name of this flavor.
    name = resource.Body('name')
    #: The description of the flavor.
    description = resource.Body('description')
    #: Size of the disk this flavor offers. *Type: int*
    disk = resource.Body('disk', type=int)
    #: ``True`` if this is a publicly visible flavor. ``False`` if this is
    #: a private image. *Type: bool*
    is_public = resource.Body('os-flavor-access:is_public', type=bool)
    #: The amount of RAM (in MB) this flavor offers. *Type: int*
    ram = resource.Body('ram', type=int)
    #: The number of virtual CPUs this flavor offers. *Type: int*
    vcpus = resource.Body('vcpus', type=int)
    #: Size of the swap partitions.
    swap = resource.Body('swap')
    #: Size of the ephemeral data disk attached to this server. *Type: int*
    ephemeral = resource.Body('OS-FLV-EXT-DATA:ephemeral', type=int)
    #: ``True`` if this flavor is disabled, ``False`` if not. *Type: bool*
    is_disabled = resource.Body('OS-FLV-DISABLED:disabled', type=bool)
    #: The bandwidth scaling factor this flavor receives on the network.
    rxtx_factor = resource.Body('rxtx_factor', type=float)
    # TODO(mordred) extra_specs can historically also come from
    #               OS-FLV-WITH-EXT-SPECS:extra_specs. Do we care?
    #: A dictionary of the flavor's extra-specs key-and-value pairs.
    extra_specs = resource.Body('extra_specs', type=dict, default={})

    @classmethod
    def list(cls, session, paginated=True, base_path='/flavors/detail',
             allow_unknown_params=False, **params):
        # Find will invoke list when name was passed. Since we want to return
        # flavor with details (same as direct get) we need to swap default here
        # and list with "/flavors" if no details explicitely requested
        if 'is_public' not in params or params['is_public'] is None:
            # is_public is ternary - None means give all flavors.
            # Force it to string to avoid requests skipping it.
            params['is_public'] = 'None'
        return super(Flavor, cls).list(
            session, paginated=paginated,
            base_path=base_path,
            allow_unknown_params=allow_unknown_params,
            **params)

    def _action(self, session, body, microversion=None):
        """Preform flavor actions given the message body."""
        url = utils.urljoin(Flavor.base_path, self.id, 'action')
        headers = {'Accept': ''}
        attrs = {}
        if microversion:
            # Do not reset microversion if it is set on a session level
            attrs['microversion'] = microversion
        response = session.post(
            url, json=body, headers=headers, **attrs)
        exceptions.raise_from_response(response)
        return response

    def add_tenant_access(self, session, tenant):
        """Adds flavor access to a tenant and flavor."""
        body = {'addTenantAccess': {'tenant': tenant}}
        self._action(session, body)

    def remove_tenant_access(self, session, tenant):
        """Removes flavor access to a tenant and flavor."""
        body = {'removeTenantAccess': {'tenant': tenant}}
        self._action(session, body)

    def get_access(self, session):
        """Lists tenants who have access to a private flavor

        By default, only administrators can manage private flavor access. A
        private flavor has is_public set to false while a public flavor has
        is_public set to true.

        :return: List of dicts with flavor_id and tenant_id attributes
        """
        url = utils.urljoin(Flavor.base_path, self.id, 'os-flavor-access')
        response = session.get(url)
        exceptions.raise_from_response(response)
        return response.json().get('flavor_access', [])

    def fetch_extra_specs(self, session):
        """Fetch extra_specs of the flavor

        Starting with 2.61 extra_specs are returned with the flavor details,
        before that a separate call is required.
        """
        url = utils.urljoin(Flavor.base_path, self.id, 'os-extra_specs')
        microversion = self._get_microversion_for(session, 'fetch')
        response = session.get(url, microversion=microversion)
        exceptions.raise_from_response(response)
        specs = response.json().get('extra_specs', {})
        self._update(extra_specs=specs)
        return self

    def create_extra_specs(self, session, specs):
        """Creates extra specs for a flavor"""
        url = utils.urljoin(Flavor.base_path, self.id, 'os-extra_specs')
        microversion = self._get_microversion_for(session, 'create')
        response = session.post(
            url,
            json={'extra_specs': specs},
            microversion=microversion)
        exceptions.raise_from_response(response)
        specs = response.json().get('extra_specs', {})
        self._update(extra_specs=specs)
        return self

    def get_extra_specs_property(self, session, prop):
        """Get individual extra_spec property"""
        url = utils.urljoin(Flavor.base_path, self.id,
                            'os-extra_specs', prop)
        microversion = self._get_microversion_for(session, 'fetch')
        response = session.get(url, microversion=microversion)
        exceptions.raise_from_response(response)
        val = response.json().get(prop)
        return val

    def update_extra_specs_property(self, session, prop, val):
        """Update An Extra Spec For A Flavor"""
        url = utils.urljoin(Flavor.base_path, self.id,
                            'os-extra_specs', prop)
        microversion = self._get_microversion_for(session, 'commit')
        response = session.put(
            url,
            json={prop: val},
            microversion=microversion)
        exceptions.raise_from_response(response)
        val = response.json().get(prop)
        return val

    def delete_extra_specs_property(self, session, prop):
        """Delete An Extra Spec For A Flavor"""
        url = utils.urljoin(Flavor.base_path, self.id,
                            'os-extra_specs', prop)
        microversion = self._get_microversion_for(session, 'delete')
        response = session.delete(
            url,
            microversion=microversion)
        exceptions.raise_from_response(response)


FlavorDetail = Flavor
