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
from openstack import proxy
from openstack.dns.v2 import recordset as _rs
from openstack.dns.v2 import zone as _zone
from openstack.dns.v2 import zone_import as _zone_import
from openstack.dns.v2 import zone_export as _zone_export
from openstack.dns.v2 import zone_transfer as _zone_transfer
from openstack.dns.v2 import floating_ip as _fip


class Proxy(proxy.Proxy):

    # ======== Zones ========
    def zones(self, **query):
        """Retrieve a generator of zones

        :param dict query: Optional query parameters to be sent to limit the
            resources being returned.

            * `name`: Zone Name field.
            * `type`: Zone Type field.
            * `email`: Zone email field.
            * `status`: Status of the zone.
            * `ttl`: TTL field filter.abs
            * `description`: Zone description field filter.

        :returns: A generator of zone
            :class:`~openstack.dns.v2.zone.Zone` instances.
        """
        return self._list(_zone.Zone, **query)

    def create_zone(self, **attrs):
        """Create a new zone from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.dns.v2.zone.Zone`,
            comprised of the properties on the Zone class.
        :returns: The results of zone creation.
        :rtype: :class:`~openstack.dns.v2.zone.Zone`
        """
        return self._create(_zone.Zone, prepend_key=False, **attrs)

    def get_zone(self, zone):
        """Get a zone

        :param zone: The value can be the ID of a zone
             or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :returns: Zone instance.
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

    def update_zone(self, zone, **attrs):
        """Update zone attributes

        :param zone: The id or an instance of
            :class:`~openstack.dns.v2.zone.Zone`.
        :param dict attrs: attributes for update on
            :class:`~openstack.dns.v2.zone.Zone`.

        :rtype: :class:`~openstack.dns.v2.zone.Zone`
        """
        return self._update(_zone.Zone, zone, **attrs)

    def find_zone(self, name_or_id, ignore_missing=True, **attrs):
        """Find a single zone

        :param name_or_id: The name or ID of a zone
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the zone does not exist.
            When set to ``True``, no exception will be set when attempting
            to delete a nonexistent zone.

        :returns: :class:`~openstack.dns.v2.zone.Zone`
        """
        return self._find(_zone.Zone, name_or_id,
                          ignore_missing=ignore_missing)

    def abandon_zone(self, zone, **attrs):
        """Abandon Zone

        :param zone: The value can be the ID of a zone to be abandoned
             or a :class:`~openstack.dns.v2.zone_export.ZoneExport` instance.

        :returns: None
        """
        zone = self._get_resource(_zone.Zone, zone)

        return zone.abandon(self)

    def xfr_zone(self, zone, **attrs):
        """Trigger update of secondary Zone

        :param zone: The value can be the ID of a zone to be abandoned
             or a :class:`~openstack.dns.v2.zone_export.ZoneExport` instance.

        :returns: None
        """
        zone = self._get_resource(_zone.Zone, zone)
        return zone.xfr(self)

    # ======== Recordsets ========
    def recordsets(self, zone=None, **query):
        """Retrieve a generator of recordsets

        :param zone: The optional value can be the ID of a zone
             or a :class:`~openstack.dns.v2.zone.Zone` instance. If it is not
             given all recordsets for all zones of the tenant would be
             retrieved
        :param dict query: Optional query parameters to be sent to limit the
            resources being returned.

            * `name`: Recordset Name field.
            * `type`: Type field.
            * `status`: Status of the recordset.
            * `ttl`: TTL field filter.
            * `description`: Recordset description field filter.

        :returns: A generator of zone
            (:class:`~openstack.dns.v2.recordset.Recordset`) instances
        """
        base_path = None
        if not zone:
            base_path = '/recordsets'
        else:
            zone = self._get_resource(_zone.Zone, zone)
            query.update({'zone_id': zone.id})
        return self._list(_rs.Recordset, base_path=base_path, **query)

    def create_recordset(self, zone, **attrs):
        """Create a new recordset in the zone

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
        return self._create(_rs.Recordset, prepend_key=False, **attrs)

    def update_recordset(self, recordset, **attrs):
        """Update Recordset attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.dns.v2.recordset.Recordset`,
            comprised of the properties on the Recordset class.
        :returns: The results of zone creation
        :rtype: :class:`~openstack.dns.v2.recordset.Recordset`
        """
        return self._update(_rs.Recordset, recordset, **attrs)

    def get_recordset(self, recordset, zone):
        """Get a recordset

        :param zone: The value can be the ID of a zone
             or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :param recordset: The value can be the ID of a recordset
             or a :class:`~openstack.dns.v2.recordset.Recordset` instance.
        :returns: Recordset instance
        :rtype: :class:`~openstack.dns.v2.recordset.Recordset`
        """
        zone = self._get_resource(_zone.Zone, zone)
        return self._get(_rs.Recordset, recordset, zone_id=zone.id)

    def delete_recordset(self, recordset, zone=None, ignore_missing=True):
        """Delete a zone

        :param recordset: The value can be the ID of a recordset
             or a :class:`~openstack.dns.v2.recordset.Recordset`
             instance.
        :param zone: The value can be the ID of a zone
             or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the zone does not exist. When set to ``True``, no exception will
            be set when attempting to delete a nonexistent zone.

        :returns: Recordset instance been deleted
        :rtype: :class:`~openstack.dns.v2.recordset.Recordset`
        """
        if zone:
            zone = self._get_resource(_zone.Zone, zone)
            recordset = self._get(
                _rs.Recordset, recordset, zone_id=zone.id)
        return self._delete(_rs.Recordset, recordset,
                            ignore_missing=ignore_missing)

    def find_recordset(self, zone, name_or_id, ignore_missing=True, **attrs):
        """Find a single recordset

        :param zone: The value can be the ID of a zone
             or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :param name_or_id: The name or ID of a zone
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the zone does not exist.
            When set to ``True``, no exception will be set when attempting
            to delete a nonexistent zone.

        :returns: :class:`~openstack.dns.v2.recordset.Recordset`
        """
        zone = self._get_resource(_zone.Zone, zone)
        return self._find(_rs.Recordset, name_or_id,
                          ignore_missing=ignore_missing, zone_id=zone.id,
                          **attrs)

    # ======== Zone Imports ========
    def zone_imports(self, **query):
        """Retrieve a generator of zone imports

        :param dict query: Optional query parameters to be sent to limit the
            resources being returned.

            * `zone_id`: Zone I field.
            * `message`: Message field.
            * `status`: Status of the zone import record.

        :returns: A generator of zone
            :class:`~openstack.dns.v2.zone_import.ZoneImport` instances.
        """
        return self._list(_zone_import.ZoneImport, **query)

    def create_zone_import(self, **attrs):
        """Create a new zone import from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.dns.v2.zone_import.ZoneImport`,
            comprised of the properties on the ZoneImport class.
        :returns: The results of zone creation.
        :rtype: :class:`~openstack.dns.v2.zone_import.ZoneImport`
        """
        return self._create(_zone_import.ZoneImport, prepend_key=False,
                            **attrs)

    def get_zone_import(self, zone_import):
        """Get a zone import record

        :param zone: The value can be the ID of a zone import
             or a :class:`~openstack.dns.v2.zone_import.ZoneImport` instance.
        :returns: ZoneImport instance.
        :rtype: :class:`~openstack.dns.v2.zone_import.ZoneImport`
        """
        return self._get(_zone_import.ZoneImport, zone_import)

    def delete_zone_import(self, zone_import, ignore_missing=True):
        """Delete a zone import

        :param zone_import: The value can be the ID of a zone import
             or a :class:`~openstack.dns.v2.zone_import.ZoneImport` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the zone does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent zone.

        :returns: None
        """
        return self._delete(_zone_import.ZoneImport, zone_import,
                            ignore_missing=ignore_missing)

    # ======== Zone Exports ========
    def zone_exports(self, **query):
        """Retrieve a generator of zone exports

        :param dict query: Optional query parameters to be sent to limit the
            resources being returned.

            * `zone_id`: Zone I field.
            * `message`: Message field.
            * `status`: Status of the zone import record.

        :returns: A generator of zone
            :class:`~openstack.dns.v2.zone_export.ZoneExport` instances.
        """
        return self._list(_zone_export.ZoneExport, **query)

    def create_zone_export(self, zone, **attrs):
        """Create a new zone export from attributes

        :param zone: The value can be the ID of a zone to be exported
             or a :class:`~openstack.dns.v2.zone_export.ZoneExport` instance.
        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.dns.v2.zone_export.ZoneExport`,
            comprised of the properties on the ZoneExport class.
        :returns: The results of zone creation.
        :rtype: :class:`~openstack.dns.v2.zone_export.ZoneExport`
        """
        zone = self._get_resource(_zone.Zone, zone)
        return self._create(_zone_export.ZoneExport,
                            base_path='/zones/%(zone_id)s/tasks/export',
                            prepend_key=False,
                            zone_id=zone.id,
                            **attrs)

    def get_zone_export(self, zone_export):
        """Get a zone export record

        :param zone: The value can be the ID of a zone import
             or a :class:`~openstack.dns.v2.zone_export.ZoneExport` instance.
        :returns: ZoneExport instance.
        :rtype: :class:`~openstack.dns.v2.zone_export.ZoneExport`
        """
        return self._get(_zone_export.ZoneExport, zone_export)

    def get_zone_export_text(self, zone_export):
        """Get a zone export record as text

        :param zone: The value can be the ID of a zone import
             or a :class:`~openstack.dns.v2.zone_export.ZoneExport` instance.
        :returns: ZoneExport instance.
        :rtype: :class:`~openstack.dns.v2.zone_export.ZoneExport`
        """
        return self._get(_zone_export.ZoneExport, zone_export,
                         base_path='/zones/tasks/export/%(id)s/export')

    def delete_zone_export(self, zone_export, ignore_missing=True):
        """Delete a zone export

        :param zone_export: The value can be the ID of a zone import
             or a :class:`~openstack.dns.v2.zone_export.ZoneExport` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the zone does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent zone.

        :returns: None
        """
        return self._delete(_zone_export.ZoneExport, zone_export,
                            ignore_missing=ignore_missing)

    # ======== FloatingIPs ========
    def floating_ips(self, **query):
        """Retrieve a generator of recordsets

        :param dict query: Optional query parameters to be sent to limit the
            resources being returned.

            * `name`: Recordset Name field.
            * `type`: Type field.
            * `status`: Status of the recordset.
            * `ttl`: TTL field filter.
            * `description`: Recordset description field filter.

        :returns: A generator of floatingips
            (:class:`~openstack.dns.v2.floating_ip.FloatingIP`) instances
        """
        return self._list(_fip.FloatingIP, **query)

    def get_floating_ip(self, floating_ip):
        """Get a Floating IP

        :param floating_ip: The value can be the ID of a floating ip
             or a :class:`~openstack.dns.v2.floating_ip.FloatingIP` instance.
             The ID is in format "region_name:floatingip_id"
        :returns: FloatingIP instance.
        :rtype: :class:`~openstack.dns.v2.floating_ip.FloatingIP`
        """
        return self._get(_fip.FloatingIP, floating_ip)

    def update_floating_ip(self, floating_ip, **attrs):
        """Update floating ip attributes

        :param floating_ip: The id or an instance of
            :class:`~openstack.dns.v2.fip.FloatingIP`.
        :param dict attrs: attributes for update on
            :class:`~openstack.dns.v2.fip.FloatingIP`.

        :rtype: :class:`~openstack.dns.v2.fip.FloatingIP`
        """
        return self._update(_fip.FloatingIP, floating_ip, **attrs)

    # ======== Zone Transfer ========
    def zone_transfer_requests(self, **query):
        """Retrieve a generator of zone transfer requests

        :param dict query: Optional query parameters to be sent to limit the
            resources being returned.

            * `status`: Status of the recordset.

        :returns: A generator of transfer requests
            (:class:`~openstack.dns.v2.zone_transfer.ZoneTransferRequest`)
            instances
        """
        return self._list(_zone_transfer.ZoneTransferRequest, **query)

    def get_zone_transfer_request(self, request):
        """Get a ZoneTransfer Request info

        :param request: The value can be the ID of a transfer request
             or a :class:`~openstack.dns.v2.zone_transfer.ZoneTransferRequest`
             instance.
        :returns: Zone transfer request instance.
        :rtype: :class:`~openstack.dns.v2.zone_transfer.ZoneTransferRequest`
        """
        return self._get(_zone_transfer.ZoneTransferRequest, request)

    def create_zone_transfer_request(self, zone, **attrs):
        """Create a new ZoneTransfer Request from attributes

        :param zone: The value can be the ID of a zone to be transferred
             or a :class:`~openstack.dns.v2.zone_export.ZoneExport` instance.
        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.dns.v2.zone_transfer.ZoneTransferRequest`,
            comprised of the properties on the ZoneTransferRequest class.
        :returns: The results of zone transfer request creation.
        :rtype: :class:`~openstack.dns.v2.zone_transfer.ZoneTransferRequest`
        """
        zone = self._get_resource(_zone.Zone, zone)
        return self._create(
            _zone_transfer.ZoneTransferRequest,
            base_path='/zones/%(zone_id)s/tasks/transfer_requests',
            prepend_key=False,
            zone_id=zone.id,
            **attrs)

    def update_zone_transfer_request(self, request, **attrs):
        """Update ZoneTransfer Request attributes

        :param floating_ip: The id or an instance of
            :class:`~openstack.dns.v2.zone_transfer.ZoneTransferRequest`.
        :param dict attrs: attributes for update on
            :class:`~openstack.dns.v2.zone_transfer.ZoneTransferRequest`.

        :rtype: :class:`~openstack.dns.v2.zone_transfer.ZoneTransferRequest`
        """
        return self._update(_zone_transfer.ZoneTransferRequest,
                            request, **attrs)

    def delete_zone_transfer_request(self, request, ignore_missing=True):
        """Delete a ZoneTransfer Request

        :param request: The value can be the ID of a zone transfer request
             or a :class:`~openstack.dns.v2.zone_transfer.ZoneTransferRequest`
             instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the zone does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent zone.

        :returns: None
        """
        return self._delete(_zone_transfer.ZoneTransferRequest, request,
                            ignore_missing=ignore_missing)

    def zone_transfer_accepts(self, **query):
        """Retrieve a generator of zone transfer accepts

        :param dict query: Optional query parameters to be sent to limit the
            resources being returned.

            * `status`: Status of the recordset.

        :returns: A generator of transfer accepts
            (:class:`~openstack.dns.v2.zone_transfer.ZoneTransferAccept`)
            instances
        """
        return self._list(_zone_transfer.ZoneTransferAccept, **query)

    def get_zone_transfer_accept(self, accept):
        """Get a ZoneTransfer Accept info

        :param request: The value can be the ID of a transfer accept
             or a :class:`~openstack.dns.v2.zone_transfer.ZoneTransferAccept`
             instance.
        :returns: Zone transfer request instance.
        :rtype: :class:`~openstack.dns.v2.zone_transfer.ZoneTransferAccept`
        """
        return self._get(_zone_transfer.ZoneTransferAccept, accept)

    def create_zone_transfer_accept(self, **attrs):
        """Create a new ZoneTransfer Accept from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.dns.v2.zone_transfer.ZoneTransferAccept`,
            comprised of the properties on the ZoneTransferAccept class.
        :returns: The results of zone transfer request creation.
        :rtype: :class:`~openstack.dns.v2.zone_transfer.ZoneTransferAccept`
        """
        return self._create(_zone_transfer.ZoneTransferAccept, **attrs)

    def _get_cleanup_dependencies(self):
        # DNS may depend on floating ip
        return {
            'dns': {
                'before': ['network']
            }
        }

    def _service_cleanup(self, dry_run=True, client_status_queue=False,
                         identified_resources=None,
                         filters=None, resource_evaluation_fn=None):
        pass
