==========
Data Model
==========

shade has a very strict policy on not breaking backwards compatability ever.
However, with the data structures returned from OpenStack, there are places
where the resource structures from OpenStack are returned to the user somewhat
directly, leaving a shade user open to changes/differences in result content.

To combat that, shade 'normalizes' the return structure from OpenStack in many
places, and the results of that normalization are listed below. Where shade
performs normalization, a user can count on any fields declared in the docs
as being completely safe to use - they are as much a part of shade's API
contract as any other Python method.

Some OpenStack objects allow for arbitrary attributes at
the root of the object. shade will pass those through so as not to break anyone
who may be counting on them, but as they are arbitrary shade can make no
guarantees as to their existence. As part of normalization, shade will put any
attribute from an OpenStack resource that is not in its data model contract
into an attribute called 'properties'. The contents of properties are
defined to be an arbitrary collection of key value pairs with no promises as
to any particular key ever existing.

If a user passes `strict=True` to the shade constructor, shade will not pass
through arbitrary objects to the root of the resource, and will instead only
put them in the properties dict. If a user is worried about accidentally
writing code that depends on an attribute that is not part of the API contract,
this can be a useful tool. Keep in mind all data can still be accessed via
the properties dict, but any code touching anything in the properties dict
should be aware that the keys found there are highly user/cloud specific.
Any key that is transformed as part of the shade data model contract will
not wind up with an entry in properties - only keys that are unknown.

Location
--------

A Location defines where a resource lives. It includes a cloud name and a
region name, an availability zone as well as information about the project
that owns the resource.

The project information may contain a project id, or a combination of one or
more of a project name with a domain name or id. If a project id is present,
it should be considered correct.

Some resources do not carry ownership information with them. For those, the
project information will be filled in from the project the user currently
has a token for.

Some resources do not have information about availability zones, or may exist
region wide. Those resources will have None as their availability zone.

If all of the project information is None, then

.. code-block:: python

  Location = dict(
    cloud=str(),
    region=str(),
    zone=str() or None,
    project=dict(
      id=str() or None,
      name=str() or None,
      domain_id=str() or None,
      domain_name=str() or None))


Flavor
------

A flavor for a Nova Server.

.. code-block:: python

  Flavor = dict(
    location=Location(),
    id=str(),
    name=str(),
    is_public=bool(),
    is_disabled=bool(),
    ram=int(),
    vcpus=int(),
    disk=int(),
    ephemeral=int(),
    swap=int(),
    rxtx_factor=float(),
    extra_specs=dict(),
    properties=dict())


Flavor Access
------

An access entry for a Nova Flavor.

.. code-block:: python

  FlavorAccess = dict(
    flavor_id=str(),
    project_id=str())


Image
-----

A Glance Image.

.. code-block:: python

  Image = dict(
    location=Location(),
    id=str(),
    name=str(),
    min_ram=int(),
    min_disk=int(),
    size=int(),
    virtual_size=int(),
    container_format=str(),
    disk_format=str(),
    checksum=str(),
    created_at=str(),
    updated_at=str(),
    owner=str(),
    is_public=bool(),
    is_protected=bool(),
    visibility=str(),
    status=str(),
    locations=list(),
    direct_url=str() or None,
    tags=list(),
    properties=dict())

Security Group
--------------

A Security Group from either Nova or Neutron

.. code-block:: python

  SecurityGroup = dict(
    location=Location(),
    id=str(),
    name=str(),
    description=str(),
    security_group_rules=list(),
    properties=dict())

Security Group Rule
-------------------

A Security Group Rule from either Nova or Neutron

.. code-block:: python

  SecurityGroupRule = dict(
    location=Location(),
    id=str(),
    direction=str(),  # oneof('ingress', 'egress')
    ethertype=str(),
    port_range_min=int() or None,
    port_range_max=int() or None,
    protocol=str() or None,
    remote_ip_prefix=str() or None,
    security_group_id=str() or None,
    remote_group_id=str() or None
    properties=dict())

Server
------

A Server from Nova

.. code-block:: python

  Server = dict(
    location=Location(),
    id=str(),
    name=str(),
    image=dict() or str(),
    flavor=dict(),
    volumes=list(),  # Volume
    interface_ip=str(),
    has_config_drive=bool(),
    accessIPv4=str(),
    accessIPv6=str(),
    addresses=dict(),  # string, list(Address)
    created=str(),
    key_name=str(),
    metadata=dict(),  # string, string
    private_v4=str(),
    progress=int(),
    public_v4=str(),
    public_v6=str(),
    security_groups=list(),  # SecurityGroup
    status=str(),
    updated=str(),
    user_id=str(),
    host_id=str() or None,
    power_state=str() or None,
    task_state=str() or None,
    vm_state=str() or None,
    launched_at=str() or None,
    terminated_at=str() or None,
    task_state=str() or None,
    properties=dict())

ComputeLimits
-------------

Limits and current usage for a project in Nova

.. code-block:: python

  ComputeLimits = dict(
    location=Location(),
    max_personality=int(),
    max_personality_size=int(),
    max_server_group_members=int(),
    max_server_groups=int(),
    max_server_meta=int(),
    max_total_cores=int(),
    max_total_instances=int(),
    max_total_keypairs=int(),
    max_total_ram_size=int(),
    total_cores_used=int(),
    total_instances_used=int(),
    total_ram_used=int(),
    total_server_groups_used=int(),
    properties=dict())

Floating IP
-----------

A Floating IP from Neutron or Nova


.. code-block:: python

  FloatingIP = dict(
    location=Location(),
    id=str(),
    description=str(),
    attached=bool(),
    fixed_ip_address=str() or None,
    floating_ip_address=str() or None,
    network=str() or None,
    port=str() or None,
    router=str(),
    status=str(),
    created_at=str() or None,
    updated_at=str() or None,
    revision_number=int() or None,
    properties=dict())

Project
-------

A Project from Keystone (or a tenant if Keystone v2)

Location information for Project has some specific semantics.

If the project has a parent project, that will be in location.project.id,
and if it doesn't that should be None. If the Project is associated with
a domain that will be in location.project.domain_id regardless of the current
user's token scope. location.project.name and location.project.domain_name
will always be None. Finally, location.region_name will always be None as
Projects are global to a cloud. If a deployer happens to deploy OpenStack
in such a way that users and projects are not shared amongst regions, that
necessitates treating each of those regions as separate clouds from shade's
POV.

.. code-block:: python

  Project = dict(
    location=Location(),
    id=str(),
    name=str(),
    description=str(),
    is_enabled=bool(),
    is_domain=bool(),
    properties=dict())

Volume
------

A volume from cinder.

.. code-block:: python

  Volume = dict(
    location=Location(),
    id=str(),
    name=str(),
    description=str(),
    size=int(),
    attachments=list(),
    status=str(),
    migration_status=str() or None,
    host=str() or None,
    replication_driver=str() or None,
    replication_status=str() or None,
    replication_extended_status=str() or None,
    snapshot_id=str() or None,
    created_at=str(),
    updated_at=str() or None,
    source_volume_id=str() or None,
    consistencygroup_id=str() or None,
    volume_type=str() or None,
    metadata=dict(),
    is_bootable=bool(),
    is_encrypted=bool(),
    can_multiattach=bool(),
    properties=dict())


VolumeType
------

A volume type from cinder.

.. code-block:: python

  VolumeType = dict(
    location=Location(),
    id=str(),
    name=str(),
    description=str() or None,
    is_public=bool(),
    qos_specs_id=str() or None,
    extra_specs=dict(),
    properties=dict())


VolumeTypeAccess
------

A volume type access from cinder.

.. code-block:: python

  VolumeTypeAccess = dict(
    location=Location(),
    volume_type_id=str(),
    project_id=str(),
    properties=dict())
