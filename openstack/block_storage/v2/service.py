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


from openstack import exceptions
from openstack import resource
from openstack import utils


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
    #: Binary name of service
    binary = resource.Body('binary')
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

    def _action(self, session, action, body):
        url = utils.urljoin(Service.base_path, action)
        response = session.put(url, json=body)
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

    def failover(
        self,
        session,
        *,
        backend_id=None,
    ):
        """Failover a service

        Only applies to replicating cinder-volume services.
        """
        body = {'host': self.host}
        if backend_id:
            body['backend_id'] = backend_id

        return self._action(session, 'failover_host', body)
