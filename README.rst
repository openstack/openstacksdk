OpenStack Python SDK
====================

``python-openstacksdk`` is a new Python library and SDK for OpenStack
clouds. It is very young, and not yet usable, but it's under active
development.

Our goal is to provide a Python library which is:

* Pleasant to use
* Well documented
* Complete (works with any OpenStack project)

Building Documentation
----------------------

This documentation is written by contributors, for contributors.

The source is maintained in the ``doc/source/`` folder using
`reStructuredText`_ and built by `Sphinx`_

.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Sphinx: http://sphinx.pocoo.org/

To build the docs locally::

    $ python setup.py build_sphinx

Results are in the ``doc/build/html/`` directory.

Requirements
------------

* Python 2.6+, Python 3.3+
* pbr
* requests
* iso8601
* stevedore

License
-------

Apache 2.0
