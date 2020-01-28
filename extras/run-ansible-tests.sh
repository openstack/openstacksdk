#!/bin/bash
#############################################################################
# run-ansible-tests.sh
#
# Script used to setup a tox environment for running Ansible. This is meant
# to be called by tox (via tox.ini). To run the Ansible tests, use:
#
#    tox -e ansible [TAG ...]
# or
#    tox -e ansible -- -c cloudX [TAG ...]
# or to use the development version of Ansible:
#    tox -e ansible -- -d -c cloudX [TAG ...]
#
# USAGE:
#    run-ansible-tests.sh -e ENVDIR [-d] [-c CLOUD] [TAG ...]
#
# PARAMETERS:
#    -d         Use Ansible source repo development branch.
#    -e ENVDIR  Directory of the tox environment to use for testing.
#    -c CLOUD   Name of the cloud to use for testing.
#               Defaults to "devstack-admin".
#    [TAG ...]  Optional list of space-separated tags to control which
#               modules are tested.
#
# EXAMPLES:
#    # Run all Ansible tests
#    run-ansible-tests.sh -e ansible
#
#    # Run auth, keypair, and network tests against cloudX
#    run-ansible-tests.sh -e ansible -c cloudX auth keypair network
#############################################################################

echo "
    Thanks for submitting patch for Openstack Ansible modules!
    We moved Openstack Ansible modules to Openstack repositories.
    Next patches should be submitted not with Ansible Github but with
    Openstack Gerrit: https://review.opendev.org/#/q/project:openstack/ansible-collections-openstack
    Please submit your code there from now.
    Thanks for your contribution and sorry for inconvienience.
"
exit 1
