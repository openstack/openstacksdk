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

from openstack.object_store.v1 import _base
from openstack import resource


class Account(_base.BaseResource):
    _custom_metadata_prefix = "X-Account-Meta-"

    base_path = "/"

    allow_fetch = True
    allow_commit = True
    allow_head = True

    #: The total number of bytes that are stored in Object Storage for
    #: the account.
    account_bytes_used = resource.Header("x-account-bytes-used", type=int)
    #: The number of containers.
    account_container_count = resource.Header("x-account-container-count",
                                              type=int)
    #: The number of objects in the account.
    account_object_count = resource.Header("x-account-object-count", type=int)
    #: The secret key value for temporary URLs. If not set,
    #: this header is not returned by this operation.
    meta_temp_url_key = resource.Header("x-account-meta-temp-url-key")
    #: A second secret key value for temporary URLs. If not set,
    #: this header is not returned by this operation.
    meta_temp_url_key_2 = resource.Header("x-account-meta-temp-url-key-2")
    #: The timestamp of the transaction.
    timestamp = resource.Header("x-timestamp")

    has_body = False
    requires_id = False

    def set_temp_url_key(self, proxy, key, secondary=False):
        """Set the temporary url key for the account.

        :param proxy: The proxy to use for making this request.
        :type proxy: :class:`~openstack.proxy.Proxy`
        :param key:
          Text of the key to use.
        :param bool secondary:
          Whether this should set the secondary key. (defaults to False)
        """
        header = 'Temp-URL-Key'
        if secondary:
            header += '-2'

        return self.set_metadata(proxy, {header: key})
