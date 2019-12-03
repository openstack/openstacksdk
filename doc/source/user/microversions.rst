=============
Microversions
=============

As openstacksdk rolls out support for consuming microversions, it will do so
on a call by call basis as needed. Just like with major versions, openstacksdk
should have logic to handle each microversion for a given REST call it makes,
with the following rules in mind:

* If an activity openstack performs can be done differently or more efficiently
  with a new microversion, the support should be added to openstack.cloud and
  to the appropriate Proxy class.

* openstacksdk should always attempt to use the latest microversion it is aware
  of for a given call, unless a microversion removes important data.

* Microversion selection should under no circumstances be exposed to the user
  in python API calls in the Resource layer or the openstack.cloud layer.

* Microversion selection is exposed to the user in the REST layer via the
  ``microversion`` argument to each REST call.

* A user of the REST layer may set the default microversion by setting
  ``{service_type}_default_microversion`` in clouds.yaml or
  ``OS_{service_type|upper}_DEFAULT_MICROVERSION`` environment variable.

.. note::

  Setting the default microversion in any circumstance other than when using
  the REST layer is highly discouraged. Both of the higher layers in
  openstacksdk provide data normalization as well as logic about which REST
  call to make. Setting the default microversion could change the behavior
  of the service in question in such a way that openstacksdk does not
  understand. If there is a feature of a service that needs a microversion
  and it is not already transparently exposed in openstacksdk, please file
  a bug.

* If a feature is only exposed for a given microversion and cannot be simulated
  for older clouds without that microversion, it is ok to add it, but
  a clear error message should be given to the user that the given feature is
  not available on their cloud. (A message such as "This cloud supports
  a maximum microversion of XXX for service YYY and this feature only exists
  on clouds with microversion ZZZ. Please contact your cloud provider for
  information about when this feature might be available")

* When adding a feature that only exists behind a new microversion,
  every effort should be made to figure out how to provide the same
  functionality if at all possible, even if doing so is inefficient. If an
  inefficient workaround is employed, a warning should be provided to the
  user. (the user's workaround to skip the inefficient behavior would be to
  stop using that openstacksdk API call) An example of this is the nova
  "get me a network" feature. The logic of "get me a network" can be done
  client-side, albeit less efficiently. Adding support for the
  "get me a network" feature via nova microversion should also add support for
  doing the client-side workaround.

* If openstacksdk is aware of logic for more than one microversion, it should
  always attempt to use the latest version available for the service for that
  call.

* Objects returned from openstacksdk should always go through normalization and
  thus should always conform to openstacksdk's documented data model. The
  objects should never look different to the user regardless of the
  microversion used for the REST call.

* If a microversion adds new fields to an object, those fields should be
  added to openstacksdk's data model contract for that object and the data
  should either be filled in by performing additional REST calls if the data is
  available that way, or the field should have a default value of None which
  the user can be expected to test for when attempting to use the new value.

* If a microversion removes fields from an object that are part of the
  existing data model contract, care should be taken to not use the new
  microversion for that call unless forced to by lack of availablity of the
  old microversion on the cloud in question. In the case where an old
  microversion is no longer available, care must be taken to either find the
  data from another source and fill it in, or to put a value of None into the
  field and document for the user that on some clouds the value may not exist.

* If a microversion removes a field and the outcome is particularly intractable
  and impossible to work around without fundamentally breaking users,
  an issue should be raised with the service team in question. Hopefully a
  resolution can be found during the period while clouds still have the old
  microversion.

* As new calls or objects are added, it is important to check in with
  the service team in question on the expected stability of the object. If
  there are known changes expected in the future, even if they may be a few
  years off, openstacksdk should take care to not add committments to its data
  model for those fields/features. It is ok for openstacksdk to not have
  something.

  .. note::
    openstacksdk does not currently have any sort of "experimental" opt-in API
    that would allow exposing things to a user that may not be supportable
    under the normal compatibility contract. If a conflict arises in the
    future where there is a strong desire for a feature but also a lack of
    certainty about its stability over time, an experimental API may want to
    be explored ... but concrete use cases should arise before such a thing
    is started.
