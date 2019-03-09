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

==========================
Working with Profile Types
==========================

A **profile** is a template used to create and manage nodes, i.e. objects
exposed by other OpenStack services. A profile encodes the information needed
for node creation in a property named ``spec``.


List Profile Types
~~~~~~~~~~~~~~~~~~

To examine the known profile types:

.. literalinclude:: ../../examples/clustering/profile_type.py
   :pyobject: list_profile_types

Full example: `manage profile type`_


Get Profile Type
~~~~~~~~~~~~~~~~

To get the details about a profile type, you need to provide the name of it.

.. literalinclude:: ../../examples/clustering/profile_type.py
   :pyobject: get_profile_type

Full example: `manage profile type`_

.. _manage profile type: https://opendev.org/openstack/openstacksdk/src/branch/master/examples/clustering/profile_type.py
