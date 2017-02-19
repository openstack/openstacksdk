#!/bin/bash
#
# NOTE(thowe): There are some issues with OCC envvars that force us to do
# this for now.
#
mkdir -p ~/.config/openstack/
FILE=~/.config/openstack/clouds.yaml
export OS_IDENTITY_API_VERSION=3 # force v3 identity
echo 'clouds:' >$FILE
echo '  test_cloud:' >>$FILE
env | grep OS_ | tr '=' ' ' | while read k v
do
  k=$(echo $k | sed -e 's/OS_//')
  k=$(echo $k | tr '[A-Z]' '[a-z]')
  case "$k" in
  region_name|*_api_version)
    echo "    $k: $v" >>$FILE
  esac
done
echo "    auth:" >>$FILE
env | grep OS_ | tr '=' ' ' | while read k v
do
  k=$(echo $k | sed -e 's/OS_//')
  k=$(echo $k | tr '[A-Z]' '[a-z]')
  case "$k" in
  region_name|*_api_version)
    ;;
  *)
    echo "      $k: $v" >>$FILE
  esac
done
