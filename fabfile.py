import os
import datetime
from contextlib import contextmanager
from tempfile import mkdtemp
from fabric.api import cd, env, get, local, prefix, run, settings, sudo, task
from fabric.operations import put

CHEF_VERSION = '10.20.0'

branch = 'master'
project = "wagtaildemo"
app = "wagtaildemo"

env.code_dir = '/home/vagrant/wagtaildemo'


env.root_dir = "/usr/local/apps/%s" % project
env.venvs = '/usr/local/venv'
env.virtualenv = '/home/vagrant/.virtualenvs/wagtaildemo'
env.activate = 'source %s/bin/activate ' % env.virtualenv

env.media_dir = '%s/media' % env.root_dir
env.key_filename = '~/.ssh/id_rsa'


@contextmanager
def _virtualenv():
    with prefix(env.activate):
        yield


def _manage_py(command):
    run('python manage.py %s' % command)


@task
def install_chef(latest=True):
    """
    Install chef-solo on the server
    """
    sudo('apt-get update', pty=True)
    sudo('apt-get install -y git-core rubygems ruby ruby-dev', pty=True)
    sudo('gem install chef --no-ri --no-rdoc', pty=True)


def parse_ssh_config(text):
    """
    Parse an ssh-config output into a Python dict.

    Because Windows doesn't have grep, lol.
    """
    try:
        lines = text.split('\n')
        lists = [l.split(' ') for l in lines]
        lists = [filter(None, l) for l in lists]

        tuples = [(l[0], ''.join(l[1:]).strip().strip('\r')) for l in lists]

        return dict(tuples)

    except IndexError:
        raise Exception("Malformed input")


def set_env_for_user(user='example'):
    if user == 'vagrant':
        # set ssh key file for vagrant
        result = local('vagrant ssh-config', capture=True)
        data = parse_ssh_config(result)

        try:
            env.user = user
            env.host_string = 'vagrant@127.0.0.1:%s' % data['Port']
            env.key_filename = data['IdentityFile'].strip('"')
        except KeyError:
            raise Exception("Missing data from ssh-config")


# @task
# def loaddata(fname='demo/fixtures/initial_data.json'):
#     """
#     Loads data from local fixtures file. By defult it loads apps/survey/fixtures/surveys.json.gz
#     You can use 'fab vagrant loaddata:PATH_TO_FIXTURE_FILE' to load a specific file.
#     """
#     set_env_for_user('vagrant')
#     with cd(env.code_dir):
#         with _virtualenv():
#             _manage_py('loaddata %s' %(fname))


# @task
# def dumpdata(fname='data.json'):
#     with cd('/home/vagrant/wagtaildemo/'):
#         run('ls')
#         _manage_py('dumpdata --format=json --indent=4  wagtailcore.page demo.multilingualpage demo.langrootpage demo.spanishhomepage demo.englishhomepage > backups/%s' % (fname))

@task
def backup_db(dbname='wagtaildemo'):
    # pg_dump wagtaildemo -n public -c -f backups/____FILENAME____ -Fc -O -no-acl -U postgres
    date = datetime.datetime.now().strftime("%Y-%m-%d%H%M")
    dump_name = "%s-%s.dump" % (date, dbname)
    run("pg_dump %s -n public -c -f /tmp/%s -Fc -O -no-acl -U postgres" % (dbname, dump_name))
    get("/tmp/%s" % dump_name, "backups/%s" % dump_name)

@task
def restore_db(dump_name):
    # pg_restore --verbose --clean --no-acl --no-owner -U postgres -d wagtaildemo backups/____FILENAME____
    put(dump_name, "/tmp/%s" % dump_name.split('/')[-1])
    run("pg_restore --verbose --clean --no-acl --no-owner -U postgres -d wagtaildemo /tmp/%s" % dump_name.split('/')[-1])
    #run("cd %s && %s/bin/python manage.py migrate --settings=config.environments.staging" % (env.app_dir, env.venv))


@task
def runserver():
    set_env_for_user('vagrant')
    with cd(env.code_dir):
        with _virtualenv():
            _manage_py('runserver 0.0.0.0:8000')

@task
def restart():
    """
    Reload nginx/gunicorn
    """
    with settings(warn_only=True):
        sudo('initctl stop app')
        sudo('initctl start app')
        sudo('/etc/init.d/nginx reload')


@task
def vagrant(username='vagrant'):
    # set ssh key file for vagrant
    set_env_for_user(username)
    result = local('vagrant ssh-config', capture=True)
    data = parse_ssh_config(result)
    env.remote = 'vagrant'
    env.branch = branch
    env.host = '127.0.0.1'
    env.port = data['Port']
    env.code_dir = '/home/vagrant/wagtaildemo'
    env.app_dir = '/vagrant'
    env.venv = '/home/vagrant/.virtualenvs/wagtaildemo'
    env.settings = 'config.environments.development'
    env.db_user = 'vagrant'

    try:
        env.host_string = '%s@127.0.0.1:%s' % (username, data['Port'])
    except KeyError:
        raise Exception("Missing data from ssh-config")
