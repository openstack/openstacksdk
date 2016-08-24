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

from openstack.key_manager import key_manager_service
from openstack.key_manager.v1 import _format
from openstack import resource2


class Order(resource2.Resource):
    resources_key = 'orders'
    base_path = '/orders'
    service = key_manager_service.KeyManagerService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True

    #: Timestamp in ISO8601 format of when the order was created
    created_at = resource2.Body('created')
    #: Keystone Id of the user who created the order
    creator_id = resource2.Body('creator_id')
    #: A dictionary containing key-value parameters which specify the
    #: details of an order request
    meta = resource2.Body('meta', type=dict)
    #: A URI for this order
    order_ref = resource2.Body('order_ref')
    #: The ID of this order
    order_id = resource2.Body('order_ref', alternate_id=True,
                              type=_format.HREFToUUID)
    #: Secret href associated with the order
    secret_ref = resource2.Body('secret_ref')
    #: Secret ID associated with the order
    secret_id = resource2.Body('secret_ref', type=_format.HREFToUUID)
    # The status of this order
    status = resource2.Body('status')
    #: Metadata associated with the order
    sub_status = resource2.Body('sub_status')
    #: Metadata associated with the order
    sub_status_message = resource2.Body('sub_status_message')
    # The type of order
    type = resource2.Body('type')
    #: 	Timestamp in ISO8601 format of the last time the order was updated.
    updated_at = resource2.Body('updated')
