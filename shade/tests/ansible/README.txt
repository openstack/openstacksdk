This directory contains a testing infrastructure for the Ansible
OpenStack modules. You will need a clouds.yaml file in order to run
the tests. You must provide a value for the `cloud` variable for each
run (using the -e option) as a default is not currently provided.


Examples
--------

* Run all module tests against a provider:

    ansible-playbook run.yml -e "cloud=hp"

* Run only the keypair and security_group tests:

    ansible-playbook run.yml -e "cloud=hp" --tags "keypair,security_group"

* Run all tests except security_group:

    ansible-playbook run.yml -e "cloud=hp" --skip-tags "security_group"
