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
from openstack import resource


class NetworkResource(resource.Resource):
    #: Revision number of the resource. *Type: int*
    revision_number = resource.Body('revision_number', type=int)

    def _prepare_request(self, requires_id=None, prepend_key=False,
                         patch=False, base_path=None, params=None,
                         if_revision=None, **kwargs):
        req = super(NetworkResource, self)._prepare_request(
            requires_id=requires_id, prepend_key=prepend_key, patch=patch,
            base_path=base_path, params=params)
        if if_revision is not None:
            req.headers['If-Match'] = "revision_number=%d" % if_revision
        return req
