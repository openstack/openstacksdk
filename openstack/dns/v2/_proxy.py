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

from typing import Any, ClassVar, Literal, overload
from collections.abc import Callable, Generator, Sequence
import queue

from openstack.dns.v2 import blacklist as _blacklist
from openstack.dns.v2 import floating_ip as _fip
from openstack.dns.v2 import limit as _limit
from openstack.dns.v2 import quota as _quota
from openstack.dns.v2 import recordset as _rs
from openstack.dns.v2 import service_status as _svc_status
from openstack.dns.v2 import tld as _tld
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
    api_version: ClassVar[Literal['2']] = '2'

    _resource_registry = {
        "blacklist": _blacklist.Blacklist,
        "floating_ip": _fip.FloatingIP,
        "limits": _limit.Limit,
        "quota": _quota.Quota,
        "recordset": _rs.Recordset,
        "service_status": _svc_status.ServiceStatus,
        "zone": _zone.Zone,
        "tsigkey": _tsigkey.TSIGKey,
        "zone_export": _zone_export.ZoneExport,
        "zone_import": _zone_import.ZoneImport,
        "zone_nameserver": _zone_nameserver.ZoneNameserver,
        "zone_share": _zone_share.ZoneShare,
        "zone_transfer_request": _zone_transfer.ZoneTransferRequest,
        "tld": _tld.TLD,
    }

    # ======== Zones ========
    def zones(self, **query: Any) -> Generator[_zone.Zone, None, None]:
        """Retrieve a generator of zones

        :param query: Optional query parameters to be sent to limit the
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

    def create_zone(self, **attrs: Any) -> _zone.Zone:
        """Create a new zone from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.dns.v2.zone.Zone`,
            comprised of the properties on the Zone class.
        :returns: The results of zone creation.
        """
        if attrs.get('type') == "SECONDARY":
            attrs.pop('email', None)
            attrs.pop('ttl', None)
        return self._create(_zone.Zone, prepend_key=False, **attrs)

    def get_zone(self, zone: str | _zone.Zone) -> _zone.Zone:
        """Get a zone

        :param zone: The value can be the ID of a zone
            or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :returns: Zone instance.
        """
        return self._get(_zone.Zone, zone)

    # TODO(stephenfin): This method should return None
    def delete_zone(
        self,
        zone: str | _zone.Zone,
        ignore_missing: bool = True,
        delete_shares: bool = False,
    ) -> _zone.Zone | None:
        """Delete a zone

        :param zone: The value can be the ID of a zone
            or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the zone does not exist. When set to ``True``, no exception
            will be set when attempting to delete a nonexistent zone.
        :param delete_shares: When True, delete the zone shares along with
                                   the zone.

        :returns: Zone been deleted
        """
        return self._delete(
            _zone.Zone,
            zone,
            ignore_missing=ignore_missing,
            delete_shares=delete_shares,
        )

    def update_zone(self, zone: str | _zone.Zone, **attrs: Any) -> _zone.Zone:
        """Update zone attributes

        :param zone: The id or an instance of
            :class:`~openstack.dns.v2.zone.Zone`.
        :param attrs: attributes for update on
            :class:`~openstack.dns.v2.zone.Zone`.

        """
        return self._update(_zone.Zone, zone, **attrs)

    @overload
    def find_zone(
        self,
        name_or_id: str,
        ignore_missing: Literal[False],
    ) -> _zone.Zone: ...

    @overload
    def find_zone(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
    ) -> _zone.Zone | None: ...

    def find_zone(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
    ) -> _zone.Zone | None:
        """Find a single zone

        :param name_or_id: The name or ID of a zone
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the zone does not exist.
            When set to ``True``, no exception will be set when attempting
            to delete a nonexistent zone.

        :returns: :class:`~openstack.dns.v2.zone.Zone`
        """
        return self._find(
            _zone.Zone, name_or_id, ignore_missing=ignore_missing
        )

    def abandon_zone(self, zone: str | _zone.Zone, **attrs: Any) -> None:
        """Abandon Zone

        :param zone: The value can be the ID of a zone to be abandoned
            or a :class:`~openstack.dns.v2.zone_export.ZoneExport` instance.

        :returns: None
        """
        zone = self._get_resource(_zone.Zone, zone)

        zone.abandon(self)

    def xfr_zone(self, zone: str | _zone.Zone, **attrs: Any) -> None:
        """Trigger update of secondary Zone

        :param zone: The value can be the ID of a zone to be abandoned
            or a :class:`~openstack.dns.v2.zone_export.ZoneExport` instance.

        :returns: None
        """
        zone = self._get_resource(_zone.Zone, zone)
        zone.xfr(self)

    # ======== Zone nameservers ========
    def zone_nameservers(
        self,
        zone: str | _zone.Zone,
    ) -> Generator[_zone_nameserver.ZoneNameserver, None, None]:
        """Retrieve a generator of nameservers for a zone

        :param zone: The value can be the ID of a zone or a
            :class:`~openstack.dns.v2.zone.Zone` instance.
        :returns: A generator of
            :class:`~openstack.dns.v2.zone_nameserver.ZoneNameserver`
            instances.
        """
        zone_id = resource.Resource._get_id(zone)
        return self._list(
            _zone_nameserver.ZoneNameserver,
            zone_id=zone_id,
        )

    # ======== Recordsets ========
    def recordsets(
        self,
        zone: str | _zone.Zone | None = None,
        **query: Any,
    ) -> Generator[_rs.Recordset, None, None]:
        """Retrieve a generator of recordsets

        :param zone: The optional value can be the ID of a zone
            or a :class:`~openstack.dns.v2.zone.Zone` instance. If it is not
            given all recordsets for all zones of the tenant would be
            retrieved
        :param query: Optional query parameters to be sent to limit the
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

    def create_recordset(
        self,
        zone: str | _zone.Zone,
        **attrs: Any,
    ) -> _rs.Recordset:
        """Create a new recordset in the zone

        :param zone: The value can be the ID of a zone
            or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.dns.v2.recordset.Recordset`,
            comprised of the properties on the Recordset class.
        :returns: The results of zone creation
        """
        zone = self._get_resource(_zone.Zone, zone)
        attrs.update({'zone_id': zone.id})
        return self._create(_rs.Recordset, prepend_key=False, **attrs)

    def update_recordset(
        self, recordset: str | _rs.Recordset, **attrs: Any
    ) -> _rs.Recordset:
        """Update Recordset attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.dns.v2.recordset.Recordset`,
            comprised of the properties on the Recordset class.
        :returns: The results of zone creation
        """
        return self._update(_rs.Recordset, recordset, **attrs)

    def get_recordset(
        self,
        recordset: str | _rs.Recordset,
        zone: str | _zone.Zone,
    ) -> _rs.Recordset:
        """Get a recordset

        :param zone: The value can be the ID of a zone
            or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :param recordset: The value can be the ID of a recordset
            or a :class:`~openstack.dns.v2.recordset.Recordset` instance.
        :returns: Recordset instance
        """
        zone = self._get_resource(_zone.Zone, zone)
        return self._get(_rs.Recordset, recordset, zone_id=zone.id)

    # TODO(stephenfin): This method should return None
    def delete_recordset(
        self,
        recordset: str | _rs.Recordset,
        zone: str | _zone.Zone | None = None,
        ignore_missing: bool = True,
    ) -> _rs.Recordset | None:
        """Delete a zone

        :param recordset: The value can be the ID of a recordset
            or a :class:`~openstack.dns.v2.recordset.Recordset`
            instance.
        :param zone: The value can be the ID of a zone
            or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the zone does not exist. When set to ``True``, no exception
            will be set when attempting to delete a nonexistent zone.

        :returns: Recordset instance been deleted
        """
        if zone:
            zone = self._get_resource(_zone.Zone, zone)
            recordset = self._get(_rs.Recordset, recordset, zone_id=zone.id)
        return self._delete(
            _rs.Recordset, recordset, ignore_missing=ignore_missing
        )

    @overload
    def find_recordset(
        self,
        zone: str | _zone.Zone,
        name_or_id: str,
        ignore_missing: Literal[False],
        **query: Any,
    ) -> _rs.Recordset: ...

    @overload
    def find_recordset(
        self,
        zone: str | _zone.Zone,
        name_or_id: str,
        ignore_missing: bool = True,
        **query: Any,
    ) -> _rs.Recordset | None: ...

    def find_recordset(
        self,
        zone: str | _zone.Zone,
        name_or_id: str,
        ignore_missing: bool = True,
        **query: Any,
    ) -> _rs.Recordset | None:
        """Find a single recordset

        :param zone: The value can be the ID of a zone
            or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :param name_or_id: The name or ID of a zone
        :param ignore_missing: When set to ``False``
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
    def zone_imports(
        self,
        **query: Any,
    ) -> Generator[_zone_import.ZoneImport, None, None]:
        """Retrieve a generator of zone imports

        :param query: Optional query parameters to be sent to limit the
            resources being returned.

            * `zone_id`: Zone I field.
            * `message`: Message field.
            * `status`: Status of the zone import record.

        :returns: A generator of zone
            :class:`~openstack.dns.v2.zone_import.ZoneImport` instances.
        """
        return self._list(_zone_import.ZoneImport, **query)

    def create_zone_import(self, **attrs: Any) -> _zone_import.ZoneImport:
        """Create a new zone import from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.dns.v2.zone_import.ZoneImport`,
            comprised of the properties on the ZoneImport class.
        :returns: The results of zone creation.
        """
        return self._create(
            _zone_import.ZoneImport, prepend_key=False, **attrs
        )

    def get_zone_import(
        self, zone_import: str | _zone_import.ZoneImport
    ) -> _zone_import.ZoneImport:
        """Get a zone import record

        :param zone: The value can be the ID of a zone import
            or a :class:`~openstack.dns.v2.zone_import.ZoneImport` instance.
        :returns: ZoneImport instance.
        """
        return self._get(_zone_import.ZoneImport, zone_import)

    # TODO(stephenfin): This method should return None
    def delete_zone_import(
        self,
        zone_import: str | _zone_import.ZoneImport,
        ignore_missing: bool = True,
    ) -> _zone_import.ZoneImport | None:
        """Delete a zone import

        :param zone_import: The value can be the ID of a zone import
            or a :class:`~openstack.dns.v2.zone_import.ZoneImport` instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the zone does not exist. When set to ``True``, no exception
            will be set when attempting to delete a nonexistent zone.

        :returns: The deleted zone import.
        """
        return self._delete(
            _zone_import.ZoneImport, zone_import, ignore_missing=ignore_missing
        )

    # ======== Zone Exports ========
    def zone_exports(
        self,
        **query: Any,
    ) -> Generator[_zone_export.ZoneExport, None, None]:
        """Retrieve a generator of zone exports

        :param query: Optional query parameters to be sent to limit the
            resources being returned.

            * `zone_id`: Zone I field.
            * `message`: Message field.
            * `status`: Status of the zone import record.

        :returns: A generator of zone
            :class:`~openstack.dns.v2.zone_export.ZoneExport` instances.
        """
        return self._list(_zone_export.ZoneExport, **query)

    def create_zone_export(
        self,
        zone: str | _zone.Zone,
        **attrs: Any,
    ) -> _zone_export.ZoneExport:
        """Create a new zone export from attributes

        :param zone: The value can be the ID of a zone to be exported
            or a :class:`~openstack.dns.v2.zone_export.ZoneExport` instance.
        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.dns.v2.zone_export.ZoneExport`,
            comprised of the properties on the ZoneExport class.
        :returns: The results of zone creation.
        """
        zone = self._get_resource(_zone.Zone, zone)
        return self._create(
            _zone_export.ZoneExport,
            base_path='/zones/%(zone_id)s/tasks/export',
            prepend_key=False,
            zone_id=zone.id,
            **attrs,
        )

    def get_zone_export(
        self, zone_export: str | _zone_export.ZoneExport
    ) -> _zone_export.ZoneExport:
        """Get a zone export record

        :param zone: The value can be the ID of a zone import
            or a :class:`~openstack.dns.v2.zone_export.ZoneExport` instance.
        :returns: ZoneExport instance.
        """
        return self._get(_zone_export.ZoneExport, zone_export)

    def get_zone_export_text(
        self, zone_export: str | _zone_export.ZoneExport
    ) -> _zone_export.ZoneExport:
        """Get a zone export record as text

        :param zone: The value can be the ID of a zone import
            or a :class:`~openstack.dns.v2.zone_export.ZoneExport` instance.
        :returns: ZoneExport instance.
        """
        return self._get(
            _zone_export.ZoneExport,
            zone_export,
            base_path='/zones/tasks/export/%(id)s/export',
        )

    # TODO(stephenfin): This method should return None
    def delete_zone_export(
        self,
        zone_export: str | _zone_export.ZoneExport,
        ignore_missing: bool = True,
    ) -> _zone_export.ZoneExport | None:
        """Delete a zone export

        :param zone_export: The value can be the ID of a zone import
            or a :class:`~openstack.dns.v2.zone_export.ZoneExport` instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the zone does not exist. When set to ``True``, no exception
            will be set when attempting to delete a nonexistent zone.

        :returns: The deleted zone export.
        """
        return self._delete(
            _zone_export.ZoneExport, zone_export, ignore_missing=ignore_missing
        )

    # ======== FloatingIPs ========
    def floating_ips(
        self,
        **query: Any,
    ) -> Generator[_fip.FloatingIP, None, None]:
        """Retrieve a generator of recordsets

        :param query: Optional query parameters to be sent to limit the
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

    def get_floating_ip(
        self, floating_ip: str | _fip.FloatingIP
    ) -> _fip.FloatingIP:
        """Get a Floating IP

        :param floating_ip: The value can be the ID of a floating ip
            or a :class:`~openstack.dns.v2.floating_ip.FloatingIP` instance.
            The ID is in format "region_name:floatingip_id"
        :returns: FloatingIP instance.
        """
        return self._get(_fip.FloatingIP, floating_ip)

    def update_floating_ip(
        self, floating_ip: str | _fip.FloatingIP, **attrs: Any
    ) -> _fip.FloatingIP:
        """Update floating ip attributes

        :param floating_ip: The id or an instance of
            :class:`~openstack.dns.v2.fip.FloatingIP`.
        :param attrs: attributes for update on
            :class:`~openstack.dns.v2.fip.FloatingIP`.

        """
        return self._update(_fip.FloatingIP, floating_ip, **attrs)

    def unset_floating_ip(
        self, floating_ip: str | _fip.FloatingIP
    ) -> _fip.FloatingIP:
        """Unset a Floating IP PTR record
        :param floating_ip: ID for the floatingip associated with the
            project.
        :returns: FloatingIP PTR record.
        """
        # concat `region:floating_ip_id` as id
        attrs = {'ptrdname': None}
        return self._update(_fip.FloatingIP, floating_ip, **attrs)

    # ======== Zone Transfer ========
    def zone_transfer_requests(
        self,
        **query: Any,
    ) -> Generator[_zone_transfer.ZoneTransferRequest, None, None]:
        """Retrieve a generator of zone transfer requests

        :param query: Optional query parameters to be sent to limit the
            resources being returned.

            * `status`: Status of the recordset.

        :returns: A generator of transfer requests
            (:class:`~openstack.dns.v2.zone_transfer.ZoneTransferRequest`)
            instances
        """
        return self._list(_zone_transfer.ZoneTransferRequest, **query)

    def get_zone_transfer_request(
        self, request: str | _zone_transfer.ZoneTransferRequest
    ) -> _zone_transfer.ZoneTransferRequest:
        """Get a ZoneTransfer Request info

        :param request: The value can be the ID of a transfer request
            or a :class:`~openstack.dns.v2.zone_transfer.ZoneTransferRequest`
            instance.
        :returns: Zone transfer request instance.
        """
        return self._get(_zone_transfer.ZoneTransferRequest, request)

    def create_zone_transfer_request(
        self,
        zone: str | _zone.Zone,
        **attrs: Any,
    ) -> _zone_transfer.ZoneTransferRequest:
        """Create a new ZoneTransfer Request from attributes

        :param zone: The value can be the ID of a zone to be transferred
            or a :class:`~openstack.dns.v2.zone_export.ZoneExport` instance.
        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.dns.v2.zone_transfer.ZoneTransferRequest`,
            comprised of the properties on the ZoneTransferRequest class.
        :returns: The results of zone transfer request creation.
        """
        zone = self._get_resource(_zone.Zone, zone)
        return self._create(
            _zone_transfer.ZoneTransferRequest,
            base_path='/zones/%(zone_id)s/tasks/transfer_requests',
            prepend_key=False,
            zone_id=zone.id,
            **attrs,
        )

    def update_zone_transfer_request(
        self, request: str | _zone_transfer.ZoneTransferRequest, **attrs: Any
    ) -> _zone_transfer.ZoneTransferRequest:
        """Update ZoneTransfer Request attributes

        :param floating_ip: The id or an instance of
            :class:`~openstack.dns.v2.zone_transfer.ZoneTransferRequest`.
        :param attrs: attributes for update on
            :class:`~openstack.dns.v2.zone_transfer.ZoneTransferRequest`.

        """
        return self._update(
            _zone_transfer.ZoneTransferRequest, request, **attrs
        )

    # TODO(stephenfin): This method should return None
    def delete_zone_transfer_request(
        self,
        request: str | _zone_transfer.ZoneTransferRequest,
        ignore_missing: bool = True,
    ) -> _zone_transfer.ZoneTransferRequest | None:
        """Delete a ZoneTransfer Request

        :param request: The value can be the ID of a zone transfer request
            or a :class:`~openstack.dns.v2.zone_transfer.ZoneTransferRequest`
            instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the zone does not exist. When set to ``True``, no exception
            will be set when attempting to delete a nonexistent zone.

        :returns: The deleted zone transfer request.
        """
        return self._delete(
            _zone_transfer.ZoneTransferRequest,
            request,
            ignore_missing=ignore_missing,
        )

    def zone_transfer_accepts(
        self,
        **query: Any,
    ) -> Generator[_zone_transfer.ZoneTransferAccept, None, None]:
        """Retrieve a generator of zone transfer accepts

        :param query: Optional query parameters to be sent to limit the
            resources being returned.

            * `status`: Status of the recordset.

        :returns: A generator of transfer accepts
            (:class:`~openstack.dns.v2.zone_transfer.ZoneTransferAccept`)
            instances
        """
        return self._list(_zone_transfer.ZoneTransferAccept, **query)

    def get_zone_transfer_accept(
        self, accept: str | _zone_transfer.ZoneTransferAccept
    ) -> _zone_transfer.ZoneTransferAccept:
        """Get a ZoneTransfer Accept info

        :param request: The value can be the ID of a transfer accept
            or a :class:`~openstack.dns.v2.zone_transfer.ZoneTransferAccept`
            instance.
        :returns: Zone transfer request instance.
        """
        return self._get(_zone_transfer.ZoneTransferAccept, accept)

    def create_zone_transfer_accept(
        self, **attrs: Any
    ) -> _zone_transfer.ZoneTransferAccept:
        """Create a new ZoneTransfer Accept from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.dns.v2.zone_transfer.ZoneTransferAccept`,
            comprised of the properties on the ZoneTransferAccept class.
        :returns: The results of zone transfer request creation.
        """
        return self._create(_zone_transfer.ZoneTransferAccept, **attrs)

    # ======== Zone Shares ========
    def zone_shares(
        self,
        zone: str | _zone.Zone,
        **query: Any,
    ) -> Generator[_zone_share.ZoneShare, None, None]:
        """Retrieve a generator of zone shares

        :param zone: The zone ID or a
            :class:`~openstack.dns.v2.zone.Zone` instance
        :param query: Optional query parameters to be sent to limit the
                           resources being returned.

                           * `target_project_id`: The target project ID field.

        :returns: A generator of zone shares
            :class:`~openstack.dns.v2.zone_share.ZoneShare` instances.
        """
        zone_obj = self._get_resource(_zone.Zone, zone)
        return self._list(_zone_share.ZoneShare, zone_id=zone_obj.id, **query)

    def get_zone_share(
        self,
        zone: str | _zone.Zone,
        zone_share: str | _zone_share.ZoneShare,
    ) -> _zone_share.ZoneShare:
        """Get a zone share

        :param zone: The value can be the ID of a zone
            or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :param zone_share: The zone_share can be either the ID of the zone
            share or a :class:`~openstack.dns.v2.zone_share.ZoneShare` instance
            that the zone share belongs to.

        :returns: ZoneShare instance.
        """
        zone_obj = self._get_resource(_zone.Zone, zone)
        return self._get(
            _zone_share.ZoneShare, zone_share, zone_id=zone_obj.id
        )

    @overload
    def find_zone_share(
        self,
        zone: str | _zone.Zone,
        zone_share_id: str,
        ignore_missing: Literal[False],
    ) -> _zone_share.ZoneShare: ...

    @overload
    def find_zone_share(
        self,
        zone: str | _zone.Zone,
        zone_share_id: str,
        ignore_missing: bool = True,
    ) -> _zone_share.ZoneShare | None: ...

    def find_zone_share(
        self,
        zone: str | _zone.Zone,
        zone_share_id: str,
        ignore_missing: bool = True,
    ) -> _zone_share.ZoneShare | None:
        """Find a single zone share

        :param zone: The value can be the ID of a zone
            or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :param zone_share_id: The zone share ID
        :param ignore_missing: When set to ``False``
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

    def create_zone_share(
        self,
        zone: str | _zone.Zone,
        **attrs: Any,
    ) -> _zone_share.ZoneShare:
        """Create a new zone share from attributes

        :param zone: The zone ID or a
            :class:`~openstack.dns.v2.zone.Zone` instance
        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.dns.v2.zone_share.ZoneShare`,
            comprised of the properties on the ZoneShare class.

        :returns: The results of zone share creation
        """
        zone_obj = self._get_resource(_zone.Zone, zone)
        return self._create(
            _zone_share.ZoneShare, zone_id=zone_obj.id, **attrs
        )

    def delete_zone_share(
        self,
        zone: str | _zone.Zone,
        zone_share: str | _zone_share.ZoneShare,
        ignore_missing: bool = True,
    ) -> None:
        """Delete a zone share

        :param zone: The zone ID or a
            :class:`~openstack.dns.v2.zone.Zone` instance
        :param zone_share: The zone_share can be either the ID of the zone
            share or a :class:`~openstack.dns.v2.zone_share.ZoneShare` instance
            that the zone share belongs to.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the zone share does not exist. When set to ``True``, no
            exception will be set when attempting to delete a nonexistent zone
            share.

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
    def limits(self, **query: Any) -> Generator[_limit.Limit, None, None]:
        """Retrieve a generator of limits

        :returns: A generator of limits
            (:class:`~openstack.dns.v2.limit.Limit`) instances
        """
        return self._list(_limit.Limit, **query)

    # ======== Quotas ========
    def quotas(self, **query: Any) -> Generator[_quota.Quota, None, None]:
        """Return a generator of quotas

        :param query: Optional query parameters to be sent to limit the
            resources being returned.

        :returns: A generator of quota objects
        """
        return self._list(_quota.Quota, **query)

    def get_quota(self, quota: str | _quota.Quota) -> _quota.Quota:
        """Get a quota

        :param quota: The value can be the ID of a quota or a
            :class:`~openstack.dns.v2.quota.Quota` instance.
            The ID of a quota is the same as the project ID for the quota.

        :returns: One :class:`~openstack.dns.v2.quota.Quota`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
        """
        return self._get(_quota.Quota, quota)

    def update_quota(
        self, quota: str | _quota.Quota, **attrs: Any
    ) -> _quota.Quota:
        """Update a quota

        :param quota: Either the ID of a quota or a
            :class:`~openstack.dns.v2.quota.Quota` instance. The ID of a quota
            is the same as the project ID for the quota.
        :param attrs: The attributes to update on the quota represented
            by ``quota``.

        :returns: The updated quota
        """
        return self._update(_quota.Quota, quota, **attrs)

    # TODO(stephenfin): This method should return None
    def delete_quota(
        self, quota: str | _quota.Quota, ignore_missing: bool = True
    ) -> _quota.Quota | None:
        """Delete a quota (i.e. reset to the default quota)

        :param quota: The value can be the ID of a quota or a
            :class:`~openstack.dns.v2.quota.Quota` instance.
            The ID of a quota is the same as the project ID for the quota.
        :param ignore_missing: When set to ``False``,
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the quota does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent quota.

        :returns: The deleted quota.
        """
        return self._delete(_quota.Quota, quota, ignore_missing=ignore_missing)

    # ======== Service Statuses ========
    def service_statuses(
        self,
    ) -> Generator[_svc_status.ServiceStatus, None, None]:
        """Retrieve a generator of service statuses

        :returns: A generator of service statuses
            :class:`~openstack.dns.v2.service_status.ServiceStatus` instances.
        """
        return self._list(_svc_status.ServiceStatus)

    def get_service_status(
        self, service: str | _svc_status.ServiceStatus
    ) -> _svc_status.ServiceStatus:
        """Get a status of a service in the Designate system

        :param service: The value can be the ID of a service
            or a :class:`~openstack.dns.v2.service_status.ServiceStatus`
            instance.

        :returns: ServiceStatus instance.
        """
        return self._get(_svc_status.ServiceStatus, service)

    # ======== TLDs ========
    def tlds(self, **query: Any) -> Generator[_tld.TLD, None, None]:
        """Retrieve a generator of tlds

        :param query: Optional query parameters to be sent to limit the
            resources being returned.

            * `name`: TLD Name field.

        :returns: A generator of tld
            :class:`~openstack.dns.v2.tld.TLD` instances.
        """
        return self._list(_tld.TLD, **query)

    def create_tld(self, **attrs: Any) -> _tld.TLD:
        """Create a new tld from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.dns.v2.tld.TLD`,
            comprised of the properties on the TLD class.
        :returns: The results of TLD creation.
        """
        return self._create(_tld.TLD, prepend_key=False, **attrs)

    def get_tld(self, tld: str | _tld.TLD) -> _tld.TLD:
        """Get a tld

        :param tld: The value can be the ID of a tld
            or a :class:`~openstack.dns.v2.tld.TLD` instance.
        :returns: tld instance.
        """
        return self._get(_tld.TLD, tld)

    # TODO(stephenfin): This method should return None
    def delete_tld(
        self, tld: str | _tld.TLD, ignore_missing: bool = True
    ) -> _tld.TLD | None:
        """Delete a tld

        :param tld: The value can be the ID of a tld
            or a :class:`~openstack.dns.v2.tld.TLD` instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the tld does not exist. When set to ``True``, no exception
            will be set when attempting to delete a nonexistent tld.

        :returns: TLD been deleted
        """
        return self._delete(
            _tld.TLD,
            tld,
            ignore_missing=ignore_missing,
        )

    def update_tld(self, tld: str | _tld.TLD, **attrs: Any) -> _tld.TLD:
        """Update tld attributes

        :param tld: The id or an instance of
            :class:`~openstack.dns.v2.tld.TLD`.
        :param attrs: attributes for update on
            :class:`~openstack.dns.v2.tld.TLD`.

        """
        return self._update(_tld.TLD, tld, **attrs)

    @overload
    def find_tld(
        self,
        name_or_id: str,
        ignore_missing: Literal[False],
    ) -> _tld.TLD: ...

    @overload
    def find_tld(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
    ) -> _tld.TLD | None: ...

    def find_tld(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
    ) -> _tld.TLD | None:
        """Find a single tld

        :param name_or_id: The name or ID of a tld
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the tld does not exist.
            When set to ``True``, no exception will be set when attempting
            to delete a nonexistent tld.

        :returns: :class:`~openstack.dns.v2.tld.TLD`
        """
        return self._find(_tld.TLD, name_or_id, ignore_missing=ignore_missing)

    # ====== TSIG keys ======
    def tsigkeys(
        self,
        **query: Any,
    ) -> Generator[_tsigkey.TSIGKey, None, None]:
        """Retrieve a generator of zones

        :param query: Optional query parameters to be sent to limit the
            resources being returned.

        :returns: A generator of zone
            :class: `~openstack.dns.v2.tsigkey.TSIGKey` instances.
        """
        return self._list(_tsigkey.TSIGKey, **query)

    def create_tsigkey(self, **attrs: Any) -> _tsigkey.TSIGKey:
        """Create a new tsigkey from attributes

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.dns.v2.tsigkey.Tsigkey`,
            comprised of the properties on the Tsigkey class.
        :returns: The results of zone creation.
        """
        return self._create(_tsigkey.TSIGKey, prepend_key=False, **attrs)

    def get_tsigkey(self, tsigkey: str | _tsigkey.TSIGKey) -> _tsigkey.TSIGKey:
        """Get a zone

        :param tsigkey: The value can be the ID of a tsigkey
            or a :class:'~openstack.dns.v2.tsigkey.TSIGKey' instance.
        :returns: A generator of tsigkey
            :class:'~openstack.dns.v2.tsigkey.TSIGKey' instances.
        """
        return self._get(_tsigkey.TSIGKey, tsigkey)

    def delete_tsigkey(
        self,
        tsigkey: str | _tsigkey.TSIGKey,
        ignore_missing: bool = True,
        delete_shares: bool = False,
    ) -> None:
        """Delete a TSIG key

        :param tsigkey: The value can be the ID of a TSIG key
            or a :class:`~openstack.dns.v2.tsigkey.TSIGKey` instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the TSIG key does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent TSIG key.
        :param delete_shares: Whether to delete associated shares.

        :returns: TSIG Key that has been deleted
        """

        self._delete(
            _tsigkey.TSIGKey,
            tsigkey,
            ignore_missing=ignore_missing,
            delete_shares=delete_shares,
        )

    @overload
    def find_tsigkey(
        self,
        name_or_id: str,
        ignore_missing: Literal[False],
    ) -> _tsigkey.TSIGKey: ...

    @overload
    def find_tsigkey(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
    ) -> _tsigkey.TSIGKey | None: ...

    def find_tsigkey(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
    ) -> _tsigkey.TSIGKey | None:
        """Find a single tsigkey

        :param name_or_id: The name or ID of a tsigkey
        :param ignore_missing: When set to ``False``
            :class: `!openstack.exceptions.ResourceNotFound` will be raised
            when the tsigkey does not exit.
            Wehn set to ``True``, no exception will be set when attempting
            to delete a nonexitstent zone.

        :returns::class:`~openstack.dns.v2.tsigkey.TSIGKey`
        """
        return self._find(
            _tsigkey.TSIGKey, name_or_id, ignore_missing=ignore_missing
        )

    # ======== Blacklists ========
    def blacklists(
        self,
        **query: Any,
    ) -> Generator[_blacklist.Blacklist, None, None]:
        """Retrieve a generator of blacklists

        :returns: A generator of blacklist
            (:class:`~openstack.dns.v2.blacklist.Blacklist`) instances
        """
        return self._list(_blacklist.Blacklist, **query)

    def get_blacklist(
        self, blacklist: str | _blacklist.Blacklist
    ) -> _blacklist.Blacklist:
        """Get a blacklist

        :param blacklist: The value can be the ID of a blacklist
            or a :class:`~openstack.dns.v2.blacklist.Blacklist` instance.

        :returns: Blacklist instance.
        """
        return self._get(_blacklist.Blacklist, blacklist)

    def create_blacklist(self, **attrs: Any) -> _blacklist.Blacklist:
        """Create a new blacklist

        :param attrs: Keyword arguments which will be used to create
            a :class:`~openstack.dns.v2.blacklist.Blacklist`,
            comprised of the properties on the Blacklist class.

        :returns: The results of blacklist creation.
        """
        return self._create(_blacklist.Blacklist, prepend_key=False, **attrs)

    def update_blacklist(
        self, blacklist: str | _blacklist.Blacklist, **attrs: Any
    ) -> _blacklist.Blacklist:
        """Update blacklist attributes

        :param blacklist: The id or an instance of
            :class: `~openstack.dns.v2.blacklist.Blacklist`.
        :param attrs: attributes for update on
            :class: `~openstack.dns.v2.blacklist.Blacklist`.

        :returns: The updated blacklist.
        """
        return self._update(_blacklist.Blacklist, blacklist, **attrs)

    # TODO(stephenfin): This method should return None
    def delete_blacklist(
        self,
        blacklist: str | _blacklist.Blacklist,
        ignore_missing: bool = True,
    ) -> _blacklist.Blacklist | None:
        """Delete a blacklist

        :param blacklist: The id or an instance of
            :class: `~openstack.dns.v2.blacklist.Blacklist`.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the blacklist does not exist. When set to ``True``, no
            exception will be set when attempting to delete a nonexistent
            blacklist.

        :returns: Blacklist been deleted
        """
        return self._delete(
            _blacklist.Blacklist, blacklist, ignore_missing=ignore_missing
        )

    # ========== Utilities ==========
    def wait_for_status(
        self,
        res: resource.ResourceT,
        status: str,
        failures: list[str] | None = None,
        interval: int | float | None = 2,
        wait: int | None = None,
        attribute: str = 'status',
        callback: Callable[[int], None] | None = None,
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

        :returns: The updated resource.
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
        interval: int | float | None = 2,
        wait: int | None = 120,
        callback: Callable[[int], None] | None = None,
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

    def _get_cleanup_dependencies(
        self,
    ) -> dict[str, proxy.CleanupDependency] | None:
        # DNS may depend on floating ip
        return {'dns': {'before': ['network']}}  # type: ignore[typeddict-item]

    def _service_cleanup(
        self,
        dry_run: bool = True,
        client_status_queue: queue.Queue[resource.Resource] | None = None,
        identified_resources: dict[str, resource.Resource] | None = None,
        filters: dict[str, Any] | None = None,
        resource_evaluation_fn: Callable[
            [
                resource.Resource,
                dict[str, Any] | None,
                dict[str, resource.Resource] | None,
            ],
            bool,
        ]
        | None = None,
        skip_resources: Sequence[str] | None = None,
    ) -> None:
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
            for fip_obj in self.floating_ips():
                self._service_cleanup_del_res(
                    self.unset_floating_ip,
                    fip_obj,
                    dry_run=dry_run,
                    client_status_queue=client_status_queue,
                    identified_resources=identified_resources,
                    filters=filters,
                    resource_evaluation_fn=resource_evaluation_fn,
                )
