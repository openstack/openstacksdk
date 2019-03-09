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
Managing Policies
=================

A **policy type**  can be treated as the meta-type of a `Policy` object. A
registry of policy types is built when the Cluster service starts. When
creating a `Policy` object, you will indicate the policy type used in its
`spec` property.


List Policies
~~~~~~~~~~~~~

To examine the list of policies:

.. literalinclude:: ../../examples/clustering/policy.py
   :pyobject: list_policies

When listing policies, you can specify the sorting option using the ``sort``
parameter and you can do pagination using the ``limit`` and ``marker``
parameters.

Full example: `manage policy`_


Create Policy
~~~~~~~~~~~~~

When creating a policy, you will provide a dictionary with keys and values
according to the policy type referenced.

.. literalinclude:: ../../examples/clustering/policy.py
   :pyobject: create_policy

Optionally, you can specify a ``metadata`` keyword argument that contains some
key-value pairs to be associated with the policy.

Full example: `manage policy`_


Find Policy
~~~~~~~~~~~

To find a policy based on its name or ID:

.. literalinclude:: ../../examples/clustering/policy.py
   :pyobject: find_policy

Full example: `manage policy`_


Get Policy
~~~~~~~~~~

To get a policy based on its name or ID:

.. literalinclude:: ../../examples/clustering/policy.py
   :pyobject: get_policy

Full example: `manage policy`_


Update Policy
~~~~~~~~~~~~~

After a policy is created, most of its properties are immutable. Still, you
can update a policy's ``name`` and/or ``metadata``.

.. literalinclude:: ../../examples/clustering/policy.py
   :pyobject: update_policy

The Cluster service doesn't allow updating the ``spec`` of a policy. The only
way to achieve that is to create a new policy.

Full example: `manage policy`_


Delete Policy
~~~~~~~~~~~~~

A policy can be deleted after creation, provided that it is not referenced
by any active clusters or nodes. If you attempt to delete a policy that is
still in use, you will get an error message.

.. literalinclude:: ../../examples/clustering/policy.py
   :pyobject: delete_policy


.. _manage policy: https://opendev.org/openstack/openstacksdk/src/branch/master/examples/clustering/policy.py
