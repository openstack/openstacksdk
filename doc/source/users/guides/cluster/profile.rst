..
  Licensed under the Apache License, Version 2.0 (the "License"); you may
  not use this file except in compliance with the License. You may obtain
  a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
  License for the specific language governing permissions and limitations
  under the License.

=================
Managing Profiles
=================

A **profile type**  can be treated as the meta-type of a `Profile` object. A
registry of profile types is built when the Cluster service starts. When
creating a `Profile` object, you will indicate the profile type used in its
`spec` property.


List Profiles
~~~~~~~~~~~~~

To examine the list of profiles:

.. literalinclude:: ../../examples/cluster/profile.py
   :pyobject: list_profiles

When listing profiles, you can specify the sorting option using the ``sort``
parameter and you can do pagination using the ``limit`` and ``marker``
parameters.

Full example: `manage profile`_


Create Profile
~~~~~~~~~~~~~~

When creating a profile, you will provide a dictionary with keys and values
specified according to the profile type referenced.

.. literalinclude:: ../../examples/cluster/profile.py
   :pyobject: create_profile

Optionally, you can specify a ``metadata`` keyword argument that contains some
key-value pairs to be associated with the profile.

Full example: `manage profile`_


Find Profile
~~~~~~~~~~~~

To find a profile based on its name or ID:

.. literalinclude:: ../../examples/cluster/profile.py
   :pyobject: find_profile

The Cluster service doesn't allow updating the ``spec`` of a profile. The only
way to achieve that is to create a new profile.

Full example: `manage profile`_


Get Profile
~~~~~~~~~~~~

To get a profile based on its name or ID:

.. literalinclude:: ../../examples/cluster/profile.py
   :pyobject: get_profile

Full example: `manage profile`_


Update Profile
~~~~~~~~~~~~~~

After a profile is created, most of its properties are immutable. Still, you
can update a profile's ``name`` and/or ``metadata``.

.. literalinclude:: ../../examples/cluster/profile.py
   :pyobject: update_profile

The Cluster service doesn't allow updating the ``spec`` of a profile. The only
way to achieve that is to create a new profile.

Full example: `manage profile`_


Delete Profile
~~~~~~~~~~~~~~

A profile can be deleted after creation, provided that it is not referenced
by any active clusters or nodes. If you attempt to delete a profile that is
still in use, you will get an error message.

.. literalinclude:: ../../examples/cluster/profile.py
   :pyobject: delete_profile


.. _manage profile: http://git.openstack.org/cgit/openstack/python-openstacksdk/tree/examples/cluster/profile.py
