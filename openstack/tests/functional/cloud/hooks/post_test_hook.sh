#!/bin/bash -x

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# TODO(shade) Rework for zuul v3

export OPENSTACKSDK_DIR="$BASE/new/shade"

cd $OPENSTACKSDK_DIR
sudo chown -R jenkins:stack $OPENSTACKSDK_DIR

CLOUDS_YAML=/etc/openstack/clouds.yaml

if [ ! -e ${CLOUDS_YAML} ]
then
    # stable/liberty had clouds.yaml in the home/base directory
    sudo mkdir -p /etc/openstack
    sudo cp $BASE/new/.config/openstack/clouds.yaml ${CLOUDS_YAML}
    sudo chown -R jenkins:stack /etc/openstack
fi

# Devstack runs both keystone v2 and v3. An environment variable is set
# within the shade keystone v2 job that tells us which version we should
# test against.
if [ ${OPENSTACKSDK_USE_KEYSTONE_V2:-0} -eq 1 ]
then
    sudo sed -ie "s/identity_api_version: '3'/identity_api_version: '2.0'/g" $CLOUDS_YAML
    sudo sed -ie '/^.*domain_id.*$/d' $CLOUDS_YAML
fi

if [ "x$1" = "xtips" ] ; then
    tox_env=functional-tips
else
    tox_env=functional
fi
echo "Running shade functional test suite"
set +e
sudo -E -H -u jenkins tox -e$tox_env
EXIT_CODE=$?
sudo stestr last --subunit > $WORKSPACE/tempest.subunit
.tox/$tox_env/bin/pbr freeze
set -e

exit $EXIT_CODE
