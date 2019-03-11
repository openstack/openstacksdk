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

===================
Working with Events
===================

An event is a record generated during engine execution. Such an event
captures what has happened inside the senlin-engine. The senlin-engine service
generates event records when it is performing some actions or checking
policies.


List Events
~~~~~~~~~~~

To examine the list of events:

.. literalinclude:: ../../examples/clustering/event.py
   :pyobject: list_events

When listing events, you can specify the sorting option using the ``sort``
parameter and you can do pagination using the ``limit`` and ``marker``
parameters.

Full example: `manage event`_


Get Event
~~~~~~~~~

To get a event based on its name or ID:

.. literalinclude:: ../../examples/clustering/event.py
   :pyobject: get_event

.. _manage event: https://opendev.org/openstack/openstacksdk/src/branch/master/examples/clustering/event.py
