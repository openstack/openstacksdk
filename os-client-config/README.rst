================
os-client-config
================

.. image:: http://governance.openstack.org/badges/os-client-config.svg
    :target: http://governance.openstack.org/reference/tags/index.html

`os-client-config` is a library for collecting client configuration for
using an OpenStack cloud in a consistent and comprehensive manner. It
will find cloud config for as few as 1 cloud and as many as you want to
put in a config file. It will read environment variables and config files,
and it also contains some vendor specific default values so that you don't
have to know extra info to use OpenStack

* If you have a config file, you will get the clouds listed in it
* If you have environment variables, you will get a cloud named `envvars`
* If you have neither, you will get a cloud named `defaults` with base defaults

Source
------

* Free software: Apache license
* Documentation: http://docs.openstack.org/os-client-config/latest
* Source: http://git.openstack.org/cgit/openstack/os-client-config
* Bugs: http://bugs.launchpad.net/os-client-config
