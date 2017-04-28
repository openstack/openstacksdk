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

from openstack import utils


class TagMixin(object):

    _tag_query_parameters = {
        'tags': 'tags',
        'any_tags': 'tags-any',
        'not_tags': 'not-tags',
        'not_any_tags': 'not-tags-any',
    }

    def set_tags(self, session, tags):
        url = utils.urljoin(self.base_path, self.id, 'tags')
        session.put(url, endpoint_filter=self.service,
                    json={'tags': tags})
        self._body.attributes.update({'tags': tags})
        return self
