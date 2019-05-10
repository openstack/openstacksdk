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
import io
import six

from openstack import exceptions
from openstack import resource
from openstack import utils


class Image(resource.Resource):
    resource_key = 'image'
    resources_key = 'images'
    base_path = '/images'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    # Store all unknown attributes under 'properties' in the object.
    # Remotely they would be still in the resource root
    _store_unknown_attrs_as_properties = True

    #: Hash of the image data used. The Image service uses this value
    #: for verification.
    checksum = resource.Body('checksum')
    #: The container format refers to whether the VM image is in a file
    #: format that also contains metadata about the actual VM.
    #: Container formats include OVF and Amazon AMI. In addition,
    #: a VM image might not have a container format - instead,
    #: the image is just a blob of unstructured data.
    container_format = resource.Body('container_format')
    #: A URL to copy an image from
    copy_from = resource.Body('copy_from')
    #: The timestamp when this image was created.
    created_at = resource.Body('created_at')
    #: Valid values are: aki, ari, ami, raw, iso, vhd, vdi, qcow2, or vmdk.
    #: The disk format of a VM image is the format of the underlying
    #: disk image. Virtual appliance vendors have different formats for
    #: laying out the information contained in a VM disk image.
    disk_format = resource.Body('disk_format')
    #: Defines whether the image can be deleted.
    #: *Type: bool*
    is_protected = resource.Body('protected', type=bool)
    #: ``True`` if this is a public image.
    #: *Type: bool*
    is_public = resource.Body('is_public', type=bool)
    #: A location for the image identified by a URI
    location = resource.Body('location')
    #: The minimum disk size in GB that is required to boot the image.
    min_disk = resource.Body('min_disk')
    #: The minimum amount of RAM in MB that is required to boot the image.
    min_ram = resource.Body('min_ram')
    #: Name for the image. Note that the name of an image is not unique
    #: to a Glance node. The API cannot expect users to know the names
    #: of images owned by others.
    name = resource.Body('name')
    #: The ID of the owner, or project, of the image.
    owner_id = resource.Body('owner')
    #: Properties, if any, that are associated with the image.
    properties = resource.Body('properties')
    #: The size of the image data, in bytes.
    size = resource.Body('size')
    #: The image status.
    status = resource.Body('status')
    #: The timestamp when this image was last updated.
    updated_at = resource.Body('updated_at')

    def download(self, session, stream=False, output=None, chunk_size=1024):
        """Download the data contained in an image"""
        # TODO(briancurtin): This method should probably offload the get
        # operation into another thread or something of that nature.
        url = utils.urljoin(self.base_path, self.id, 'file')
        resp = session.get(url, stream=stream)

        # See the following bug report for details on why the checksum
        # code may sometimes depend on a second GET call.
        # https://storyboard.openstack.org/#!/story/1619675
        checksum = resp.headers.get("Content-MD5")

        if checksum is None:
            # If we don't receive the Content-MD5 header with the download,
            # make an additional call to get the image details and look at
            # the checksum attribute.
            details = self.fetch(session)
            checksum = details.checksum

        if output:
            try:
                # In python 2 we might get StringIO - delete it as soon as
                # py2 support is dropped
                if isinstance(output, io.IOBase) \
                        or isinstance(output, six.StringIO):
                    for chunk in resp.iter_content(chunk_size=chunk_size):
                        output.write(chunk)
                else:
                    with open(output, 'wb') as fd:
                        for chunk in resp.iter_content(
                                chunk_size=chunk_size):
                            fd.write(chunk)
                return resp
            except Exception as e:
                raise exceptions.SDKException(
                    "Unable to download image: %s" % e)
        # if we are returning the repsonse object, ensure that it
        # has the content-md5 header so that the caller doesn't
        # need to jump through the same hoops through which we
        # just jumped.
        if stream:
            resp.headers['content-md5'] = checksum
            return resp

        if checksum is not None:
            digest = hashlib.md5(resp.content).hexdigest()
            if digest != checksum:
                raise exceptions.InvalidResponse(
                    "checksum mismatch: %s != %s" % (checksum, digest))
        else:
            session.log.warn(
                "Unable to verify the integrity of image %s" % (self.id))

        return resp
