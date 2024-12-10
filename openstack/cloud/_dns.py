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

from openstack.cloud import _utils
from openstack.cloud import openstackcloud
from openstack import exceptions
from openstack import resource


class DnsCloudMixin(openstackcloud._OpenStackCloudMixin):
    def list_zones(self, filters=None):
        """List all available zones.

        :returns: A list of zones dicts.

        """
        if not filters:
            filters = {}
        return list(self.dns.zones(allow_unknown_params=True, **filters))

    def get_zone(self, name_or_id, filters=None):
        """Get a zone by name or ID.

        :param name_or_id: Name or ID of the zone
        :param filters:
            A dictionary of meta data to use for further filtering

        :returns:  A zone dict or None if no matching zone is found.

        """
        if not filters:
            filters = {}
        return self.dns.find_zone(
            name_or_id=name_or_id, ignore_missing=True, **filters
        )

    def search_zones(self, name_or_id=None, filters=None):
        zones = self.list_zones(filters)
        return _utils._filter_list(zones, name_or_id, filters)

    def create_zone(
        self,
        name,
        zone_type=None,
        email=None,
        description=None,
        ttl=None,
        masters=None,
    ):
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
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """

        # We capitalize in case the user passes time in lowercase, as
        # designate call expects PRIMARY/SECONDARY
        if zone_type is not None:
            zone_type = zone_type.upper()
            if zone_type not in ('PRIMARY', 'SECONDARY'):
                raise exceptions.SDKException(
                    f"Invalid type {zone_type}, valid choices are PRIMARY or SECONDARY"
                )

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

        try:
            return self.dns.create_zone(**zone)
        except exceptions.SDKException:
            raise exceptions.SDKException(f"Unable to create zone {name}")

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
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        zone = self.get_zone(name_or_id)
        if not zone:
            raise exceptions.SDKException(f"Zone {name_or_id} not found.")

        return self.dns.update_zone(zone['id'], **kwargs)

    def delete_zone(self, name_or_id):
        """Delete a zone.

        :param name_or_id: Name or ID of the zone being deleted.

        :returns: True if delete succeeded, False otherwise.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """

        zone = self.dns.find_zone(name_or_id, ignore_missing=True)
        if not zone:
            self.log.debug("Zone %s not found for deleting", name_or_id)
            return False

        self.dns.delete_zone(zone)

        return True

    def list_recordsets(self, zone):
        """List all available recordsets.

        :param zone: Name, ID or :class:`openstack.dns.v2.zone.Zone` instance
            of the zone managing the recordset.

        :returns: A list of recordsets.

        """
        if isinstance(zone, resource.Resource):
            zone_obj = zone
        else:
            zone_obj = self.get_zone(zone)
        if zone_obj is None:
            raise exceptions.SDKException(f"Zone {zone} not found.")
        return list(self.dns.recordsets(zone_obj))

    def get_recordset(self, zone, name_or_id):
        """Get a recordset by name or ID.

        :param zone: Name, ID or :class:`openstack.dns.v2.zone.Zone` instance
            of the zone managing the recordset.
        :param name_or_id: Name or ID of the recordset

        :returns:  A recordset dict or None if no matching recordset is
            found.

        """
        if isinstance(zone, resource.Resource):
            zone_obj = zone
        else:
            zone_obj = self.get_zone(zone)
        if not zone_obj:
            raise exceptions.SDKException(f"Zone {name_or_id} not found.")
        return self.dns.find_recordset(
            zone=zone_obj, name_or_id=name_or_id, ignore_missing=True
        )

    def search_recordsets(self, zone, name_or_id=None, filters=None):
        recordsets = self.list_recordsets(zone=zone)
        return _utils._filter_list(recordsets, name_or_id, filters)

    def create_recordset(
        self, zone, name, recordset_type, records, description=None, ttl=None
    ):
        """Create a recordset.

        :param zone: Name, ID or :class:`openstack.dns.v2.zone.Zone` instance
            of the zone managing the recordset.
        :param name: Name of the recordset
        :param recordset_type: Type of the recordset
        :param records: List of the recordset definitions
        :param description: Description of the recordset
        :param ttl: TTL value of the recordset

        :returns: a dict representing the created recordset.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        if isinstance(zone, resource.Resource):
            zone_obj = zone
        else:
            zone_obj = self.get_zone(zone)
        if not zone_obj:
            raise exceptions.SDKException(f"Zone {zone} not found.")

        # We capitalize the type in case the user sends in lowercase
        recordset_type = recordset_type.upper()

        body = {'name': name, 'type': recordset_type, 'records': records}

        if description:
            body['description'] = description

        if ttl:
            body['ttl'] = ttl

        return self.dns.create_recordset(zone=zone_obj, **body)

    @_utils.valid_kwargs('description', 'ttl', 'records')
    def update_recordset(self, zone, name_or_id, **kwargs):
        """Update a recordset.

        :param zone: Name, ID or :class:`openstack.dns.v2.zone.Zone` instance
            of the zone managing the recordset.
        :param name_or_id: Name or ID of the recordset being updated.
        :param records: List of the recordset definitions
        :param description: Description of the recordset
        :param ttl: TTL (Time to live) value in seconds of the recordset

        :returns: a dict representing the updated recordset.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """

        rs = self.get_recordset(zone, name_or_id)
        if not rs:
            raise exceptions.SDKException(f"Recordset {name_or_id} not found.")

        rs = self.dns.update_recordset(recordset=rs, **kwargs)

        return rs

    def delete_recordset(self, zone, name_or_id):
        """Delete a recordset.

        :param zone: Name, ID or :class:`openstack.dns.v2.zone.Zone` instance
            of the zone managing the recordset.
        :param name_or_id: Name or ID of the recordset being deleted.

        :returns: True if delete succeeded, False otherwise.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """

        recordset = self.get_recordset(zone, name_or_id)
        if not recordset:
            self.log.debug("Recordset %s not found for deleting", name_or_id)
            return False

        self.dns.delete_recordset(recordset, ignore_missing=False)

        return True
