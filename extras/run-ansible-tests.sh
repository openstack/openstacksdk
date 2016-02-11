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
#
# USAGE:
#    run-ansible-tests.sh -e ENVDIR [-c CLOUD] [TAG ...]
#
# PARAMETERS:
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


CLOUD="devstack-admin"
ENVDIR=

while getopts "c:e:" opt
do
    case $opt in
    c) CLOUD=${OPTARG} ;;
    e) ENVDIR=${OPTARG} ;;
    ?) echo "Invalid option: -${OPTARG}"
       exit 1;;
    esac
done

if [ -z ${ENVDIR} ]
then
    echo "Option -e is required"
    exit 1
fi

shift $((OPTIND-1))
TAGS=$( echo "$*" | tr ' ' , )

# We need to source the current tox environment so that Ansible will
# be setup for the correct python environment.
source $ENVDIR/bin/activate

echo "Installing Ansible"
pip install ansible

# Run the shade Ansible tests
tag_opt=""
if [ ! -z ${TAGS} ]
then
    tag_opt="--tags ${TAGS}"
fi

ansible-playbook -vvv ./shade/tests/ansible/run.yml -e "cloud=${CLOUD}" ${tag_opt}
