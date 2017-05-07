from os import path
from fabric.api import env
from fabistrano import deploy

env.hosts = '203.117.155.190'
env.user = 'ld-zhangys'
env.base_dir = '/home/ld-sgdev/zhangys/apps'
env.app_name = 'test_app'
env.git_clone = 'ssh://git@104.236.178.248:/home/git/cs5344-project.git'

env.use_sudo = False
env.update_env = False
env.deploy_via = 'local_clone'
