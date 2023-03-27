Data Model
==========

*openstacksdk* has a very strict policy on not breaking backwards compatibility
ever. However, with the data structures returned from OpenStack, there are
places where the resource structures from OpenStack are returned to the user
somewhat directly, leaving an openstacksdk user open to changes/differences in
result content.

To combat that, openstacksdk 'normalizes' the return structure from OpenStack
in many places, and the results of that normalization are listed below. Where
openstacksdk performs normalization, a user can count on any fields declared in
the docs as being completely safe to use - they are as much a part of
openstacksdk's API contract as any other Python method.

Some OpenStack objects allow for arbitrary attributes at the root of the
object. openstacksdk will pass those through so as not to break anyone who may
be counting on them, but as they are arbitrary openstacksdk can make no
guarantees as to their existence. As part of normalization, openstacksdk will
put any attribute from an OpenStack resource that is not in its data model
contract into an attribute called 'properties'. The contents of properties are
defined to be an arbitrary collection of key value pairs with no promises as to
any particular key ever existing.

If a user passes ``strict=True`` to the openstacksdk constructor, openstacksdk
will not pass through arbitrary objects to the root of the resource, and will
instead only put them in the properties dict. If a user is worried about
accidentally writing code that depends on an attribute that is not part of the
API contract, this can be a useful tool. Keep in mind all data can still be
accessed via the properties dict, but any code touching anything in the
properties dict should be aware that the keys found there are highly user/cloud
specific. Any key that is transformed as part of the openstacksdk data model
contract will not wind up with an entry in properties - only keys that are
unknown.

The ``location`` field
----------------------

A Location defines where a resource lives. It includes a cloud name and a
region name, an availability zone as well as information about the project
that owns the resource.

The project information may contain a project ID, or a combination of one or
more of a project name with a domain name or ID. If a project ID is present,
it should be considered correct.

Some resources do not carry ownership information with them. For those, the
project information will be filled in from the project the user currently
has a token for.

Some resources do not have information about availability zones, or may exist
region wide. Those resources will have None as their availability zone.

.. code-block:: python

   Location = dict(
       cloud=str(),
       region_name=str(),
       zone=str() or None,
       project=dict(
           id=str() or None,
           name=str() or None,
           domain_id=str() or None,
           domain_name=str() or None,
       )
   )
