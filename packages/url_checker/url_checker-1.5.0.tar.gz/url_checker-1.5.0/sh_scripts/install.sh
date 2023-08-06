#!/usr/bin/env bash

apt-get -y update

apt-get -y install python3-pip
apt-get -y install python3-dev python3-setuptools
apt-get -y install git
apt-get -y install supervisor

pip install --upgrade pip
pip install -r requirements.txt
pip freeze