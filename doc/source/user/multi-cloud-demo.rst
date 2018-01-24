================
Multi-Cloud Demo
================

This document contains a presentation in `presentty`_ format. If you want to
walk through it like a presentation, install `presentty` and run:

.. code:: bash

    presentty doc/source/user/multi-cloud-demo.rst

The content is hopefully helpful even if it's not being narrated, so it's being
included in the `shade` docs.

.. _presentty: https://pypi.python.org/pypi/presentty

Using Multiple OpenStack Clouds Easily with Shade
=================================================

Who am I?
=========

Monty Taylor

* OpenStack Infra Core
* irc: mordred
* twitter: @e_monty

What are we going to talk about?
================================

`shade`

* a task and end-user oriented Python library
* abstracts deployment differences
* designed for multi-cloud
* simple to use
* massive scale

  * optional advanced features to handle 20k servers a day

* Initial logic/design extracted from nodepool
* Librified to re-use in Ansible

shade is Free Software
======================

* https://git.openstack.org/cgit/openstack-infra/shade
* openstack-dev@lists.openstack.org
* #openstack-shade on freenode

This talk is Free Software, too
===============================

* Written for presentty (https://pypi.python.org/pypi/presentty)
* doc/source/multi-cloud-demo.rst
* examples in doc/source/examples
* Paths subject to change- this is the first presentation in tree!

Complete Example
================

.. code:: python

  from openstack import cloud as openstack

  # Initialize and turn on debug logging
  openstack.enable_logging(debug=True)

  for cloud_name, region_name in [
          ('my-vexxhost', 'ca-ymq-1'),
          ('my-citycloud', 'Buf1'),
          ('my-internap', 'ams01')]:
      # Initialize cloud
      cloud = openstack.openstack_cloud(cloud=cloud_name, region_name=region_name)

      # Upload an image to the cloud
      image = cloud.create_image(
          'devuan-jessie', filename='devuan-jessie.qcow2', wait=True)

      # Find a flavor with at least 512M of RAM
      flavor = cloud.get_flavor_by_ram(512)

      # Boot a server, wait for it to boot, and then do whatever is needed
      # to get a public ip for it.
      cloud.create_server(
          'my-server', image=image, flavor=flavor, wait=True, auto_ip=True)

Let's Take a Few Steps Back
===========================

Multi-cloud is easy, but you need to know a few things.

* Terminology
* Config
* Shade API

Cloud Terminology
=================

Let's define a few terms, so that we can use them with ease:

* `cloud` - logically related collection of services
* `region` - completely independent subset of a given cloud
* `patron` - human who has an account
* `user` - account on a cloud
* `project` - logical collection of cloud resources
* `domain` - collection of users and projects

Cloud Terminology Relationships
===============================

* A `cloud` has one or more `regions`
* A `patron` has one or more `users`
* A `patron` has one or more `projects`
* A `cloud` has one or more `domains`
* In a `cloud` with one `domain` it is named "default"
* Each `patron` may have their own `domain`
* Each `user` is in one `domain`
* Each `project` is in one `domain`
* A `user` has one or more `roles` on one or more `projects`

HTTP Sessions
=============

* HTTP interactions are authenticated via keystone
* Authenticating returns a `token`
* An authenticated HTTP Session is shared across a `region`

Cloud Regions
=============

A `cloud region` is the basic unit of REST interaction.

* A `cloud` has a `service catalog`
* The `service catalog` is returned in the `token`
* The `service catalog` lists `endpoint` for each `service` in each `region`
* A `region` is completely autonomous

Users, Projects and Domains
===========================

In clouds with multiple domains, project and user names are
only unique within a region.

* Names require `domain` information for uniqueness. IDs do not.
* Providing `domain` information when not needed is fine.
* `project_name` requires `project_domain_name` or `project_domain_id`
* `project_id` does not
* `username` requires `user_domain_name` or `user_domain_id`
* `user_id` does not

Confused Yet?
=============

Don't worry - you don't have to deal with most of that.

Auth per cloud, select per region
=================================

In general, the thing you need to know is:

* Configure authentication per `cloud`
* Select config to use by `cloud` and `region`

clouds.yaml
===========

Information about the clouds you want to connect to is stored in a file
called `clouds.yaml`.

`clouds.yaml` can be in your homedir: `~/.config/openstack/clouds.yaml`
or system-wide: `/etc/openstack/clouds.yaml`.

Information in your homedir, if it exists, takes precedence.

Full docs on `clouds.yaml` are at
https://docs.openstack.org/developer/os-client-config/

What about Mac and Windows?
===========================

`USER_CONFIG_DIR` is different on Linux, OSX and Windows.

* Linux: `~/.config/openstack`
* OSX: `~/Library/Application Support/openstack`
* Windows: `C:\\Users\\USERNAME\\AppData\\Local\\OpenStack\\openstack`

`SITE_CONFIG_DIR` is different on Linux, OSX and Windows.

* Linux: `/etc/openstack`
* OSX: `/Library/Application Support/openstack`
* Windows: `C:\\ProgramData\\OpenStack\\openstack`

Config Terminology
==================

For multi-cloud, think of two types:

* `profile` - Facts about the `cloud` that are true for everyone
* `cloud` - Information specific to a given `user`

Apologies for the use of `cloud` twice.

Environment Variables and Simple Usage
======================================

* Environment variables starting with `OS_` go into a cloud called `envvars`
* If you only have one cloud, you don't have to specify it
* `OS_CLOUD` and `OS_REGION_NAME` are default values for
  `cloud` and `region_name`

TOO MUCH TALKING - NOT ENOUGH CODE
==================================

basic clouds.yaml for the example code
======================================

Simple example of a clouds.yaml

* Config for a named `cloud` "my-citycloud"
* Reference a well-known "named" profile: `citycloud`
* `os-client-config` has a built-in list of profiles at
  https://docs.openstack.org/developer/os-client-config/vendor-support.html
* Vendor profiles contain various advanced config
* `cloud` name can match `profile` name (using different names for clarity)

.. code:: yaml

  clouds:
    my-citycloud:
      profile: citycloud
      auth:
        username: mordred
        project_id: 65222a4d09ea4c68934fa1028c77f394
        user_domain_id: d0919bd5e8d74e49adf0e145807ffc38
        project_domain_id: d0919bd5e8d74e49adf0e145807ffc38

Where's the password?

secure.yaml
===========

* Optional additional file just like `clouds.yaml`
* Values overlaid on `clouds.yaml`
* Useful if you want to protect secrets more stringently

Example secure.yaml
===================

* No, my password isn't XXXXXXXX
* `cloud` name should match `clouds.yaml`
* Optional - I actually keep mine in my `clouds.yaml`

.. code:: yaml

  clouds:
    my-citycloud:
      auth:
        password: XXXXXXXX

more clouds.yaml
================

More information can be provided.

* Use v3 of the `identity` API - even if others are present
* Use `https://image-ca-ymq-1.vexxhost.net/v2` for `image` API
  instead of what's in the catalog

.. code:: yaml

    my-vexxhost:
      identity_api_version: 3
      image_endpoint_override: https://image-ca-ymq-1.vexxhost.net/v2
      profile: vexxhost
      auth:
        user_domain_id: default
        project_domain_id: default
        project_name: d8af8a8f-a573-48e6-898a-af333b970a2d
        username: 0b8c435b-cc4d-4e05-8a47-a2ada0539af1

Much more complex clouds.yaml example
=====================================

* Not using a profile - all settings included
* In the `ams01` `region` there are two networks with undiscoverable qualities
* Each one are labeled here so choices can be made
* Any of the settings can be specific to a `region` if needed
* `region` settings override `cloud` settings
* `cloud` does not support `floating-ips`

.. code:: yaml

    my-internap:
      auth:
        auth_url: https://identity.api.cloud.iweb.com
        username: api-55f9a00fb2619
        project_name: inap-17037
      identity_api_version: 3
      floating_ip_source: None
      regions:
      - name: ams01
        values:
          networks:
          - name: inap-17037-WAN1654
            routes_externally: true
            default_interface: true
          - name: inap-17037-LAN3631
            routes_externally: false

Complete Example Again
======================

.. code:: python

  from openstack import cloud as openstack

  # Initialize and turn on debug logging
  openstack.enable_logging(debug=True)

  for cloud_name, region_name in [
          ('my-vexxhost', 'ca-ymq-1'),
          ('my-citycloud', 'Buf1'),
          ('my-internap', 'ams01')]:
      # Initialize cloud
      cloud = openstack.openstack_cloud(cloud=cloud_name, region_name=region_name)

      # Upload an image to the cloud
      image = cloud.create_image(
          'devuan-jessie', filename='devuan-jessie.qcow2', wait=True)

      # Find a flavor with at least 512M of RAM
      flavor = cloud.get_flavor_by_ram(512)

      # Boot a server, wait for it to boot, and then do whatever is needed
      # to get a public ip for it.
      cloud.create_server(
          'my-server', image=image, flavor=flavor, wait=True, auto_ip=True)

Step By Step
============

Import the library
==================

.. code:: python

  from openstack import cloud as openstack

Logging
=======

* `openstacksdk` uses standard python logging
* ``openstack.enable_logging`` does easy defaults
* Squelches some meaningless warnings

  * `debug`

     * Logs shade loggers at debug level

  * `http_debug` Implies `debug`, turns on HTTP tracing

.. code:: python

  # Initialize and turn on debug logging
  openstack.enable_logging(debug=True)

Example with Debug Logging
==========================

* doc/source/examples/debug-logging.py

.. code:: python

  from openstack import cloud as openstack
  openstack.enable_logging(debug=True)

  cloud = openstack.openstack_cloud(
      cloud='my-vexxhost', region_name='ca-ymq-1')
  cloud.get_image('Ubuntu 16.04.1 LTS [2017-03-03]')

Example with HTTP Debug Logging
===============================

* doc/source/examples/http-debug-logging.py

.. code:: python

  from openstack import cloud as openstack
  openstack.enable_logging(http_debug=True)

  cloud = openstack.openstack_cloud(
      cloud='my-vexxhost', region_name='ca-ymq-1')
  cloud.get_image('Ubuntu 16.04.1 LTS [2017-03-03]')

Cloud Regions
=============

* `cloud` constructor needs `cloud` and `region_name`
* `openstack.openstack_cloud` is a helper factory function

.. code:: python

  for cloud_name, region_name in [
          ('my-vexxhost', 'ca-ymq-1'),
          ('my-citycloud', 'Buf1'),
          ('my-internap', 'ams01')]:
      # Initialize cloud
      cloud = openstack.openstack_cloud(cloud=cloud_name, region_name=region_name)

Upload an Image
===============

* Picks the correct upload mechanism
* **SUGGESTION** Always upload your own base images

.. code:: python

      # Upload an image to the cloud
      image = cloud.create_image(
          'devuan-jessie', filename='devuan-jessie.qcow2', wait=True)

Always Upload an Image
======================

Ok. You don't have to. But, for multi-cloud...

* Images with same content are named different on different clouds
* Images with same name on different clouds can have different content
* Upload your own to all clouds, both problems go away
* Download from OS vendor or build with `diskimage-builder`

Find a flavor
=============

* Flavors are all named differently on clouds
* Flavors can be found via RAM
* `get_flavor_by_ram` finds the smallest matching flavor

.. code:: python

      # Find a flavor with at least 512M of RAM
      flavor = cloud.get_flavor_by_ram(512)

Create a server
===============

* my-vexxhost

  * Boot server
  * Wait for `status==ACTIVE`

* my-internap

  * Boot server on network `inap-17037-WAN1654`
  * Wait for `status==ACTIVE`

* my-citycloud

  * Boot server
  * Wait for `status==ACTIVE`
  * Find the `port` for the `fixed_ip` for `server`
  * Create `floating-ip` on that `port`
  * Wait for `floating-ip` to attach

.. code:: python

      # Boot a server, wait for it to boot, and then do whatever is needed
      # to get a public ip for it.
      cloud.create_server(
          'my-server', image=image, flavor=flavor, wait=True, auto_ip=True)

Wow. We didn't even deploy Wordpress!
=====================================

Image and Flavor by Name or ID
==============================

* Pass string to image/flavor
* Image/Flavor will be found by name or ID
* Common pattern
* doc/source/examples/create-server-name-or-id.py

.. code:: python

  from openstack import cloud as openstack

  # Initialize and turn on debug logging
  openstack.enable_logging(debug=True)

  for cloud_name, region_name, image, flavor in [
          ('my-vexxhost', 'ca-ymq-1',
           'Ubuntu 16.04.1 LTS [2017-03-03]', 'v1-standard-4'),
          ('my-citycloud', 'Buf1',
           'Ubuntu 16.04 Xenial Xerus', '4C-4GB-100GB'),
          ('my-internap', 'ams01',
           'Ubuntu 16.04 LTS (Xenial Xerus)', 'A1.4')]:
      # Initialize cloud
      cloud = openstack.openstack_cloud(cloud=cloud_name, region_name=region_name)

      # Boot a server, wait for it to boot, and then do whatever is needed
      # to get a public ip for it.
      server = cloud.create_server(
          'my-server', image=image, flavor=flavor, wait=True, auto_ip=True)
      print(server.name)
      print(server['name'])
      cloud.pprint(server)
      # Delete it - this is a demo
      cloud.delete_server(server, wait=True, delete_ips=True)

cloud.pprint method was just added this morning
===============================================

Delete Servers
==============

* `delete_ips` Delete any `floating_ips` the server may have

.. code:: python

      cloud.delete_server('my-server', wait=True, delete_ips=True)

Image and Flavor by Dict
========================

* Pass dict to image/flavor
* If you know if the value is Name or ID
* Common pattern
* doc/source/examples/create-server-dict.py

.. code:: python

  from openstack import cloud as openstack

  # Initialize and turn on debug logging
  openstack.enable_logging(debug=True)

  for cloud_name, region_name, image, flavor_id in [
          ('my-vexxhost', 'ca-ymq-1', 'Ubuntu 16.04.1 LTS [2017-03-03]',
           '5cf64088-893b-46b5-9bb1-ee020277635d'),
          ('my-citycloud', 'Buf1', 'Ubuntu 16.04 Xenial Xerus',
           '0dab10b5-42a2-438e-be7b-505741a7ffcc'),
          ('my-internap', 'ams01', 'Ubuntu 16.04 LTS (Xenial Xerus)',
           'A1.4')]:
      # Initialize cloud
      cloud = openstack.openstack_cloud(cloud=cloud_name, region_name=region_name)

      # Boot a server, wait for it to boot, and then do whatever is needed
      # to get a public ip for it.
      server = cloud.create_server(
          'my-server', image=image, flavor=dict(id=flavor_id),
          wait=True, auto_ip=True)
      # Delete it - this is a demo
      cloud.delete_server(server, wait=True, delete_ips=True)

Munch Objects
=============

* Behave like a dict and an object
* doc/source/examples/munch-dict-object.py

.. code:: python

  from openstack import cloud as openstack
  openstack.enable_logging(debug=True)

  cloud = openstack.openstack_cloud(cloud='zetta', region_name='no-osl1')
  image = cloud.get_image('Ubuntu 14.04 (AMD64) [Local Storage]')
  print(image.name)
  print(image['name'])

API Organized by Logical Resource
=================================

* list_servers
* search_servers
* get_server
* create_server
* delete_server
* update_server

For other things, it's still {verb}_{noun}

* attach_volume
* wait_for_server
* add_auto_ip

Cleanup Script
==============

* Sometimes my examples had bugs
* doc/source/examples/cleanup-servers.py

.. code:: python

  from openstack import cloud as openstack

  # Initialize and turn on debug logging
  openstack.enable_logging(debug=True)

  for cloud_name, region_name in [
          ('my-vexxhost', 'ca-ymq-1'),
          ('my-citycloud', 'Buf1'),
          ('my-internap', 'ams01')]:
      # Initialize cloud
      cloud = openstack.openstack_cloud(cloud=cloud_name, region_name=region_name)
      for server in cloud.search_servers('my-server'):
          cloud.delete_server(server, wait=True, delete_ips=True)

Normalization
=============

* https://docs.openstack.org/developer/shade/model.html#image
* doc/source/examples/normalization.py

.. code:: python

  from openstack import cloud as openstack
  openstack.enable_logging()

  cloud = openstack.openstack_cloud(cloud='fuga', region_name='cystack')
  image = cloud.get_image(
      'Ubuntu 16.04 LTS - Xenial Xerus - 64-bit - Fuga Cloud Based Image')
  cloud.pprint(image)

Strict Normalized Results
=========================

* Return only the declared model
* doc/source/examples/strict-mode.py

.. code:: python

  from openstack import cloud as openstack
  openstack.enable_logging()

  cloud = openstack.openstack_cloud(
      cloud='fuga', region_name='cystack', strict=True)
  image = cloud.get_image(
      'Ubuntu 16.04 LTS - Xenial Xerus - 64-bit - Fuga Cloud Based Image')
  cloud.pprint(image)

How Did I Find the Image Name for the Last Example?
===================================================

* I often make stupid little utility scripts
* doc/source/examples/find-an-image.py

.. code:: python

  from openstack import cloud as openstack
  openstack.enable_logging()

  cloud = openstack.openstack_cloud(cloud='fuga', region_name='cystack')
  cloud.pprint([
      image for image in cloud.list_images()
      if 'ubuntu' in image.name.lower()])

Added / Modified Information
============================

* Servers need more extra help
* Fetch addresses dict from neutron
* Figure out which IPs are good
* `detailed` - defaults to True, add everything
* `bare` - no extra calls - don't even fix broken things
* `bare` is still normalized
* doc/source/examples/server-information.py

.. code:: python

  from openstack import cloud as openstack
  openstack.enable_logging(debug=True)

  cloud = openstack.openstack_cloud(cloud='my-citycloud', region_name='Buf1')
  try:
      server = cloud.create_server(
          'my-server', image='Ubuntu 16.04 Xenial Xerus',
          flavor=dict(id='0dab10b5-42a2-438e-be7b-505741a7ffcc'),
          wait=True, auto_ip=True)

      print("\n\nFull Server\n\n")
      cloud.pprint(server)

      print("\n\nTurn Detailed Off\n\n")
      cloud.pprint(cloud.get_server('my-server', detailed=False))

      print("\n\nBare Server\n\n")
      cloud.pprint(cloud.get_server('my-server', bare=True))

  finally:
      # Delete it - this is a demo
      cloud.delete_server(server, wait=True, delete_ips=True)

Exceptions
==========

* All shade exceptions are subclasses of `OpenStackCloudException`
* Direct REST calls throw `OpenStackCloudHTTPError`
* `OpenStackCloudHTTPError` subclasses `OpenStackCloudException`
  and `requests.exceptions.HTTPError`
* `OpenStackCloudURINotFound` for 404
* `OpenStackCloudBadRequest` for 400

User Agent Info
===============

* Set `app_name` and `app_version` for User Agents
* (sssh ... `region_name` is optional if the cloud has one region)
* doc/source/examples/user-agent.py

.. code:: python

  from openstack import cloud as openstack
  openstack.enable_logging(http_debug=True)

  cloud = openstack.openstack_cloud(
      cloud='datacentred', app_name='AmazingApp', app_version='1.0')
  cloud.list_networks()

Uploading Large Objects
=======================

* swift has a maximum object size
* Large Objects are uploaded specially
* shade figures this out and does it
* multi-threaded
* doc/source/examples/upload-object.py

.. code:: python

  from openstack import cloud as openstack
  openstack.enable_logging(debug=True)

  cloud = openstack.openstack_cloud(cloud='ovh', region_name='SBG1')
  cloud.create_object(
      container='my-container', name='my-object',
      filename='/home/mordred/briarcliff.sh3d')
  cloud.delete_object('my-container', 'my-object')
  cloud.delete_container('my-container')

Uploading Large Objects
=======================

* Default max_file_size is 5G
* This is a conference demo
* Let's force a segment_size
* One MILLION bytes
* doc/source/examples/upload-object.py

.. code:: python

  from openstack import cloud as openstack
  openstack.enable_logging(debug=True)

  cloud = openstack.openstack_cloud(cloud='ovh', region_name='SBG1')
  cloud.create_object(
      container='my-container', name='my-object',
      filename='/home/mordred/briarcliff.sh3d',
      segment_size=1000000)
  cloud.delete_object('my-container', 'my-object')
  cloud.delete_container('my-container')

Service Conditionals
====================

.. code:: python

  from openstack import cloud as openstack
  openstack.enable_logging(debug=True)

  cloud = openstack.openstack_cloud(cloud='kiss', region_name='region1')
  print(cloud.has_service('network'))
  print(cloud.has_service('container-orchestration'))

Service Conditional Overrides
=============================

* Sometimes clouds are weird and figuring that out won't work

.. code:: python

  from openstack import cloud as openstack
  openstack.enable_logging(debug=True)

  cloud = openstack.openstack_cloud(cloud='rax', region_name='DFW')
  print(cloud.has_service('network'))

.. code:: yaml

  clouds:
    rax:
      profile: rackspace
      auth:
        username: mordred
        project_id: 245018
      # This is already in profile: rackspace
      has_network: false

Coming Soon
===========

* Completion of RESTification
* Full version discovery support
* Multi-cloud facade layer
* Microversion support (talk tomorrow)
* Completion of caching tier (talk tomorrow)
* All of you helping hacking on shade!!! (we're friendly)
