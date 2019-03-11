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

====================
Working with Actions
====================

An action is an abstraction of some logic that can be executed by a worker
thread. Most of the operations supported by Senlin are executed asynchronously,
which means they are queued into database and then picked up by certain worker
thread for execution.


List Actions
~~~~~~~~~~~~

To examine the list of actions:

.. literalinclude:: ../../examples/clustering/action.py
   :pyobject: list_actions

When listing actions, you can specify the sorting option using the ``sort``
parameter and you can do pagination using the ``limit`` and ``marker``
parameters.

Full example: `manage action`_


Get Action
~~~~~~~~~~

To get a action based on its name or ID:

.. literalinclude:: ../../examples/clustering/action.py
   :pyobject: get_action

.. _manage action: https://opendev.org/openstack/openstacksdk/src/branch/master/examples/clustering/action.py
