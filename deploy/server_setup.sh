#!/usr/bin/env bash

# TODO: Set to URL of git repo.
PROJECT_GIT_URL='https://github.com/4ndr/data_gather.git'

PROJECT_BASE_PATH='/usr/local/apps'
VIRTUALENV_BASE_PATH='/usr/local/virtualenvs'

# Set Ubuntu Language
locale-gen en_GB.UTF-8

# Install Python, SQLite and pip
apt-get update
apt-get install -y python3-dev sqlite python-pip supervisor nginx git

# Upgrade pip to the latest version.
pip install --upgrade pip
pip install virtualenv

mkdir -p $PROJECT_BASE_PATH
git clone $PROJECT_GIT_URL $PROJECT_BASE_PATH/data_gather

mkdir -p $VIRTUALENV_BASE_PATH
virtualenv --python=python3 $VIRTUALENV_BASE_PATH/data_gather

source $VIRTUALENV_BASE_PATH/data_gather/bin/activate
pip install -r $PROJECT_BASE_PATH/data_gather/requirements.txt

# Run migrations
cd $PROJECT_BASE_PATH/data_gather/

# Setup Supervisor to run our uwsgi process.
cp $PROJECT_BASE_PATH/data_gather/deploy/supervisor_data_gather.conf /etc/supervisor/conf.d/data_gather.conf
supervisorctl reread
supervisorctl update
supervisorctl restart data_gather

# Setup nginx to make our application accessible.
cp $PROJECT_BASE_PATH/data_gather/deploy/nginx_data_gather.conf /etc/nginx/sites-available/data_gather.conf
rm /etc/nginx/sites-enabled/default
ln -s /etc/nginx/sites-available/data_gather.conf /etc/nginx/sites-enabled/data_gather.conf
systemctl restart nginx.service

echo "DONE! :)"