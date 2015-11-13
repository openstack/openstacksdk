#!/bin/bash
#############################################################################
# run-ansible-tests.sh
#
# Script used to setup a tox environment for running Ansible. This is meant
# to be called by tox (via tox.ini). To run the Ansible tests, use:
#
#    tox -e ansible [TAG]
#
# USAGE:
#    run-ansible-tests.sh <envdir> [TAG]
#
# PARAMETERS:
#    <envdir>  Directory of the tox environment to use for testing.
#    [TAG]     Optional list of space-separated tags to control which
#              modules are tested.
#
# EXAMPLES:
#    # Run all Ansible tests
#    run-ansible-tests.sh ansible
#
#    # Run auth, keypair, and network tests
#    run-ansible-tests.sh ansible auth keypair network
#############################################################################

ENVDIR=$1
shift
TAGS=$( echo "$@" | tr ' ' , )

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
tag_opt=""
if [ "${TAGS}" != "" ]
then
    tag_opt="--tags ${TAGS}"
fi
ansible-playbook -vvv ./shade/tests/ansible/run.yml -e "cloud=devstack-admin" ${tag_opt}
