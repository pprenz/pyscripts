import os
from time import sleep
from fabric.api import env, run, cd, sudo, local

service_conventions = {
    'tornado': 'so1web%d',
    'django':  'so1feedback%d'
}

services = {
    'so1web@ubm01': {
        'tornado': 2,
        'django':  1
    },
    
    'so1web@cloud0.schoolofone.net': {
        'tornado': 4,
        'django':  1
    },

    'so1web@cloud1.schoolofone.net': {
        'tornado': 4,
        'django':  1
    },

    'so1web@cloud2.schoolofone.net': {
        'tornado': 8,
        'django':  1
    },
   
     'so1web@cloud3.schoolofone.net': {
        'tornado': 8,
        'django':  1
    },

}

env.roledefs = {
    'test': ['so1web@ubm01'],
    'prod': ['so1web@cloud0.schoolofone.net', 
             'so1web@cloud1.schoolofone.net',
             'so1web@cloud2.schoolofone.net' ,
             'so1web@cloud3.schoolofone.net']
}

if not env.roles:
    env.roles = ['test']

def _service_iterator(service_type):
    for host in env.all_hosts:
        print host
        for i in range(1, services[host][service_type] + 1):
            yield service_conventions[service_type] % i

def git_push(remote=None, branch=None):
    remote = remote or 'origin'
    branch = branch or 'master'
    local('git push %s %s' % (remote, branch), capture=False)

def deploy(branch=None):
    branch = branch or 'master'
    with cd('deployed/portal'):
        run('git pull origin %s' % branch)
        run('git reset --hard')

def puppet():
    sudo('/usr/sbin/puppetd --test')

def migrate():
    with cd('deployed/portal'):
        run('source etc/so1feedback_env.sh && ./bin/so1feedback migrate')
    
def migratedb(app=None):
    app = app or 'survey'
    with cd('deployed/portal'):
        run('source etc/so1feedback_env.sh && ./bin/so1feedback migrate %s' % app)
    
def restart(service_type):
    for service in _service_iterator(service_type):
        sudo('/sbin/restart %s' % service)
        sleep(2)

def status(service_type):
    for service in _service_iterator(service_type):
        sudo('/sbin/status %s' % service)

def stop(service_type):
    for service in _service_iterator(service_type):
        sudo('/sbin/stop %s' % service)

def start(service_type):
    for service in _service_iterator(service_type):
        sudo('/sbin/start %s' % service)

def restart_tornado():
    for i in range(1,9):
        sudo('/sbin/restart so1web%d || /sbin/start so1web%d' % (i, i))
    
    sudo('/sbin/restart so1vendors1 || /sbin/start so1vendors1')

def start_tornado():
    for i in range(1,9):
        sudo('/sbin/start so1web%d' % i)

    sudo('/sbin/start so1vendors1')

def stop_tornado():
    for i in range(1,9):
        sudo('/sbin/stop so1web%d' % i)

    sudo('/sbin/stop so1vendors1')

def start_nginx():
    sudo('/etc/init.d/nginx start')

def stop_nginx():
    sudo('/etc/init.d/nginx stop')

def reload_nginx_config():
    sudo('/etc/init.d/nginx reload')

def status_tornado():
    status('tornado')

def clear_data_cache():
    sudo('/sbin/restart memcached-data')

def release(branch=None):
    stop_nginx()
    deploy(branch)
    restart_tornado()
    clear_data_cache()
    minify_js()
    start_nginx()

def minify_js():
    with cd('deployed/portal'):
        run('python bin/concat_js.py')

def enable_maintenance_mode(message=''):
    run('echo "%s" > /var/www/so1live.com/maintenance.html' % message.replace('"', r'\"'))

def disable_maintenance_mode(message=''):
    run('rm /var/www/so1live.com/maintenance.html')

def pre_db_push(message=''):
    enable_maintenance_mode(message)

def post_db_push():
    restart_tornado()
    clear_data_cache()
    #disable_maintenance_mode()



