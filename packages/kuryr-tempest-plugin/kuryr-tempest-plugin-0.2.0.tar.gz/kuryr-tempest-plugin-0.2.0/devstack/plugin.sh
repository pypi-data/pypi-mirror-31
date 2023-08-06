# install tempest plugin
function build_test_container {
    pushd "${DEST}/kuryr-tempest-plugin/test_container"

    docker build -t kuryr/demo . -f Dockerfile
    popd
}

function install_kuryr_tempest_plugin {
    setup_dev_lib "kuryr-tempest-plugin"
}

if [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "Building kuryr/demo test container"
        build_test_container
        echo_summary "Installing Kuryr Tempest Plugin"
        install_kuryr_tempest_plugin
fi
