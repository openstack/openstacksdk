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

from openstack.common import tag
from openstack import exceptions
from openstack import resource
from openstack import utils


class NetworkResource(resource.Resource):
    #: Revision number of the resource. *Type: int*
    revision_number = resource.Body('revision_number', type=int)

    # Headers for HEAD and GET requests
    #: See http://www.ietf.org/rfc/rfc2616.txt.
    if_match = resource.Header("if-match", type=list)

    _allow_unknown_attrs_in_body = True

    def _prepare_request(
        self,
        requires_id=None,
        prepend_key=False,
        patch=False,
        base_path=None,
        params=None,
        **kwargs,
    ):
        req = super()._prepare_request(
            requires_id=requires_id,
            prepend_key=prepend_key,
            patch=patch,
            base_path=base_path,
            params=params,
            **kwargs,
        )
        return req


class TagMixinNetwork(tag.TagMixin):
    def add_tags(self, session, tags):
        """Create the tags on the resource

        :param session: The session to use for making this request.
        :param tags: List with tags to be set on the resource
        """
        tags = tags or []
        url = utils.urljoin(self.base_path, self.id, 'tags')
        session = self._get_session(session)
        response = session.post(url, json={'tags': tags})
        exceptions.raise_from_response(response)
        self._body.attributes.update({'tags': tags})
        return self
