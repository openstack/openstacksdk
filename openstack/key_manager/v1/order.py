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
from openstack import resource


class Order(resource.Resource):
    resources_key = 'orders'
    base_path = '/orders'
    service = key_manager_service.KeyManagerService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    # TODO(briancurtin): not documented
    error_reason = resource.prop('error_reason')
    # TODO(briancurtin): not documented
    error_status_code = resource.prop('error_status_code')
    #: a dictionary containing key-value parameters which specify the
    #: details of an order request
    meta = resource.prop('meta')
    #: A URI for this order
    order_ref = resource.prop('order_ref')
    #: TODO(briancurtin): not documented
    secret_ref = resource.prop('secret_ref')
    # The status of this order
    status = resource.prop('status')
    # The type of order
    type = resource.prop('type')
