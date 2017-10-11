#!/bin/bash
source ${JENKINS_HOME}/jobs/credentials.sh > /dev/null 2>&1

create_virtualenv () {
    NAME=$1
    virtualenv $NAME
    source $NAME/bin/activate
}

delete_virtualenv () {
    virtualenv_dir=$1
    deactivate
    rm -rf $virtualenv_dir
}

create_cfy_manager () {
    cfy install ${ENVIRONMENT_SETUP_ARCHIVE_URL} \
        -n ${ENVIRONMENT_SETUP_BLUEPRINT_FILE_NAME} \
        -b ecosystem_build ${ENVIRONMENT_SETUP_INPUTS_STRING} \
        --task-retries=30 \
        --task-retry-interval=5 \
        -vv --install-plugins
}

install_example () {

    echo "cfy install $1 \
        -n $ENVIRONMENT_SETUP_BLUEPRINT_FILE_NAME \
        -b example \
        -vv"

    echo "cfy uninstall \
        --allow-custom-parameters \
        -p ignore_failure=true \
        -b example \
        -vv"
}

delete_cfy_manager () {
    cfy profiles use local
    cfy uninstall \
        -b ecosystem_build \
        --task-retries=30 \
        --task-retry-interval=5 \
        --allow-custom-parameters \
        -p ignore_failure=true \
        -vv
}

create_virtualenv ecosystem
virtualenv_dir=$VIRTUAL_ENV
pip install -U pip
pip install cloudify

if ! create_cfy_manager; then
    echo "failed to create manager environment"
    delete_cfy_manager
    exit 1
fi

while IFS= read -r line;
    do
    substring="cfy profiles use"
    if [[ $line == *"${substring}"* ]]
    then
        cfy_profiles_use=$line
    fi
done<instructions.txt

$cfy_profiles_use

for i in $BLUEPRINT_EXAMPLE_URLS;
    do install_example $i
done

delete_cfy_manager

delete_virtualenv $virtualenv_dir
