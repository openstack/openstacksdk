# Install and configure **shade** library in devstack
#
# To enable shade in devstack add an entry to local.conf that looks like
#
# [[local|localrc]]
# enable_plugin shade git://git.openstack.org/openstack-infra/shade

function preinstall_shade {
    :
}

function install_shade {
    if use_library_from_git "shade"; then
        # don't clone, it'll be done by the plugin install
        setup_dev_lib "shade"
    else
        pip_install "shade"
    fi
}

function configure_shade {
    :
}

function initialize_shade {
    :
}

function unstack_shade {
    :
}

function clean_shade {
    :
}

# This is the main for plugin.sh
if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
    preinstall_shade
elif [[ "$1" == "stack" && "$2" == "install" ]]; then
    install_shade
elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
    configure_shade
elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
    initialize_shade
fi

if [[ "$1" == "unstack" ]]; then
    unstack_shade
fi

if [[ "$1" == "clean" ]]; then
    clean_shade
fi
