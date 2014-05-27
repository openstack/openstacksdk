OpenStack Python SDK
====================

``python-openstacksdk`` is a ground-up implementation of a Python
API and SDK for OpenStack REST services.


Building Documentation
----------------------

This documentation is written by contributors, for contributors.

The source is maintained in the ``doc/source`` folder using
`reStructuredText`_ and built by `Sphinx`_

.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Sphinx: http://sphinx.pocoo.org/

* Building Manually::

    $ python setup.py build_sphinx

Results are in the `build/sphinx/html` directory.

Requirements
------------

* Python 2.6+, Python 3.3+
* httpretty
* pbr
* requests

License
-------

Apache 2.0
