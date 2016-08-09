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

import hashlib

from openstack import exceptions
from openstack.image import image_service
from openstack import resource2
from openstack import utils


class Image(resource2.Resource):
    resources_key = 'images'
    base_path = '/images'
    service = image_service.ImageService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True
    patch_update = True

    _query_mapping = resource2.QueryParameters("name", "visibility",
                                               "member_status", "owner",
                                               "status", "size_min",
                                               "size_max", "sort_key",
                                               "sort_dir", "sort", "tag",
                                               "created_at", "updated_at")

    # NOTE: Do not add "self" support here. If you've used Python before,
    # you know that self, while not being a reserved word, has special
    # meaning. You can't call a class initializer with the self name
    # as the first argument and then additionally in kwargs, as we
    # do when we're constructing instances from the JSON body.
    # Resource.list explicitly pops off any "self" keys from bodies so
    # that we don't end up getting the following:
    # TypeError: __init__() got multiple values for argument 'self'

    # The image data (bytes or a file-like object)
    data = None
    # Properties
    #: Hash of the image data used. The Image service uses this value
    #: for verification.
    checksum = resource2.Body('checksum')
    #: The container format refers to whether the VM image is in a file
    #: format that also contains metadata about the actual VM.
    #: Container formats include OVF and Amazon AMI. In addition,
    #: a VM image might not have a container format - instead,
    #: the image is just a blob of unstructured data.
    container_format = resource2.Body('container_format')
    #: The date and time when the image was created.
    created_at = resource2.Body('created_at')
    #: Valid values are: aki, ari, ami, raw, iso, vhd, vdi, qcow2, or vmdk.
    #: The disk format of a VM image is the format of the underlying
    #: disk image. Virtual appliance vendors have different formats
    #: for laying out the information contained in a VM disk image.
    disk_format = resource2.Body('disk_format')
    #: Defines whether the image can be deleted.
    #: *Type: bool*
    is_protected = resource2.Body('protected', type=bool)
    #: The minimum disk size in GB that is required to boot the image.
    min_disk = resource2.Body('min_disk')
    #: The minimum amount of RAM in MB that is required to boot the image.
    min_ram = resource2.Body('min_ram')
    #: The name of the image.
    name = resource2.Body('name')
    #: The ID of the owner, or project, of the image.
    owner_id = resource2.Body('owner')
    #: Properties, if any, that are associated with the image.
    properties = resource2.Body('properties', type=dict)
    #: The size of the image data, in bytes.
    size = resource2.Body('size', type=int)
    #: When present, Glance will attempt to store the disk image data in the
    #: backing store indicated by the value of the header. When not present,
    #: Glance will store the disk image data in the backing store that is
    #: marked default. Valid values are: file, s3, rbd, swift, cinder,
    #: gridfs, sheepdog, or vsphere.
    store = resource2.Body('store')
    #: The image status.
    status = resource2.Body('status')
    #: Tags, if any, that are associated with the image.
    tags = resource2.Body('tags')
    #: The date and time when the image was updated.
    updated_at = resource2.Body('updated_at')
    #: The virtual size of the image.
    virtual_size = resource2.Body('virtual_size')
    #: The image visibility.
    visibility = resource2.Body('visibility')
    #: The URL for the virtual machine image file.
    file = resource2.Body('file')
    #: A list of URLs to access the image file in external store.
    #: This list appears if the show_multiple_locations option is set
    #: to true in the Image service's configuration file.
    locations = resource2.Body('locations')
    #: The URL to access the image file kept in external store. It appears
    #: when you set the show_image_direct_url option to true in the
    #: Image service's configuration file.
    direct_url = resource2.Body('direct_url')
    #: An image property.
    path = resource2.Body('path')
    #: Value of image property used in add or replace operations expressed
    #: in JSON notation. For example, you must enclose strings in quotation
    #: marks, and you do not enclose numeric values in quotation marks.
    value = resource2.Body('value')
    #: The URL to access the image file kept in external store.
    url = resource2.Body('url')
    #: The location metadata.
    metadata = resource2.Body('metadata', type=dict)

    def _action(self, session, action):
        """Call an action on an image ID."""
        url = utils.urljoin(self.base_path, self.id, 'actions', action)
        return session.post(url, endpoint_filter=self.service)

    def deactivate(self, session):
        """Deactivate an image

        Note: Only administrative users can view image locations
        for deactivated images.
        """
        self._action(session, "deactivate")

    def reactivate(self, session):
        """Reactivate an image

        Note: The image must exist in order to be reactivated.
        """
        self._action(session, "reactivate")

    def add_tag(self, session, tag):
        """Add a tag to an image"""
        url = utils.urljoin(self.base_path, self.id, 'tags', tag)
        session.put(url, endpoint_filter=self.service)

    def remove_tag(self, session, tag):
        """Remove a tag from an image"""
        url = utils.urljoin(self.base_path, self.id, 'tags', tag)
        session.delete(url, endpoint_filter=self.service)

    def upload(self, session):
        """Upload data into an existing image"""
        url = utils.urljoin(self.base_path, self.id, 'file')
        session.put(url, endpoint_filter=self.service, data=self.data,
                    headers={"Content-Type": "application/octet-stream",
                             "Accept": ""})

    def download(self, session):
        """Download the data contained in an image"""
        # TODO(briancurtin): This method should probably offload the get
        # operation into another thread or something of that nature.
        url = utils.urljoin(self.base_path, self.id, 'file')
        resp = session.get(url, endpoint_filter=self.service)

        checksum = resp.headers["Content-MD5"]
        digest = hashlib.md5(resp.content).hexdigest()
        if digest != checksum:
            raise exceptions.InvalidResponse("checksum mismatch")

        return resp.content
