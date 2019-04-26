# Install and configure **openstacksdk** library in devstack
#
# To enable openstacksdk in devstack add an entry to local.conf that looks like
#
# [[local|localrc]]
# enable_plugin openstacksdk https://opendev.org/openstack/openstacksdk

function preinstall_openstacksdk {
    :
}

function install_openstacksdk {
    if use_library_from_git "openstacksdk"; then
        # don't clone, it'll be done by the plugin install
        setup_dev_lib "openstacksdk"
    else
        pip_install "openstacksdk"
    fi
}

function configure_openstacksdk {
    :
}

function initialize_openstacksdk {
    :
}

function unstack_openstacksdk {
    :
}

function clean_openstacksdk {
    :
}

# This is the main for plugin.sh
if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
    preinstall_openstacksdk
elif [[ "$1" == "stack" && "$2" == "install" ]]; then
    install_openstacksdk
elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
    configure_openstacksdk
elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
    initialize_openstacksdk
fi

if [[ "$1" == "unstack" ]]; then
    unstack_openstacksdk
fi

if [[ "$1" == "clean" ]]; then
    clean_openstacksdk
fi
