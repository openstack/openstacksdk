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

from openstack.cloud import exc
from openstack.cloud import _normalize
from openstack.cloud import _utils


class DnsCloudMixin(_normalize.Normalizer):

    @property
    def _dns_client(self):
        if 'dns' not in self._raw_clients:
            dns_client = self._get_versioned_client(
                'dns', min_version=2, max_version='2.latest')
            self._raw_clients['dns'] = dns_client
        return self._raw_clients['dns']

    def list_zones(self):
        """List all available zones.

        :returns: A list of zones dicts.

        """
        data = self._dns_client.get(
            "/zones",
            error_message="Error fetching zones list")
        return self._get_and_munchify('zones', data)

    def get_zone(self, name_or_id, filters=None):
        """Get a zone by name or ID.

        :param name_or_id: Name or ID of the zone
        :param filters:
            A dictionary of meta data to use for further filtering
            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns:  A zone dict or None if no matching zone is found.

        """
        return _utils._get_entity(self, 'zone', name_or_id, filters)

    def search_zones(self, name_or_id=None, filters=None):
        zones = self.list_zones()
        return _utils._filter_list(zones, name_or_id, filters)

    def create_zone(self, name, zone_type=None, email=None, description=None,
                    ttl=None, masters=None):
        """Create a new zone.

        :param name: Name of the zone being created.
        :param zone_type: Type of the zone (primary/secondary)
        :param email: Email of the zone owner (only
                      applies if zone_type is primary)
        :param description: Description of the zone
        :param ttl: TTL (Time to live) value in seconds
        :param masters: Master nameservers (only applies
                        if zone_type is secondary)

        :returns: a dict representing the created zone.

        :raises: OpenStackCloudException on operation error.
        """

        # We capitalize in case the user passes time in lowercase, as
        # designate call expects PRIMARY/SECONDARY
        if zone_type is not None:
            zone_type = zone_type.upper()
            if zone_type not in ('PRIMARY', 'SECONDARY'):
                raise exc.OpenStackCloudException(
                    "Invalid type %s, valid choices are PRIMARY or SECONDARY" %
                    zone_type)

        zone = {
            "name": name,
            "email": email,
            "description": description,
        }
        if ttl is not None:
            zone["ttl"] = ttl

        if zone_type is not None:
            zone["type"] = zone_type

        if masters is not None:
            zone["masters"] = masters

        data = self._dns_client.post(
            "/zones", json=zone,
            error_message="Unable to create zone {name}".format(name=name))
        return self._get_and_munchify(key=None, data=data)

    @_utils.valid_kwargs('email', 'description', 'ttl', 'masters')
    def update_zone(self, name_or_id, **kwargs):
        """Update a zone.

        :param name_or_id: Name or ID of the zone being updated.
        :param email: Email of the zone owner (only
                      applies if zone_type is primary)
        :param description: Description of the zone
        :param ttl: TTL (Time to live) value in seconds
        :param masters: Master nameservers (only applies
                        if zone_type is secondary)

        :returns: a dict representing the updated zone.

        :raises: OpenStackCloudException on operation error.
        """
        zone = self.get_zone(name_or_id)
        if not zone:
            raise exc.OpenStackCloudException(
                "Zone %s not found." % name_or_id)

        data = self._dns_client.patch(
            "/zones/{zone_id}".format(zone_id=zone['id']), json=kwargs,
            error_message="Error updating zone {0}".format(name_or_id))
        return self._get_and_munchify(key=None, data=data)

    def delete_zone(self, name_or_id):
        """Delete a zone.

        :param name_or_id: Name or ID of the zone being deleted.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """

        zone = self.get_zone(name_or_id)
        if zone is None:
            self.log.debug("Zone %s not found for deleting", name_or_id)
            return False

        return self._dns_client.delete(
            "/zones/{zone_id}".format(zone_id=zone['id']),
            error_message="Error deleting zone {0}".format(name_or_id))

        return True

    def list_recordsets(self, zone):
        """List all available recordsets.

        :param zone: Name or ID of the zone managing the recordset

        :returns: A list of recordsets.

        """
        zone_obj = self.get_zone(zone)
        if zone_obj is None:
            raise exc.OpenStackCloudException(
                "Zone %s not found." % zone)
        return self._dns_client.get(
            "/zones/{zone_id}/recordsets".format(zone_id=zone_obj['id']),
            error_message="Error fetching recordsets list")['recordsets']

    def get_recordset(self, zone, name_or_id):
        """Get a recordset by name or ID.

        :param zone: Name or ID of the zone managing the recordset
        :param name_or_id: Name or ID of the recordset

        :returns:  A recordset dict or None if no matching recordset is
            found.

        """
        zone_obj = self.get_zone(zone)
        if zone_obj is None:
            raise exc.OpenStackCloudException(
                "Zone %s not found." % zone)
        try:
            return self._dns_client.get(
                "/zones/{zone_id}/recordsets/{recordset_id}".format(
                    zone_id=zone_obj['id'], recordset_id=name_or_id),
                error_message="Error fetching recordset")
        except Exception:
            return None

    def search_recordsets(self, zone, name_or_id=None, filters=None):
        recordsets = self.list_recordsets(zone=zone)
        return _utils._filter_list(recordsets, name_or_id, filters)

    def create_recordset(self, zone, name, recordset_type, records,
                         description=None, ttl=None):
        """Create a recordset.

        :param zone: Name or ID of the zone managing the recordset
        :param name: Name of the recordset
        :param recordset_type: Type of the recordset
        :param records: List of the recordset definitions
        :param description: Description of the recordset
        :param ttl: TTL value of the recordset

        :returns: a dict representing the created recordset.

        :raises: OpenStackCloudException on operation error.

        """
        zone_obj = self.get_zone(zone)
        if zone_obj is None:
            raise exc.OpenStackCloudException(
                "Zone %s not found." % zone)

        # We capitalize the type in case the user sends in lowercase
        recordset_type = recordset_type.upper()

        body = {
            'name': name,
            'type': recordset_type,
            'records': records
        }

        if description:
            body['description'] = description

        if ttl:
            body['ttl'] = ttl

        return self._dns_client.post(
            "/zones/{zone_id}/recordsets".format(zone_id=zone_obj['id']),
            json=body,
            error_message="Error creating recordset {name}".format(name=name))

    @_utils.valid_kwargs('description', 'ttl', 'records')
    def update_recordset(self, zone, name_or_id, **kwargs):
        """Update a recordset.

        :param zone: Name or ID of the zone managing the recordset
        :param name_or_id: Name or ID of the recordset being updated.
        :param records: List of the recordset definitions
        :param description: Description of the recordset
        :param ttl: TTL (Time to live) value in seconds of the recordset

        :returns: a dict representing the updated recordset.

        :raises: OpenStackCloudException on operation error.
        """
        zone_obj = self.get_zone(zone)
        if zone_obj is None:
            raise exc.OpenStackCloudException(
                "Zone %s not found." % zone)

        recordset_obj = self.get_recordset(zone, name_or_id)
        if recordset_obj is None:
            raise exc.OpenStackCloudException(
                "Recordset %s not found." % name_or_id)

        new_recordset = self._dns_client.put(
            "/zones/{zone_id}/recordsets/{recordset_id}".format(
                zone_id=zone_obj['id'], recordset_id=name_or_id), json=kwargs,
            error_message="Error updating recordset {0}".format(name_or_id))

        return new_recordset

    def delete_recordset(self, zone, name_or_id):
        """Delete a recordset.

        :param zone: Name or ID of the zone managing the recordset.
        :param name_or_id: Name or ID of the recordset being deleted.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """

        zone_obj = self.get_zone(zone)
        if zone_obj is None:
            self.log.debug("Zone %s not found for deleting", zone)
            return False

        recordset = self.get_recordset(zone_obj['id'], name_or_id)
        if recordset is None:
            self.log.debug("Recordset %s not found for deleting", name_or_id)
            return False

        self._dns_client.delete(
            "/zones/{zone_id}/recordsets/{recordset_id}".format(
                zone_id=zone_obj['id'], recordset_id=name_or_id),
            error_message="Error deleting recordset {0}".format(name_or_id))

        return True
