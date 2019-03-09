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

=========================
Working with Policy Types
=========================

A **policy** is a template that encodes the information needed for specifying
the rules that are checked/enforced before/after certain actions are performed
on a cluster. The rules are encoded in a property named ``spec``.


List Policy Types
~~~~~~~~~~~~~~~~~

To examine the known policy types:

.. literalinclude:: ../../examples/clustering/policy_type.py
   :pyobject: list_policy_types

Full example: `manage policy type`_


Get Policy Type
~~~~~~~~~~~~~~~

To retrieve the details about a policy type, you need to provide the name of
it.

.. literalinclude:: ../../examples/clustering/policy_type.py
   :pyobject: get_policy_type

Full example: `manage policy type`_

.. _manage policy type: https://opendev.org/openstack/openstacksdk/src/branch/master/examples/clustering/policy_type.py
