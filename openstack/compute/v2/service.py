# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import typing as ty

from keystoneauth1 import adapter
import typing_extensions as ty_ext

from openstack import exceptions
from openstack import resource
from openstack import utils


class Service(resource.Resource):
    resource_key = 'service'
    resources_key = 'services'
    base_path = '/os-services'

    # capabilities
    allow_list = True
    allow_commit = True
    allow_delete = True

    _query_mapping = resource.QueryParameters(
        'name',
        'binary',
        'host',
        name='binary',
    )

    # Properties
    #: The availability zone of service
    availability_zone = resource.Body("zone")
    #: Binary name of service
    binary = resource.Body('binary')
    #: Disabled reason of service
    disabled_reason = resource.Body('disabled_reason')
    #: Whether or not this service was forced down manually by an administrator
    #: after the service was fenced
    is_forced_down = resource.Body('forced_down', type=bool)
    #: The name of the host where service runs
    host = resource.Body('host')
    #: Service name
    name = resource.Body('name', alias='binary')
    #: State of service
    state = resource.Body('state')
    #: Status of service
    status = resource.Body('status')
    #: The date and time when the resource was updated
    updated_at = resource.Body('updated_at')

    _max_microversion = '2.69'

    @ty.overload
    @classmethod
    def find(
        cls,
        session: adapter.Adapter,
        name_or_id: str,
        ignore_missing: ty.Literal[True] = True,
        list_base_path: str | None = None,
        *,
        microversion: str | None = None,
        all_projects: bool | None = None,
        **params: ty.Any,
    ) -> ty_ext.Self | None: ...

    @ty.overload
    @classmethod
    def find(
        cls,
        session: adapter.Adapter,
        name_or_id: str,
        ignore_missing: ty.Literal[False],
        list_base_path: str | None = None,
        *,
        microversion: str | None = None,
        all_projects: bool | None = None,
        **params: ty.Any,
    ) -> ty_ext.Self: ...

    # excuse the duplication here: it's mypy's fault
    # https://github.com/python/mypy/issues/14764
    @ty.overload
    @classmethod
    def find(
        cls,
        session: adapter.Adapter,
        name_or_id: str,
        ignore_missing: bool,
        list_base_path: str | None = None,
        *,
        microversion: str | None = None,
        all_projects: bool | None = None,
        **params: ty.Any,
    ) -> ty_ext.Self | None: ...

    @classmethod
    def find(
        cls,
        session: adapter.Adapter,
        name_or_id: str,
        ignore_missing: bool = True,
        list_base_path: str | None = None,
        *,
        microversion: str | None = None,
        all_projects: bool | None = None,
        **params: ty.Any,
    ) -> ty_ext.Self | None:
        # No direct request possible, thus go directly to list
        if list_base_path:
            params['base_path'] = list_base_path

        # all_projects is a special case that is used by multiple services. We
        # handle it here since it doesn't make sense to pass it to the .fetch
        # call above
        if all_projects is not None:
            params['all_projects'] = all_projects

        data = cls.list(
            session,
            base_path=list_base_path,
        )

        result = None
        for maybe_result in data:
            # Since ID might be both int and str force cast
            id_value = str(cls._get_id(maybe_result))
            name_value = maybe_result.name

            if str(name_or_id) in (id_value, name_value):
                if 'host' in params and maybe_result['host'] != params['host']:
                    continue
                # Only allow one resource to be found. If we already
                # found a match, raise an exception to show it.
                if result is None:
                    result = maybe_result
                else:
                    msg = "More than one %s exists with the name '%s'."
                    msg = msg % (cls.__name__, name_or_id)
                    raise exceptions.DuplicateResource(msg)

        if result is not None:
            return result

        if ignore_missing:
            return None
        raise exceptions.NotFoundException(
            f"No {cls.__name__} found for {name_or_id}"
        )

    def commit(self, session, prepend_key=False, *args, **kwargs):
        # we need to set prepend_key to false
        return super().commit(session, prepend_key, *args, **kwargs)

    def _action(self, session, action, body, microversion=None):
        if not microversion:
            microversion = session.default_microversion
        url = utils.urljoin(Service.base_path, action)
        response = session.put(url, json=body, microversion=microversion)
        self._translate_response(response)
        return self

    def set_forced_down(self, session, host=None, binary=None, forced=False):
        """Update forced_down information of a service."""
        microversion = session.default_microversion
        body = {}
        if not host:
            host = self.host
        if not binary:
            binary = self.binary
        body = {
            'host': host,
            'binary': binary,
        }
        if utils.supports_microversion(session, '2.11'):
            body['forced_down'] = forced
            # Using forced_down works only 2.11-2.52, therefore pin it
            microversion = '2.11'

        # This will not work with newest microversions
        return self._action(
            session,
            'force-down',
            body,
            microversion=microversion,
        )

    force_down = set_forced_down

    def enable(self, session, host, binary):
        """Enable service."""
        body = {
            'host': host,
            'binary': binary,
        }

        return self._action(session, 'enable', body)

    def disable(self, session, host, binary, reason=None):
        """Disable service."""
        body = {
            'host': host,
            'binary': binary,
        }

        if not reason:
            action = 'disable'
        else:
            body['disabled_reason'] = reason
            action = 'disable-log-reason'

        return self._action(session, action, body)
