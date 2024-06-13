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

from openstack import exceptions
from openstack.image import _download
from openstack import resource


class Image(resource.Resource, _download.DownloadMixin):
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

    _query_mapping = resource.QueryParameters(
        'name',
        'container_format',
        'disk_format',
        'status',
        'size_min',
        'size_max',
    )

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
    owner = resource.Body('owner', alias='owner_id')
    #: The ID of the owner, or project, of the image. (backwards compat)
    owner_id = resource.Body('owner', alias='owner')
    #: Properties, if any, that are associated with the image.
    properties = resource.Body('properties')
    #: The size of the image data, in bytes.
    size = resource.Body('size')
    #: The image status.
    status = resource.Body('status')
    #: The timestamp when this image was last updated.
    updated_at = resource.Body('updated_at')

    @classmethod
    def find(cls, session, name_or_id, ignore_missing=True, **params):
        """Find a resource by its name or id.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param name_or_id: This resource's identifier, if needed by
                           the request. The default is ``None``.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.NotFoundException` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict params: Any additional parameters to be passed into
                            underlying methods, such as to
                            :meth:`~openstack.resource.Resource.existing`
                            in order to pass on URI parameters.

        :return: The :class:`Resource` object matching the given name or id
                 or None if nothing matches.
        :raises: :class:`openstack.exceptions.DuplicateResource` if more
                 than one resource is found for this request.
        :raises: :class:`openstack.exceptions.NotFoundException` if nothing
                 is found and ignore_missing is ``False``.
        """
        session = cls._get_session(session)
        # Try to short-circuit by looking directly for a matching ID.
        try:
            match = cls.existing(
                id=name_or_id,
                connection=session._get_connection(),
                **params,
            )
            return match.fetch(session, **params)
        except exceptions.NotFoundException:
            pass

        params['name'] = name_or_id

        data = cls.list(session, base_path='/images/detail', **params)

        result = cls._get_one_match(name_or_id, data)
        if result is not None:
            return result

        if ignore_missing:
            return None
        raise exceptions.NotFoundException(
            f"No {cls.__name__} found for {name_or_id}"
        )
