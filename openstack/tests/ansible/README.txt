This directory contains a testing infrastructure for the Ansible
OpenStack modules. You will need a clouds.yaml file in order to run
the tests. You must provide a value for the `cloud` variable for each
run (using the -e option) as a default is not currently provided.

If you want to run these tests against devstack, it is easiest to use
the tox target. This assumes you have a devstack-admin cloud defined
in your clouds.yaml file that points to devstack. Some examples of
using tox:

    tox -e ansible

    tox -e ansible keypair security_group

If you want to run these tests directly, or against different clouds,
then you'll need to use the ansible-playbook command that comes with
the Ansible distribution and feed it the run.yml playbook. Some examples:

    # Run all module tests against a provider
    ansible-playbook run.yml -e "cloud=hp"

    # Run only the keypair and security_group tests
    ansible-playbook run.yml -e "cloud=hp" --tags "keypair,security_group"

    # Run all tests except security_group
    ansible-playbook run.yml -e "cloud=hp" --skip-tags "security_group"
