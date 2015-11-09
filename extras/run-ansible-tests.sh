#!/bin/bash
#############################################################################
# run-ansible-tests.sh
#
# Script used to setup a tox environment for running Ansible. This is meant
# to be called by tox (via tox.ini). To run the Ansible tests, use:
#
#    tox -e ansible
#
# USAGE:
#    run-ansible-tests.sh <envdir>
#
# PARAMETERS:
#    <envdir>  Directory of the tox environment to use for testing.
#############################################################################

ENVDIR=$1

if [ -d ${ENVDIR}/ansible ]
then
    echo "Using existing Ansible install"
else
    echo "Installing Ansible at $ENVDIR"
    git clone --recursive git://github.com/ansible/ansible.git ${ENVDIR}/ansible
fi

# We need to source the current tox environment so that Ansible will
# be setup for the correct python environment.
source $ENVDIR/bin/activate

# Setup Ansible
source $ENVDIR/ansible/hacking/env-setup

# Run the shade Ansible tests
ansible-playbook -vvv ./shade/tests/ansible/run.yml -e "cloud=devstack-admin"
