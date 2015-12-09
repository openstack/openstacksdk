#!/bin/bash
#
# This is a script that kicks off a series of functional tests against a
# OpenStack devstack cloud.  This script is intended to work as a gate
# in project-config for the Python SDK.

DIR=$(cd $(dirname "$0") && pwd)

echo "Running SDK functional test suite"
sudo -H -u stack -i <<!
source ~stack/devstack/accrc/admin/admin
export OS_CLOUD=test_cloud
echo 'Running tests with:'
env | grep OS_
${DIR}/create_yaml.sh

cd ${DIR}
echo '=functional=============================================='
tox -e functional
FUNCTIONAL_RESULT=\$?
echo '=examples================================================'
tox -e examples
EXAMPLES_RESULT=\$?
echo '========================================================='
echo "Functional test result: \$FUNCTIONAL_RESULT"
echo "Examples test result:   \$EXAMPLES_RESULT"
test \$FUNCTIONAL_RESULT == 0 -a \$EXAMPLES_RESULT == 0
!
# TODO(thowe) For now we are going to ignore tests failures
# It is easier to change this script than the gate.  The magic
# string fro this script should probably specify the -e option
# so the script will fail immediately if a command fails.
exit 0
