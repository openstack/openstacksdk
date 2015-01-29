=====
Usage
=====

To use python-openstacksdk in a project::

    from openstack import connection
    from openstack import user_preference
    # First, specify your preferences
    pref = user_preference.UserPreference()
    pref.set_region('network', 'zion')
    # Second, create your authorization arguments
    auth_args = {
        'auth_url': 'http://172.20.1.108:5000/v3',
        'project_name': 'hacker',
        'user_name': 'neo',
        'password': 'bluepill',
    }
    # Third, create a connection
    conn = connection.Connection(preference=pref, **auth_args)
    # Finally, access your desired services
    network = conn.network.find_network("matrix")
    if network is None:
        network = conn.network.create_network({"name": "matrix"})
