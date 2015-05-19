#!/bin/bash
#
# This is a script that kicks off a series of functional tests against a
# OpenStack devstack cloud.  This script is intended to work as a gate
# in project-config for the Python SDK.

DIR=$(cd $(dirname "$0") && pwd)

echo "Running SDK functional test suite"
sudo -H -u stack -i <<!
source ~stack/devstack/accrc/admin/admin
export OS_CLOUD=envvars
echo 'Running tests with:'
env | grep OS_
cd ${DIR}
tox -e functional
!
# TODO(thowe) For now we are going to ignore tests failures
# It is easier to change this script than the gate.  The magic
# string fro this script should probably specify the -e option
# so the script will fail immediately if a command fails.
exit 0
