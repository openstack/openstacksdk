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

import six

from openstack.compute import compute_service
from openstack import resource


class ServerMeta(resource.Resource):
    resource_key = 'meta'
    id_attribute = 'key'
    base_path = '/servers/%(server_id)s/metadata'
    service = compute_service.ComputeService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The metadata key.
    key = resource.prop('key')
    #: The ID of a server.
    server_id = resource.prop('server_id')
    #: The metadata value.
    value = resource.prop('value')

    @classmethod
    def create_by_id(cls, session, attrs, resource_id=None, path_args=None):
        url = cls._get_url(path_args, resource_id)
        body = {cls.resource_key: {attrs['key']: attrs['value']}}
        resp = session.put(url, endpoint_filter=cls.service, json=body)
        resp = resp.json()
        return {'key': resource_id,
                'value': resp[cls.resource_key][resource_id]}

    @classmethod
    def get_data_by_id(cls, session, resource_id, path_args=None,
                       include_headers=False):
        url = cls._get_url(path_args, resource_id)
        resp = session.get(url, endpoint_filter=cls.service)
        resp = resp.json()
        return {'key': resource_id,
                'value': resp[cls.resource_key][resource_id]}

    @classmethod
    def update_by_id(cls, session, resource_id, attrs, path_args=None):
        return cls.create_by_id(session, attrs, resource_id, path_args)

    @classmethod
    def delete_by_id(cls, session, resource_id, path_args=None):
        url = cls._get_url(path_args, resource_id)
        headers = {'Accept': ''}
        session.delete(url, endpoint_filter=cls.service, headers=headers)

    @classmethod
    def list(cls, session, path_args=None, **params):
        url = '/servers/%(server_id)s/metadata' % path_args
        resp = session.get(url, endpoint_filter=cls.service, params=params)
        resp = resp.json()
        resp = resp['metadata']
        return [cls.existing(server_id=path_args['server_id'], key=key,
                             value=value)
                for key, value in six.iteritems(resp)]
