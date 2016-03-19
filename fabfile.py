'''
Automated staging deployment has been tested on Ubuntu with
actual development done on AMI

Specify actual configuration overrides as environment arguments
or in a separate file as exports that bash can source.

Example:
    * provision 3 ubuntu instances on EC2
    * source the development virtualenv with extras installed:
        to install extras use: pip install -e .[test]
    * db server is 1.2.3.4, web1 is a.b.c.d, and web2 is w.x.y.z
    Configuring DB server:
        fab -i <yoursshpemkey> ubuntu@1.2.3.4 configure_db_server
        NOTE: if the development is also on Ubuntu and ssh localhost works
              the local DB server can also be provisione the same way

    Running tests:
        fab runtests

    Deploying app on staging servers:
        PEZ_DB_HOST=1.2.3.4 fab -i <yoursshpemkey> -H ubuntu@a.b.c.d,ubuntu@w.x.y.z deploy

'''

import os
import time
import fabtools

from fabric.api import (
    settings, run, sudo, local, abort, put
)
from fabric.contrib import files

from pez.config import configuration
from pez.models import create_schema, drop_schema

DEPLOY_ENV_PATH = '/opt/pezapp'
GUNICORN_BIN = os.path.join(DEPLOY_ENV_PATH, 'bin', 'gunicorn')
DEPLOY_USERNAME = 'pezapp'
DEPLOY_TMP_PATH = '/tmp/pez'
DEPLOY_SERVICE_NAME = 'pezapp'
DEPLOY_SERVICE_PORT = 8000
DEPLOY_UPSTART_FILE = os.path.join(
    '/etc/init',
    DEPLOY_SERVICE_NAME + '.conf'
)

# direct key references to fail fast if missing
dbusername = configuration['dbusername']
dbpassword = configuration['dbpassword']
dbname = configuration['dbname']


def runtests():
    '''
    Recreating schema is necessary as test may left DB in
    incosistent state.

    '''
    result = local('python setup.py nosetests')
    server_drop_schema()
    server_create_schema()
    if result.failed:
        abort('Tests failed')


def configure_db_server():
    '''
    Bootstrapping Postgresql and needed packages on a remote host.

    Supports only Debian/Ubuntu
    If the Dev server is self opened for ssh it can be configured as well.

    '''
    with settings(warn_only=True):
        fabtools.deb.update_index()
    fabtools.require.postgres.server()
    fabtools.require.postgres.user(dbusername, password=dbpassword)
    fabtools.require.postgres.database(dbname, owner=dbusername)
    postgres_conf = files.first(
        '/etc/postgresql/9*/main/pg_hba.conf'
    )
    postgres_listen_conf = files.first(
        '/etc/postgresql/9*/main/postgresql.conf'
    )
    if not postgres_conf or not postgres_listen_conf:
        abort('Could not find Postgresql configuration file')
    files.append(
        postgres_conf,
        'host    all             all             0.0.0.0/0               md5',
        use_sudo=True
    )
    files.append(
        postgres_listen_conf,
        "listen_addresses = '*'",
        use_sudo=True
    )
    sudo("service postgresql restart")


def server_create_schema():
    '''
    Creates DB objects that are not yet exist in the database.

    '''
    create_schema()


def server_drop_schema():
    '''
    Dangerous, run only on dev and staging.

    '''
    drop_schema()


def create_virtualenv():
    fabtools.require.user(DEPLOY_USERNAME, create_home=False, shell='/bin/false')
    if fabtools.files.is_dir(DEPLOY_ENV_PATH):
        fabtools.files.remove(
            DEPLOY_ENV_PATH,
            recursive=True,
            use_sudo=True
        )
    fabtools.require.directory(
        DEPLOY_ENV_PATH,
        use_sudo=True
    )
    fabtools.require.deb.package('python-pip', update=True)
    fabtools.require.deb.package('python-virtualenv', update=True)
    fabtools.require.deb.package('build-essential')
    fabtools.require.deb.package('python-dev')
    fabtools.require.deb.package('cython')
    fabtools.require.python.virtualenv(
        DEPLOY_ENV_PATH,
        use_sudo=True,
        clear=True
    )


def install_into_virtualenv():
    local('rm -rf dist')
    local('python setup.py sdist')
    fabtools.require.directory(DEPLOY_TMP_PATH)
    copied_files = put('dist/*.tar.gz', DEPLOY_TMP_PATH)
    sdist_file = copied_files[0]
    with fabtools.python.virtualenv(DEPLOY_ENV_PATH):
        sudo('pip install {}'\
                .format(
                    os.path.join(DEPLOY_TMP_PATH, os.path.basename(sdist_file))
                )
            )


def create_upstart_file():
    fabtools.require.files.file(
        path=DEPLOY_UPSTART_FILE,
        contents='''description "Unique UINTs dispenser service - PEZ"

start on stopped rc RUNLEVEL=[345]
stop on runlevel [!345]

env PEZ_DB_NAME="{dbname}"
env PEZ_DB_HOST="{dbhost}"
env PEZ_DB_USERNAME="{dbusername}"

# better use start-stop-daemon instead of built-in gunicorn --daemon or --user
# arguments as the control process is still would be runnning as root

exec start-stop-daemon --chuid {pezuser} --exec {gunicorn_bin} --start -- --bind=0.0.0.0:{bind_port} pez.webapp

respawn
'''.format(
            gunicorn_bin=GUNICORN_BIN,
            bind_port=DEPLOY_SERVICE_PORT,
            pezuser=DEPLOY_USERNAME,
            **configuration
        ),
        use_sudo=True,
    )


def start_service():
    if not fabtools.service.is_running(DEPLOY_SERVICE_NAME):
        fabtools.service.start(DEPLOY_SERVICE_NAME)


def stop_service():
    if fabtools.service.is_running(DEPLOY_SERVICE_NAME):
        fabtools.service.stop(DEPLOY_SERVICE_NAME)


def verify_deployment():
    response = run('curl -s http://localhost:{bind_port}/v1/forward'\
        .format(bind_port=DEPLOY_SERVICE_PORT)
    )
    print 'Response body: "{}"'.format(response)
    try:
        uint = int(response, 10)
        assert uint >= 1
    except (ValueError, AssertionError):
        abort('Got invalid response from the service')


def deploy():
    stop_service()
    create_virtualenv()
    install_into_virtualenv()
    create_upstart_file()
    start_service()
    print 'Waiting for service to start'
    time.sleep(5)
    verify_deployment()

