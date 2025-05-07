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

import enum
import typing as ty

from keystoneauth1 import adapter as ksa_adapter

from openstack import exceptions
from openstack import resource
from openstack import utils


class Level(enum.Enum):
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    INFO = 'INFO'
    DEBUG = 'DEBUG'


class Binary(enum.Enum):
    ANY = '*'
    API = 'cinder-api'
    VOLUME = 'cinder-volume'
    SCHEDULER = 'cinder-scheduler'
    BACKUP = 'cinder-backup'


class LogLevel(resource.Resource):
    # Properties
    #: The binary name of the service.
    binary = resource.Body('binary')
    # TODO(stephenfin): Do we need these? They are request-only.
    # #: The name of the host.
    # server = resource.Body('server')
    # #: he prefix for the log path we are querying, for example ``cinder.`` or
    # #: ``sqlalchemy.engine.`` When not present or the empty string is passed
    # #: all log levels will be retrieved.
    # prefix = resource.Body('prefix')
    #: The name of the host.
    host = resource.Body('host')
    #: The current log level that queried.
    levels = resource.Body('levels', type=dict)


class Service(resource.Resource):
    resources_key = 'services'
    base_path = '/os-services'

    # capabilities
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'binary',
        'host',
    )

    # Properties
    #: The ID of active storage backend (cinder-volume services only)
    active_backend_id = resource.Body('active_backend_id')
    #: The availability zone of service
    availability_zone = resource.Body('zone')
    #: The state of storage backend (cinder-volume services only) (since 3.49)
    backend_state = resource.Body('backend_state')
    #: Binary name of service
    binary = resource.Body('binary')
    #: The cluster name (since 3.7)
    cluster = resource.Body('cluster')
    #: Disabled reason of service
    disabled_reason = resource.Body('disabled_reason')
    #: The name of the host where service runs
    host = resource.Body('host')
    # Whether the host is frozen or not (cinder-volume services only)
    is_frozen = resource.Body('frozen')
    #: Service name
    name = resource.Body('name', alias='binary')
    #: The volume service replication status (cinder-volume services only)
    replication_status = resource.Body('replication_status')
    #: State of service
    state = resource.Body('state')
    #: Status of service
    status = resource.Body('status')
    #: The date and time when the resource was updated
    updated_at = resource.Body('updated_at')

    # 3.32 introduced the 'set-log' action
    _max_microversion = '3.32'

    @classmethod
    def find(cls, session, name_or_id, ignore_missing=True, **params):
        # No direct request possible, thus go directly to list
        data = cls.list(session, **params)

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
        return super().commit(
            session,
            prepend_key,
            *args,
            **kwargs,
        )

    def _action(self, session, action, body, microversion=None):
        if not microversion:
            microversion = session.default_microversion
        url = utils.urljoin(Service.base_path, action)
        response = session.put(url, json=body, microversion=microversion)
        self._translate_response(response)
        return self

    def enable(self, session):
        """Enable service."""
        body = {'binary': self.binary, 'host': self.host}
        return self._action(session, 'enable', body)

    def disable(self, session, *, reason=None):
        """Disable service."""
        body = {'binary': self.binary, 'host': self.host}

        if not reason:
            action = 'disable'
        else:
            action = 'disable-log-reason'
            body['disabled_reason'] = reason

        return self._action(session, action, body)

    def thaw(self, session):
        body = {'host': self.host}
        return self._action(session, 'thaw', body)

    def freeze(self, session):
        body = {'host': self.host}
        return self._action(session, 'freeze', body)

    @classmethod
    def set_log_levels(
        cls,
        session: ksa_adapter.Adapter,
        *,
        level: Level,
        binary: Binary | None = None,
        server: str | None = None,
        prefix: str | None = None,
    ) -> None:
        """Set log level for services.

        :param session: The session to use for making this request.
        :param level: The log level to set, case insensitive, accepted values
            are ``INFO``, ``WARNING``, ``ERROR`` and ``DEBUG``.
        :param binary: The binary name of the service.
        :param server: The name of the host.
        :param prefix: The prefix for the log path we are querying, for example
            ``cinder.`` or ``sqlalchemy.engine.`` When not present or the empty
            string is passed all log levels will be retrieved.
        :returns: None.
        """
        microversion = cls._assert_microversion_for(
            session, '3.32', error_message="Cannot use set-log action"
        )
        body = {
            'level': level,
            'binary': binary or '',  # cinder insists on strings
            'server': server,
            'prefix': prefix,
        }
        url = utils.urljoin(cls.base_path, 'set-log')
        response = session.put(url, json=body, microversion=microversion)
        exceptions.raise_from_response(response)

    @classmethod
    def get_log_levels(
        cls,
        session: ksa_adapter.Adapter,
        *,
        binary: Binary | None = None,
        server: str | None = None,
        prefix: str | None = None,
    ) -> ty.Generator[LogLevel, None, None]:
        """Get log level for services.

        :param session: The session to use for making this request.
        :param binary: The binary name of the service.
        :param server: The name of the host.
        :param prefix: The prefix for the log path we are querying, for example
            ``cinder.`` or ``sqlalchemy.engine.`` When not present or the empty
            string is passed all log levels will be retrieved.
        :returns: A generator of
            :class:`~openstack.block_storage.v3.service.LogLevel` objects.
        """
        microversion = cls._assert_microversion_for(
            session, '3.32', error_message="Cannot use get-log action"
        )
        body = {
            'binary': binary or '',  # cinder insists on strings
            'server': server,
            'prefix': prefix,
        }
        url = utils.urljoin(cls.base_path, 'get-log')
        response = session.put(url, json=body, microversion=microversion)
        exceptions.raise_from_response(response)

        for entry in response.json()['log_levels']:
            yield LogLevel(
                binary=entry['binary'],
                host=entry['host'],
                levels=entry['levels'],
            )

    def failover(
        self,
        session,
        *,
        cluster=None,
        backend_id=None,
    ):
        """Failover a service

        Only applies to replicating cinder-volume services.
        """
        body = {'host': self.host}
        if cluster:
            body['cluster'] = cluster
        if backend_id:
            body['backend_id'] = backend_id

        action = 'failover_host'
        if utils.supports_microversion(session, '3.26'):
            action = 'failover'

        return self._action(session, action, body)
