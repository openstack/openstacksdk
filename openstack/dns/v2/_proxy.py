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

from openstack.dns.v2 import name_server as _name_server
from openstack.dns.v2 import ptr as _ptr
from openstack.dns.v2 import recordset as _recordset
from openstack.dns.v2 import router as _router
from openstack.dns.v2 import zone as _zone
from openstack.exceptions import InvalidRequest
from openstack import proxy2


class Proxy(proxy2.BaseProxy):
    def zones(self, **query):
        """Retrieve a generator of zones

        :param dict query: Optional query parameters to be sent to limit the
                      resources being returned.
            * ``zone_type``: Zone Type
            * ``marker``:  pagination marker
            * ``limit``: pagination limit

        :returns: A generator of zone (:class:`~openstack.dns.v2.zone.Zone`)
                  instances
        """
        return self._list(_zone.Zone, paginated=True, **query)

    def create_zone(self, **attrs):
        """Create a new zone from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.dns.v2.zone.Zone`,
                           comprised of the properties on the Zone class.
        :returns: The results of zone creation
        :rtype: :class:`~openstack.dns.v2.zone.Zone`
        """
        return self._create(_zone.Zone, prepend_key=False, **attrs)

    def get_zone(self, zone):
        """Get a zone

        :param zone: The value can be the ID of a zone
             or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :returns: Zone instance
        :rtype: :class:`~openstack.dns.v2.zone.Zone`
        """
        return self._get(_zone.Zone, zone)

    def delete_zone(self, zone, ignore_missing=True):
        """Delete a zone

        :param zone: The value can be the ID of a zone
             or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the zone does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent zone.

        :returns: Zone been deleted
        :rtype: :class:`~openstack.dns.v2.zone.Zone`
        """
        return self._delete(_zone.Zone, zone, ignore_missing=ignore_missing)

    def find_zone(self, name_or_id, ignore_missing=True):
        """Find a single zone

        :param name_or_id: The name or ID of a zone
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the zone does not exist.
            When set to ``True``, no exception will be set when attempting
            to delete a nonexistent zone.

        :returns: ``None``
        """
        return self._find(_zone.Zone, name_or_id,
                          ignore_missing=ignore_missing)

    def nameservers(self, zone):
        """list nameservers of Zone

        :param zone: The value can be the ID of a zone
             or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :returns: list of `~openstack.dns.v2.name_server.NameServer` instance
        :rtype: :class:`~openstack.dns.v2.name_server.NameServer`
        """
        instance = self._get_resource(_zone.Zone, zone)
        return self._list(_name_server.NameServer, paginated=False,
                          zone_id=instance.id)

    def add_router_to_zone(self, zone, **router):
        """Add router(VPC) to zone

        :param zone: The value can be the ID of a zone
             or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :returns: list of `~openstack.dns.v2.name_server.NameServer` instance
        :rtype: :class:`~openstack.dns.v2.name_server.NameServer`
        """
        zone = self._get_resource(_zone.Zone, zone)
        router.update({'zone_id': zone.id})
        return self._create(_router.AssociateRouter, **router)

    def remove_router_from_zone(self, zone, **router):
        """Add router(VPC) to zone

        :param zone: The value can be the ID of a zone
             or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :returns: list of `~openstack.dns.v2.name_server.NameServer` instance
        :rtype: :class:`~openstack.dns.v2.name_server.NameServer`
        """
        zone = self._get_resource(_zone.Zone, zone)
        router.update({'zone_id': zone.id})
        return self._create(_router.DisassociateRouter, **router)

    def create_recordset(self, zone, **attrs):
        """Create a new recordset of zone

         :param zone: The value can be the ID of a zone
             or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.dns.v2.recordset.Recordset`,
                           comprised of the properties on the Recordset class.
        :returns: The results of zone creation
        :rtype: :class:`~openstack.dns.v2.recordset.Recordset`
        """
        zone = self._get_resource(_zone.Zone, zone)
        attrs.update({'zone_id': zone.id})
        return self._create(_recordset.Recordset, prepend_key=False, **attrs)

    def get_recordset(self, zone, recordset):
        """Get a recordset

        :param zone: The value can be the ID of a zone
             or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :param recordset: The value can be the ID of a recordset
             or a :class:`~openstack.dns.v2.recordset.Recordset` instance.
        :returns: Recordset instance
        :rtype: :class:`~openstack.dns.v2.recordset.Recordset`
        """
        zone = self._get_resource(_zone.Zone, zone)
        recordset = self._get_resource(_recordset.Recordset, recordset,
                                       zone_id=zone.id)
        return self._get(_recordset.Recordset, recordset)

    def recordsets(self, zone, **query):
        """Retrieve a generator of recordsets which belongs to `zone`

        :param zone: The value can be the ID of a zone
             or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :param dict query: Optional query parameters to be sent to limit the
                      resources being returned.
            * ``marker``:  pagination marker
            * ``limit``: pagination limit

        :returns: A generator of zone (:class:`~openstack.dns.v2.zone.Zone`)
                  instances
        """
        zone = self._get_resource(_zone.Zone, zone)
        query.update({'zone_id': zone.id})
        return self._list(_recordset.Recordset, paginated=True, **query)

    def delete_recordset(self, zone, recordset, ignore_missing=True):
        """Delete a zone

        :param zone: The value can be the ID of a zone
             or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :param recordset: The value can be the ID of a recordset
             or a :class:`~openstack.dns.v2.recordset.Recordset` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the zone does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent zone.

        :returns: Recordset instance been deleted
        :rtype: :class:`~openstack.dns.v2.recordset.Recordset`
        """
        zone = self._get_resource(_zone.Zone, zone)
        recordset = self._get_resource(_recordset.Recordset, recordset,
                                       zone_id=zone.id)
        return self._delete(_recordset.Recordset, recordset,
                            ignore_missing=ignore_missing)

    def all_recordsets(self, **query):
        """Retrieve a generator of recordsets which belongs to `zone`

        :param dict query: Optional query parameters to be sent to limit the
                      resources being returned.
            * ``marker``:  pagination marker
            * ``limit``: pagination limit

        :returns: A generator of zone (:class:`~openstack.dns.v2.zone.Zone`)
                  instances
        """
        return self._list(_recordset.Recordsets, paginated=True, **query)

    def create_ptr(self, **attrs):
        """Create a new ptr of zone

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.dns.v2.ptr.PTR`,
                           comprised of the properties on the PTR class.
        :returns: The results of zone creation
        :rtype: :class:`~openstack.dns.v2.ptr.PTR`
        """
        if 'region' not in attrs:
            raise InvalidRequest('Attribute `region` is required')
        if 'floating_ip_id' not in attrs:
            raise InvalidRequest('Attribute `floating_ip_id` is required')
        # concat `region:floating_ip_id` as id
        attrs.update({'id': attrs['region'] + ':' + attrs['floating_ip_id']})
        return self._update(_ptr.PTR, prepend_key=False, **attrs)

    def get_ptr(self, region, floating_ip_id):
        """Get a ptr

        :param region: project region
        :param floating_ip_id: the PTR floating ip id
        :returns: PTR instance
        :rtype: :class:`~openstack.dns.v2.ptr.PTR`
        """
        # concat `region:floating_ip_id` as id
        ptr_id = region + ':' + floating_ip_id
        return self._get(_ptr.PTR, ptr_id)

    def ptrs(self, **query):
        """Retrieve a generator of ptrs which belongs to `zone`

        :param dict query: Optional query parameters to be sent to limit the
                      resources being returned.
            * ``marker``:  pagination marker
            * ``limit``: pagination limit
        :returns: A generator of PTR (:class:`~openstack.dns.v2.ptr.PTR`)
                  instances
        """
        return self._list(_ptr.PTR, paginated=True, **query)

    def restore_ptr(self, region, floating_ip_id):
        """Restore PTR record

        :param region: project region
        :param floating_ip_id: floating ip id
        :returns: PTR instance been deleted
        :rtype: :class:`~openstack.dns.v2.ptr.PTR`
        """
        # concat `region:floating_ip_id` as id
        ptr_id = region + ':' + floating_ip_id
        return self._update(_ptr.PTR,
                            ptr_id,
                            prepend_key=False,
                            has_body=False,
                            ptrdname=None)
