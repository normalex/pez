#!/usr/bin/env bash

VENV_PATH="$1"

if ! [[ -d "${VENV_PATH}" ]]; then
    echo "First Argument: Virtual environment path does not exist"
    exit 1
fi

sudo yum check-update || sudo apt-get update

sudo yum -y groupinstall "Development tools" || sudo apt-get -y install build-essential
sudo yum -y install python27-devel || sudo apt-get -y install python-dev

if ! [[ -x "$(which pip)" ]]; then
        sudo yum -y install python-pip || sudo apt-get -y install python-pip
    fi

    sudo pip install --upgrade pip virtualenv
    virtualenv "${VENV_PATH}"
    . "${VENV_PATH}/bin/activate"
    pip install -e .[test]

