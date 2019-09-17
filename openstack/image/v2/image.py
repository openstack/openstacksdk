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
from openstack import utils


class Image(resource.Resource, resource.TagMixin, _download.DownloadMixin):
    resources_key = 'images'
    base_path = '/images'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    commit_method = 'PATCH'
    commit_jsonpatch = True

    # Store all unknown attributes under 'properties' in the object.
    # Remotely they would be still in the resource root
    _store_unknown_attrs_as_properties = True

    _query_mapping = resource.QueryParameters(
        "name", "visibility",
        "member_status", "owner",
        "status", "size_min", "size_max",
        "protected", "is_hidden",
        "sort_key", "sort_dir", "sort", "tag",
        "created_at", "updated_at",
        is_hidden="os_hidden")

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
    checksum = resource.Body('checksum')
    #: The container format refers to whether the VM image is in a file
    #: format that also contains metadata about the actual VM.
    #: Container formats include OVF and Amazon AMI. In addition,
    #: a VM image might not have a container format - instead,
    #: the image is just a blob of unstructured data.
    container_format = resource.Body('container_format')
    #: The date and time when the image was created.
    created_at = resource.Body('created_at')
    #: Valid values are: aki, ari, ami, raw, iso, vhd, vdi, qcow2, or vmdk.
    #: The disk format of a VM image is the format of the underlying
    #: disk image. Virtual appliance vendors have different formats
    #: for laying out the information contained in a VM disk image.
    disk_format = resource.Body('disk_format')
    #: This field controls whether an image is displayed in the default
    #: image-list response
    is_hidden = resource.Body('os_hidden', type=bool)
    #: Defines whether the image can be deleted.
    #: *Type: bool*
    is_protected = resource.Body('protected', type=bool)
    #: The algorithm used to compute a secure hash of the image data
    #: for this image
    hash_algo = resource.Body('os_hash_algo')
    #: The hexdigest of the secure hash of the image data computed using
    #: the algorithm whose name is the value of the os_hash_algo property.
    hash_value = resource.Body('os_hash_value')
    #: The minimum disk size in GB that is required to boot the image.
    min_disk = resource.Body('min_disk')
    #: The minimum amount of RAM in MB that is required to boot the image.
    min_ram = resource.Body('min_ram')
    #: The name of the image.
    name = resource.Body('name')
    #: The ID of the owner, or project, of the image.
    owner_id = resource.Body('owner')
    # TODO(mordred) This is not how this works in v2. I mean, it's how it
    # should work, but it's not. We need to fix properties. They work right
    # in shade, so we can draw some logic from there.
    #: Properties, if any, that are associated with the image.
    properties = resource.Body('properties')
    #: The size of the image data, in bytes.
    size = resource.Body('size', type=int)
    #: When present, Glance will attempt to store the disk image data in the
    #: backing store indicated by the value of the header. When not present,
    #: Glance will store the disk image data in the backing store that is
    #: marked default. Valid values are: file, s3, rbd, swift, cinder,
    #: gridfs, sheepdog, or vsphere.
    store = resource.Body('store')
    #: The image status.
    status = resource.Body('status')
    #: The date and time when the image was updated.
    updated_at = resource.Body('updated_at')
    #: The virtual size of the image.
    virtual_size = resource.Body('virtual_size')
    #: The image visibility.
    visibility = resource.Body('visibility')
    #: The URL for the virtual machine image file.
    file = resource.Body('file')
    #: A list of URLs to access the image file in external store.
    #: This list appears if the show_multiple_locations option is set
    #: to true in the Image service's configuration file.
    locations = resource.Body('locations')
    #: The URL to access the image file kept in external store. It appears
    #: when you set the show_image_direct_url option to true in the
    #: Image service's configuration file.
    direct_url = resource.Body('direct_url')
    #: The URL to access the image file kept in external store.
    url = resource.Body('url')
    #: The location metadata.
    metadata = resource.Body('metadata', type=dict)

    # Additional Image Properties
    # https://docs.openstack.org/glance/latest/user/common-image-properties.html
    # http://docs.openstack.org/cli-reference/glance-property-keys.html
    #: The CPU architecture that must be supported by the hypervisor.
    architecture = resource.Body("architecture")
    #: The hypervisor type. Note that qemu is used for both QEMU and
    #: KVM hypervisor types.
    hypervisor_type = resource.Body("hypervisor_type")
    #: Optional property allows created servers to have a different bandwidth
    #: cap than that defined in the network they are attached to.
    instance_type_rxtx_factor = resource.Body(
        "instance_type_rxtx_factor", type=float)
    # For snapshot images, this is the UUID of the server used to
    #: create this image.
    instance_uuid = resource.Body('instance_uuid')
    #: Specifies whether the image needs a config drive.
    #: `mandatory` or `optional` (default if property is not used).
    needs_config_drive = resource.Body('img_config_drive')
    #: The ID of an image stored in the Image service that should be used
    #: as the kernel when booting an AMI-style image.
    kernel_id = resource.Body('kernel_id')
    #: The common name of the operating system distribution in lowercase
    os_distro = resource.Body('os_distro')
    #: The operating system version as specified by the distributor.
    os_version = resource.Body('os_version')
    #: Secure Boot is a security standard. When the instance starts,
    #: Secure Boot first examines software such as firmware and OS by
    #: their signature and only allows them to run if the signatures are valid.
    needs_secure_boot = resource.Body('os_secure_boot')
    #: Time for graceful shutdown
    os_shutdown_timeout = resource.Body('os_shutdown_timeout', type=int)
    #: The ID of image stored in the Image service that should be used as
    #: the ramdisk when booting an AMI-style image.
    ramdisk_id = resource.Body('ramdisk_id')
    #: The virtual machine mode. This represents the host/guest ABI
    #: (application binary interface) used for the virtual machine.
    vm_mode = resource.Body('vm_mode')
    #: The preferred number of sockets to expose to the guest.
    hw_cpu_sockets = resource.Body('hw_cpu_sockets', type=int)
    #: The preferred number of cores to expose to the guest.
    hw_cpu_cores = resource.Body('hw_cpu_cores', type=int)
    #: The preferred number of threads to expose to the guest.
    hw_cpu_threads = resource.Body('hw_cpu_threads', type=int)
    #: Specifies the type of disk controller to attach disk devices to.
    #: One of scsi, virtio, uml, xen, ide, or usb.
    hw_disk_bus = resource.Body('hw_disk_bus')
    #: Used to pin the virtual CPUs (vCPUs) of instances to the
    #: host's physical CPU cores (pCPUs).
    hw_cpu_policy = resource.Body('hw_cpu_policy')
    #: Defines how hardware CPU threads in a simultaneous
    #: multithreading-based (SMT) architecture be used.
    hw_cpu_thread_policy = resource.Body('hw_cpu_thread_policy')
    #: Adds a random-number generator device to the image's instances.
    hw_rng_model = resource.Body('hw_rng_model')
    #: For libvirt: Enables booting an ARM system using the specified
    #: machine type.
    #: For Hyper-V: Specifies whether the Hyper-V instance will be a
    #: generation 1 or generation 2 VM.
    hw_machine_type = resource.Body('hw_machine_type')
    #: Enables the use of VirtIO SCSI (virtio-scsi) to provide block device
    #: access for compute instances; by default, instances use VirtIO Block
    #: (virtio-blk).
    hw_scsi_model = resource.Body('hw_scsi_model')
    #: Specifies the count of serial ports that should be provided.
    hw_serial_port_count = resource.Body('hw_serial_port_count', type=int)
    #: The video image driver used.
    hw_video_model = resource.Body('hw_video_model')
    #: Maximum RAM for the video image.
    hw_video_ram = resource.Body('hw_video_ram', type=int)
    #: Enables a virtual hardware watchdog device that carries out the
    #: specified action if the server hangs.
    hw_watchdog_action = resource.Body('hw_watchdog_action')
    #: The kernel command line to be used by the libvirt driver, instead
    #: of the default.
    os_command_line = resource.Body('os_command_line')
    #: Specifies the model of virtual network interface device to use.
    hw_vif_model = resource.Body('hw_vif_model')
    #: If true, this enables the virtio-net multiqueue feature.
    #: In this case, the driver sets the number of queues equal to the
    #: number of guest vCPUs. This makes the network performance scale
    #: across a number of vCPUs.
    is_hw_vif_multiqueue_enabled = resource.Body(
        'hw_vif_multiqueue_enabled', type=bool)
    #: If true, enables the BIOS bootmenu.
    is_hw_boot_menu_enabled = resource.Body('hw_boot_menu', type=bool)
    #: The virtual SCSI or IDE controller used by the hypervisor.
    vmware_adaptertype = resource.Body('vmware_adaptertype')
    #: A VMware GuestID which describes the operating system installed
    #: in the image.
    vmware_ostype = resource.Body('vmware_ostype')
    #: If true, the root partition on the disk is automatically resized
    #: before the instance boots.
    has_auto_disk_config = resource.Body('auto_disk_config')
    #: The operating system installed on the image.
    os_type = resource.Body('os_type')
    #: The operating system admin username.
    os_admin_user = resource.Body('os_admin_user')
    #: If true, QEMU guest agent will be exposed to the instance.
    hw_qemu_guest_agent = resource.Body('hw_qemu_guest_agent', type=bool)
    #: If true, require quiesce on snapshot via QEMU guest agent.
    os_require_quiesce = resource.Body('os_require_quiesce', type=bool)
    #: The URL for the schema describing a virtual machine image.
    schema = resource.Body('schema')

    def _action(self, session, action):
        """Call an action on an image ID."""
        url = utils.urljoin(self.base_path, self.id, 'actions', action)
        return session.post(url,)

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

    def upload(self, session):
        """Upload data into an existing image"""
        url = utils.urljoin(self.base_path, self.id, 'file')
        return session.put(url, data=self.data,
                           headers={"Content-Type": "application/octet-stream",
                                    "Accept": ""})

    def stage(self, session):
        """Stage binary image data into an existing image"""
        url = utils.urljoin(self.base_path, self.id, 'stage')
        response = session.put(
            url, data=self.data,
            headers={"Content-Type": "application/octet-stream",
                     "Accept": ""})
        self._translate_response(response, has_body=False)
        return self

    def import_image(self, session, method='glance-direct', uri=None,
                     store=None):
        """Import Image via interoperable image import process"""
        url = utils.urljoin(self.base_path, self.id, 'import')
        json = {'method': {'name': method}}
        if uri:
            if method == 'web-download':
                json['method']['uri'] = uri
            elif method == 'glance-direct':
                json['method']['uri'] = uri
            else:
                raise exceptions.InvalidRequest('URI is only supported with '
                                                'method: "web-download"')
        headers = {}
        if store is not None:
            headers = {'X-Image-Meta-Store': store.id}
        session.post(url, json=json, headers=headers)

    def _prepare_request(self, requires_id=None, prepend_key=False,
                         patch=False, base_path=None):
        request = super(Image, self)._prepare_request(requires_id=requires_id,
                                                      prepend_key=prepend_key,
                                                      patch=patch,
                                                      base_path=base_path)
        if patch:
            headers = {
                'Content-Type': 'application/openstack-images-v2.1-json-patch',
                'Accept': ''
            }
            request.headers.update(headers)

        return request

    @classmethod
    def find(cls, session, name_or_id, ignore_missing=True, **params):
        # Do a regular search first (ignoring missing)
        result = super(Image, cls).find(session, name_or_id, True,
                                        **params)

        if result:
            return result
        else:
            # Search also in hidden images
            params['is_hidden'] = True
            data = cls.list(session, **params)

            result = cls._get_one_match(name_or_id, data)
            if result is not None:
                return result

        if ignore_missing:
            return None
        raise exceptions.ResourceNotFound(
            "No %s found for %s" % (cls.__name__, name_or_id))
