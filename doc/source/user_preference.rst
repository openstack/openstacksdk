UserPreference
==============
.. automodule:: openstack.user_preference

UserPreference Object
-----------------

.. autoclass:: openstack.user_preference.UserPreference
   :members:

Examples
--------

The ``UserPreference`` class is constructed with no arguments.

Set Methods
~~~~~~~~~~~

The user preferences are set based on the service type.  Service type would
normally be something like 'compute', 'identity', 'object-store', etc.::

    from openstack import user_preference
    pref = user_preference.UserPreference()
    pref.set_name('compute', 'matrix')
    pref.set_region(pref.ALL, 'zion')
    pref.set_version('identity', 'v3')
    pref.set_visibility('object-store', 'internal')
    for service in pref.get_services():
        print str(pref.get_preference(service.service_type))

The resulting preference print out would look something like::

    service_type=compute,region=zion,service_name=matrix
    service_type=network,region=zion
    service_type=database,region=zion
    service_type=image,region=zion
    service_type=metering,region=zion
    service_type=orchestration,region=zion
    service_type=object-store,visibility=internal,region=zion
    service_type=identity,region=zion,version=v3
