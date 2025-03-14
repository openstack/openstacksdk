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

import typing as ty

from openstack.dns.v2 import floating_ip as _fip
from openstack.dns.v2 import limit as _limit
from openstack.dns.v2 import recordset as _rs
from openstack.dns.v2 import service_status as _svc_status
from openstack.dns.v2 import tsigkey as _tsigkey
from openstack.dns.v2 import zone as _zone
from openstack.dns.v2 import zone_export as _zone_export
from openstack.dns.v2 import zone_import as _zone_import
from openstack.dns.v2 import zone_nameserver as _zone_nameserver
from openstack.dns.v2 import zone_share as _zone_share
from openstack.dns.v2 import zone_transfer as _zone_transfer
from openstack import proxy
from openstack import resource


class Proxy(proxy.Proxy):
    _resource_registry = {
        "floating_ip": _fip.FloatingIP,
        "limits": _limit.Limit,
        "recordset": _rs.Recordset,
        "service_status": _svc_status.ServiceStatus,
        "zone": _zone.Zone,
        "tsigkey": _tsigkey.TSIGKey,
        "zone_export": _zone_export.ZoneExport,
        "zone_import": _zone_import.ZoneImport,
        "zone_nameserver": _zone_nameserver.ZoneNameserver,
        "zone_share": _zone_share.ZoneShare,
        "zone_transfer_request": _zone_transfer.ZoneTransferRequest,
    }

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
        if attrs.get('type') == "SECONDARY":
            attrs.pop('email', None)
            attrs.pop('ttl', None)
        return self._create(_zone.Zone, prepend_key=False, **attrs)

    def get_zone(self, zone):
        """Get a zone

        :param zone: The value can be the ID of a zone
            or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :returns: Zone instance.
        :rtype: :class:`~openstack.dns.v2.zone.Zone`
        """
        return self._get(_zone.Zone, zone)

    def delete_zone(self, zone, ignore_missing=True, delete_shares=False):
        """Delete a zone

        :param zone: The value can be the ID of a zone
            or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the zone does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent zone.
        :param bool delete_shares: When True, delete the zone shares along with
                                   the zone.

        :returns: Zone been deleted
        :rtype: :class:`~openstack.dns.v2.zone.Zone`
        """
        return self._delete(
            _zone.Zone,
            zone,
            ignore_missing=ignore_missing,
            delete_shares=delete_shares,
        )

    def update_zone(self, zone, **attrs):
        """Update zone attributes

        :param zone: The id or an instance of
            :class:`~openstack.dns.v2.zone.Zone`.
        :param dict attrs: attributes for update on
            :class:`~openstack.dns.v2.zone.Zone`.

        :rtype: :class:`~openstack.dns.v2.zone.Zone`
        """
        return self._update(_zone.Zone, zone, **attrs)

    def find_zone(self, name_or_id, ignore_missing=True):
        """Find a single zone

        :param name_or_id: The name or ID of a zone
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the zone does not exist.
            When set to ``True``, no exception will be set when attempting
            to delete a nonexistent zone.

        :returns: :class:`~openstack.dns.v2.zone.Zone`
        """
        return self._find(
            _zone.Zone, name_or_id, ignore_missing=ignore_missing
        )

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

    # ======== Zone nameservers ========
    def zone_nameservers(self, zone):
        """Retrieve a generator of nameservers for a zone

        :param zone: The value can be the ID of a zone or a
            :class:`~openstack.dns.v2.zone.Zone` instance.
        :return: A generator of
            :class:`~openstack.dns.v2.zone_nameserver.ZoneNameserver`
            instances.
        """
        zone_id = resource.Resource._get_id(zone)
        return self._list(
            _zone_nameserver.ZoneNameserver,
            zone_id=zone_id,
        )

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
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the zone does not exist. When set to ``True``, no exception will
            be set when attempting to delete a nonexistent zone.

        :returns: Recordset instance been deleted
        :rtype: :class:`~openstack.dns.v2.recordset.Recordset`
        """
        if zone:
            zone = self._get_resource(_zone.Zone, zone)
            recordset = self._get(_rs.Recordset, recordset, zone_id=zone.id)
        return self._delete(
            _rs.Recordset, recordset, ignore_missing=ignore_missing
        )

    def find_recordset(self, zone, name_or_id, ignore_missing=True, **query):
        """Find a single recordset

        :param zone: The value can be the ID of a zone
            or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :param name_or_id: The name or ID of a zone
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the zone does not exist.
            When set to ``True``, no exception will be set when attempting
            to delete a nonexistent zone.

        :returns: :class:`~openstack.dns.v2.recordset.Recordset`
        """
        zone = self._get_resource(_zone.Zone, zone)
        return self._find(
            _rs.Recordset,
            name_or_id,
            ignore_missing=ignore_missing,
            zone_id=zone.id,
            **query,
        )

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
        return self._create(
            _zone_import.ZoneImport, prepend_key=False, **attrs
        )

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
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the zone does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent zone.

        :returns: None
        """
        return self._delete(
            _zone_import.ZoneImport, zone_import, ignore_missing=ignore_missing
        )

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
        return self._create(
            _zone_export.ZoneExport,
            base_path='/zones/%(zone_id)s/tasks/export',
            prepend_key=False,
            zone_id=zone.id,
            **attrs,
        )

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
        return self._get(
            _zone_export.ZoneExport,
            zone_export,
            base_path='/zones/tasks/export/%(id)s/export',
        )

    def delete_zone_export(self, zone_export, ignore_missing=True):
        """Delete a zone export

        :param zone_export: The value can be the ID of a zone import
            or a :class:`~openstack.dns.v2.zone_export.ZoneExport` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the zone does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent zone.

        :returns: None
        """
        return self._delete(
            _zone_export.ZoneExport, zone_export, ignore_missing=ignore_missing
        )

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

    def unset_floating_ip(self, floating_ip):
        """Unset a Floating IP PTR record
        :param floating_ip: ID for the floatingip associated with the
            project.
        :returns: FloatingIP PTR record.
        :rtype: :class:`~openstack.dns.v2.fip.FloatipgIP`
        """
        # concat `region:floating_ip_id` as id
        attrs = {'ptrdname': None}
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
            **attrs,
        )

    def update_zone_transfer_request(self, request, **attrs):
        """Update ZoneTransfer Request attributes

        :param floating_ip: The id or an instance of
            :class:`~openstack.dns.v2.zone_transfer.ZoneTransferRequest`.
        :param dict attrs: attributes for update on
            :class:`~openstack.dns.v2.zone_transfer.ZoneTransferRequest`.

        :rtype: :class:`~openstack.dns.v2.zone_transfer.ZoneTransferRequest`
        """
        return self._update(
            _zone_transfer.ZoneTransferRequest, request, **attrs
        )

    def delete_zone_transfer_request(self, request, ignore_missing=True):
        """Delete a ZoneTransfer Request

        :param request: The value can be the ID of a zone transfer request
            or a :class:`~openstack.dns.v2.zone_transfer.ZoneTransferRequest`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the zone does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent zone.

        :returns: None
        """
        return self._delete(
            _zone_transfer.ZoneTransferRequest,
            request,
            ignore_missing=ignore_missing,
        )

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

    # ======== Zone Shares ========
    def zone_shares(self, zone, **query):
        """Retrieve a generator of zone shares

        :param zone: The zone ID or a
            :class:`~openstack.dns.v2.zone.Zone` instance
        :param dict query: Optional query parameters to be sent to limit the
                           resources being returned.

                           * `target_project_id`: The target project ID field.

        :returns: A generator of zone shares
            :class:`~openstack.dns.v2.zone_share.ZoneShare` instances.
        """
        zone_obj = self._get_resource(_zone.Zone, zone)
        return self._list(_zone_share.ZoneShare, zone_id=zone_obj.id, **query)

    def get_zone_share(self, zone, zone_share):
        """Get a zone share

        :param zone: The value can be the ID of a zone
            or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :param zone_share: The zone_share can be either the ID of the zone
            share or a :class:`~openstack.dns.v2.zone_share.ZoneShare` instance
            that the zone share belongs to.

        :returns: ZoneShare instance.
        :rtype: :class:`~openstack.dns.v2.zone_share.ZoneShare`
        """
        zone_obj = self._get_resource(_zone.Zone, zone)
        return self._get(
            _zone_share.ZoneShare, zone_share, zone_id=zone_obj.id
        )

    def find_zone_share(self, zone, zone_share_id, ignore_missing=True):
        """Find a single zone share

        :param zone: The value can be the ID of a zone
            or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :param zone_share_id: The zone share ID
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the zone share does not exist.
            When set to ``True``,  None will be returned when attempting to
            find a nonexistent zone share.

        :returns: :class:`~openstack.dns.v2.zone_share.ZoneShare`
        """
        zone_obj = self._get_resource(_zone.Zone, zone)
        return self._find(
            _zone_share.ZoneShare,
            zone_share_id,
            ignore_missing=ignore_missing,
            zone_id=zone_obj.id,
        )

    def create_zone_share(self, zone, **attrs):
        """Create a new zone share from attributes

        :param zone: The zone ID or a
            :class:`~openstack.dns.v2.zone.Zone` instance
        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.dns.v2.zone_share.ZoneShare`,
            comprised of the properties on the ZoneShare class.

        :returns: The results of zone share creation
        :rtype: :class:`~openstack.dns.v2.zone_share.ZoneShare`
        """
        zone_obj = self._get_resource(_zone.Zone, zone)
        return self._create(
            _zone_share.ZoneShare, zone_id=zone_obj.id, **attrs
        )

    def delete_zone_share(self, zone, zone_share, ignore_missing=True):
        """Delete a zone share

        :param zone: The zone ID or a
            :class:`~openstack.dns.v2.zone.Zone` instance
        :param zone_share: The zone_share can be either the ID of the zone
            share or a :class:`~openstack.dns.v2.zone_share.ZoneShare` instance
            that the zone share belongs to.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the zone share does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent zone share.

        :returns: ``None``
        """
        zone_obj = self._get_resource(_zone.Zone, zone)
        self._delete(
            _zone_share.ZoneShare,
            zone_share,
            ignore_missing=ignore_missing,
            zone_id=zone_obj.id,
        )

    # ======== Limits ========
    def limits(self, **query):
        """Retrieve a generator of limits

        :returns: A generator of limits
            (:class:`~openstack.dns.v2.limit.Limit`) instances
        """
        return self._list(_limit.Limit, **query)

    # ======== Service Statuses ========
    def service_statuses(self):
        """Retrieve a generator of service statuses

        :returns: A generator of service statuses
            :class:`~openstack.dns.v2.service_status.ServiceStatus` instances.
        """
        return self._list(_svc_status.ServiceStatus)

    def get_service_status(self, service):
        """Get a status of a service in the Designate system

        :param service: The value can be the ID of a service
            or a :class:`~openstack.dns.v2.service_status.ServiceStatus` instance.

        :returns: ServiceStatus instance.
        :rtype: :class:`~openstack.dns.v2.service_status.ServiceStatus`
        """
        return self._get(_svc_status.ServiceStatus, service)

    # ========== Utilities ==========
    def wait_for_status(
        self,
        res: resource.ResourceT,
        status: str,
        failures: ty.Optional[list[str]] = None,
        interval: ty.Union[int, float, None] = 2,
        wait: ty.Optional[int] = None,
        attribute: str = 'status',
        callback: ty.Optional[ty.Callable[[int], None]] = None,
    ) -> resource.ResourceT:
        """Wait for the resource to be in a particular status.

        :param session: The session to use for making this request.
        :param resource: The resource to wait on to reach the status. The
            resource must have a status attribute specified via ``attribute``.
        :param status: Desired status of the resource.
        :param failures: Statuses that would indicate the transition
            failed such as 'ERROR'. Defaults to ['ERROR'].
        :param interval: Number of seconds to wait between checks.
        :param wait: Maximum number of seconds to wait for transition.
            Set to ``None`` to wait forever.
        :param attribute: Name of the resource attribute that contains the
            status.
        :param callback: A callback function. This will be called with a single
            value, progress. This is API specific but is generally a percentage
            value from 0-100.

        :return: The updated resource.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if the
            transition to status failed to occur in ``wait`` seconds.
        :raises: :class:`~openstack.exceptions.ResourceFailure` if the resource
            transitioned to one of the states in ``failures``.
        :raises: :class:`~AttributeError` if the resource does not have a
            ``status`` attribute
        """
        return resource.wait_for_status(
            self, res, status, failures, interval, wait, attribute, callback
        )

    def wait_for_delete(
        self,
        res: resource.ResourceT,
        interval: int = 2,
        wait: int = 120,
        callback: ty.Optional[ty.Callable[[int], None]] = None,
    ) -> resource.ResourceT:
        """Wait for a resource to be deleted.

        :param res: The resource to wait on to be deleted.
        :param interval: Number of seconds to wait before to consecutive
            checks.
        :param wait: Maximum number of seconds to wait before the change.
        :param callback: A callback function. This will be called with a single
            value, progress, which is a percentage value from 0-100.

        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
            to delete failed to occur in the specified seconds.
        """
        return resource.wait_for_delete(self, res, interval, wait, callback)

    def _get_cleanup_dependencies(self):
        # DNS may depend on floating ip
        return {'dns': {'before': ['network']}}

    def _service_cleanup(
        self,
        dry_run=True,
        client_status_queue=False,
        identified_resources=None,
        filters=None,
        resource_evaluation_fn=None,
        skip_resources=None,
    ):
        if not self.should_skip_resource_cleanup("zone", skip_resources):
            # Delete all zones
            for obj in self.zones():
                self._service_cleanup_del_res(
                    self.delete_zone,
                    obj,
                    dry_run=dry_run,
                    client_status_queue=client_status_queue,
                    identified_resources=identified_resources,
                    filters=filters,
                    resource_evaluation_fn=resource_evaluation_fn,
                )

        if not self.should_skip_resource_cleanup(
            "floating_ip", skip_resources
        ):
            # Unset all floatingIPs
            # NOTE: FloatingIPs are not cleaned when filters are set
            for obj in self.floating_ips():
                self._service_cleanup_del_res(
                    self.unset_floating_ip,
                    obj,
                    dry_run=dry_run,
                    client_status_queue=client_status_queue,
                    identified_resources=identified_resources,
                    filters=filters,
                    resource_evaluation_fn=resource_evaluation_fn,
                )

    # ====== TSIG keys ======
    def tsigkeys(self, **query):
        """Retrieve a generator of zones

        :param dict query: Optional query parameters to be sent to limit the
            resources being returned.

        :returns: A generator of zone
            :class: `~openstack.dns.v2.tsigkey.TSIGKey` instances.
        """
        return self._list(_tsigkey.TSIGKey, **query)

    def create_tsigkey(self, **attrs):
        """Create a new tsigkey from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.dns.v2.tsigkey.Tsigkey`,
            comprised of the properties on the Tsigkey class.
        :returns: The results of zone creation.
        :rtype: :class:`~openstack.dns.v2.tsigkey.Tsigkey`
        """
        return self._create(_tsigkey.TSIGKey, prepend_key=False, **attrs)

    def get_tsigkey(self, tsigkey):
        """Get a zone

        :param tsigkey: The value can be the ID of a tsigkey
            or a :class:'~openstack.dns.v2.tsigkey.TSIGKey' instance.
        :returns: A generator of tsigkey
            :class:'~openstack.dns.v2.tsigkey.TSIGKey' instances.
        """
        return self._get(_tsigkey.TSIGKey, tsigkey)

    def delete_tsigkey(
        self, tsigkey, ignore_missing=True, delete_shares=False
    ):
        """Delete a TSIG key

        :param tsigkey: The value can be the ID of a TSIG key
            or a :class:`~openstack.dns.v2.tsigkey.TSIGKey` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the TSIG key does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent TSIG key.

        :returns: TSIG Key that has been deleted
        :rtype: :class:`~openstack.dns.v2.tsigkey.TSIGKey`
        """

        return self._delete(
            _tsigkey.TSIGKey,
            tsigkey,
            ignore_missing=ignore_missing,
            delete_shares=delete_shares,
        )

    def find_tsigkey(self, name_or_id, ignore_missing=True):
        """Find a single tsigkey

        :param name_or_id: The name or ID of a tsigkey
        :param bool ignore_missing: When set to ``False``
            :class: `!openstack.exceptions.ResourceNotFound` will be raised
            when the tsigkey does not exit.
            Wehn set to ``True``, no exception will be set when attempting
            to delete a nonexitstent zone.

        :returns::class:`~openstack.dns.v2.tsigkey.TSIGKey`
        """
        return self._find(
            _tsigkey.TSIGKey, name_or_id, ignore_missing=ignore_missing
        )
