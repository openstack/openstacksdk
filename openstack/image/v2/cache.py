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


class CachedImage(resource.Resource):
    image_id = resource.Body('image_id')
    hits = resource.Body('hits')
    last_accessed = resource.Body('last_accessed')
    last_modified = resource.Body('last_modified')
    size = resource.Body('size')


class Cache(resource.Resource):
    base_path = '/cache'

    allow_fetch = True
    allow_delete = True

    _max_microversion = '2.14'

    cached_images = resource.Body('cached_images', type=list,
                                  list_type=CachedImage)
    queued_images = resource.Body('queued_images', type=list)
