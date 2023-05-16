# Copyright 2026 Red Hat Inc.
# All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

from openstack import resource


class ImageLocation(resource.Resource):
    base_path = '/images/%(image_id)s/locations'

    allow_create = True
    allow_list = True

    # Note: Glance does not support microversions. This attribute is used
    # by the SDK framework to indicate the latest API capability level
    # required for this feature. The location import API requires Glance
    # API v2 with feature capability detection indicating support for
    # location management (typically available in API v2.17+).
    _max_microversion = '2.17'

    #: Image ID stored through the image API. Typically a UUID.
    image_id = resource.URI('image_id')
    #: The Location URL to access the image from external store.
    url = resource.Body('url')
    #: Optional checksum/hash fields for location validation (Glance API).
    validation_data = resource.Body('validation_data', type=dict)
    #: The location metadata.
    metadata = resource.Body('metadata', type=dict)
