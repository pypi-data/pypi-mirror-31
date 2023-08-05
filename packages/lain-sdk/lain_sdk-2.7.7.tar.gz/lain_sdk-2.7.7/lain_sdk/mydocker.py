#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getpass
import os
import os.path
import pwd
import random
import shutil
import string
import tempfile
import requests
import subprocess
import docker
from jinja2 import Template
from .util import (info, error,
                   recur_create_file, rm,
                   parse_registry_auth, get_jwt_for_registry,
                   REGISTRY_CONNECT_TIMEOUT, REGISTRY_READ_TIMEOUT)
from .yaml.conf import DOCKER_APP_ROOT, LAIN_CACHE_DIR


DOCKER_BASE_URL = os.environ.get('DOCKER_HOST', '')

# Assume `docker` can be run without `sudo`

# docker_reg set through param or env LAIN_DOCKER_REGISTRY


def _docker(args, cwd=None, env=os.environ, capture_output=False, print_stdout=True):
    """
    Wrapper of Docker client. Use subprocess instead of docker-py to
    avoid API version inconsistency problems.

    Args:
        args: Argument list to pass to Docker client.
        cwd: Current working directory to run Docker under.
        env: Environemnt variable dict to pass to Docker client.

    Returns:
        Combined output of stdout + stderr, or return code (int).

    Raises:
        None.
    """

    cmd = ['docker'] + args
    env = dict(env, DOCKER_HOST='')

    if capture_output:
        try:
            output = subprocess.check_output(
                cmd, env=env, cwd=cwd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            output = e.output
        return output
    else:
        retcode = subprocess.call(cmd, env=env, cwd=cwd, stderr=subprocess.STDOUT,
                                  stdout=(None if print_stdout else open('/dev/null', 'w')))
        return retcode


def gen_image_name(appname, phase, meta_version=None, docker_reg=None):
    """
    {docker_reg}/{appname}:{phase}-{meta_version}
    """
    ret = '%s:%s' % (appname, phase)
    if meta_version is not None:
        ret = '%s-%s' % (ret, meta_version)
    if docker_reg is None:
        docker_reg = os.environ.get('LAIN_DOCKER_REGISTRY', None)
    if docker_reg is not None:
        ret = '%s/%s' % (docker_reg, ret)
    return ret


def get_phase(img_name):
    return img_name.split(':')[1].split('-')[0]


def gen_dockerfile(dockerfile_path, template, dockerfile_params):
    info('generating dockerfile to {}'.format(dockerfile_path))

    recur_create_file(dockerfile_path)

    with open(dockerfile_path, 'w') as f:
        f.write(Template(template).render(dockerfile_params))


def gen_dockerignore(path, ignore):
    backup_path = os.path.join(os.path.dirname(path), '.dockerignore.backup')
    gitignore_path = os.path.join(os.path.dirname(path), '.gitignore')
    if os.path.exists(path):
        shutil.copy(path, backup_path)
    else:
        try:
            shutil.copy(gitignore_path, path)
        except IOError:
            pass
    with open(path, 'a') as f:
        f.write('# Appended by lain\n')
        for p in ignore:
            f.write(p + '\n')
        f.write('# end of lain\n')


def build_image(name, context, build_args, use_cache):
    info('building image {} ...'.format(name))
    if use_cache:
        docker_args = ['build', '-t', name, '.']
    else:
        docker_args = ['build', '-t', name, '--no-cache', '.']

    if build_args:
        docker_args = ['build', '-t', name]
        for arg in build_args:
            key, val = arg.split('=', 1)
            if val.startswith('$'):
                val = os.environ[val[1:]]
            docker_args.append('--build-arg')
            docker_args.append('{}={}'.format(key, val))
        docker_args.append('.')
    retcode = _docker(docker_args, cwd=context)
    if retcode != 0:
        name = None
        error('build failed. See errors above.')
    else:
        info('build succeeded: {}'.format(name))
    return name


def build(name, context, ignore, template, params, build_args, use_cache=True):
    dockerfile_path = os.path.join(context, 'Dockerfile')
    dockerignore_path = os.path.join(context, '.dockerignore')
    dockerignore_backup = os.path.join(context, '.dockerignore.backup')
    try:
        gen_dockerfile(dockerfile_path, template, params)
        gen_dockerignore(dockerignore_path, ignore)
        name = build_image(name, context, build_args, use_cache)
    finally:
        for path in [dockerfile_path, dockerignore_path]:
            if os.path.exists(path):
                rm(path)
        if os.path.exists(dockerignore_backup):
            shutil.move(dockerignore_backup, dockerignore_path)
    return name


def compile_by_docker(build_image_name, base_image_name, context, volumes, script):
    info('building image {} ...'.format(build_image_name))
    files = subprocess.check_output(['find', '.', '-maxdepth', '1',
                           '!', '-path', './{}'.format(LAIN_CACHE_DIR),
                           '!', '-path', '.' ],
                          cwd=context).strip().split('\n')
    subprocess.check_call(['mkdir', '-p',
                           '{}{}'.format(LAIN_CACHE_DIR, DOCKER_APP_ROOT)],
                          cwd=context)
    subprocess.check_call(['cp', '-rf', '-t',
                           '{}{}'.format(LAIN_CACHE_DIR, DOCKER_APP_ROOT)] + files,
                          cwd=context)

    container_name = build_image_name.replace(':', '_')
    container_name += '-'
    container_name += ''.join(random.choice(string.digits) for _ in range(3))
    docker_args = ['run', '-w', DOCKER_APP_ROOT, '--name', container_name,
                   '--entrypoint', '/bin/bash']
    user = pwd.getpwnam(getpass.getuser())
    for v in volumes + [DOCKER_APP_ROOT]:
        docker_args += ['-v', '{}/{}{}:{}'.format(context, LAIN_CACHE_DIR, v, v)]
        script.append('(chown -R {}:{} {})'.format(user.pw_uid, user.pw_gid, v))
    docker_args += [base_image_name, '-c', ' && '.join(script)]
    info('docker {}...'.format(' '.join(docker_args)))
    try:
        run_retcode = _docker(docker_args, cwd=context)
        commit_retcode = _docker(['commit', container_name, build_image_name], print_stdout=False)
        if run_retcode != 0 or commit_retcode != 0:
            error('docker {} failed.'.format(' '.join(docker_args)))
            error('build failed: {}'.format(build_image_name))
            exit(1)

        info('docker {} succeed.'.format(' '.join(docker_args)))
        info('build succeed: {}'.format(build_image_name))
    finally:
        _docker(['rm', '-f', container_name], print_stdout=False)

    return build_image_name


def remove_container(container_id):
    info('removing container {} ...'.format(container_id))
    _docker(['kill', container_id])
    _docker(['rm', '-f', container_id])


def copy_to_host(image_name, release_copy, host_dir, context=None, volumes=None):
    '''
    release_copy: release.copy in lain.yaml
    '''
    src_dest = [(__normalize_path_in_container(x.get('src')),
                 '{}{}'.format(host_dir, __normalize_path_in_container(x.get('dest'))))
                for x in release_copy]

    scripts = []
    for x in src_dest:
        scripts.append('(mkdir -p {})'.format(os.path.dirname(x[1])))
        scripts.append('(cp -r {} {})'.format(x[0], x[1]))
    user = pwd.getpwnam(getpass.getuser())
    scripts.append('(chown -R {}:{} {})'.format(user.pw_uid, user.pw_gid, host_dir))
    docker_args = ['run', '--rm', '--entrypoint', '/bin/sh',
                   '-v', '{}:{}'.format(host_dir, host_dir)]
    if context is not None and volumes is not None:
        for v in volumes + [DOCKER_APP_ROOT]:
            docker_args += ['-v', '{}/{}{}:{}'.format(context, LAIN_CACHE_DIR, v, v)]
    docker_args += [image_name, '-c', ' && '.join(scripts)]
    retcode = _docker(docker_args, cwd=context)
    if retcode != 0:
        exit(1)


def __normalize_path_in_container(path):
    if path.startswith('$'):  # It starts with an environment variable, so keep unchanged
        return path

    return os.path.join(DOCKER_APP_ROOT, path)


def remove_none_repo():
    dangling_images = _docker(
        ['images', '-q', '-f', 'dangling=true'], capture_output=True
    ).splitlines()
    for image in dangling_images:
        _docker(['rmi', image])


def remove_explicit_exited_containers():
    exited_containers = _docker(
        ['ps', '-q', '-a', '-f', 'status=exited'], capture_output=True
    ).splitlines()
    for container in exited_containers:
        _docker(['rm', container])


def remove_image(name):
    info('removing {}'.format(name))
    remove_explicit_exited_containers()
    remove_none_repo()
    _docker(['rmi', '-f', name])


def commit(container_id, name):
    container_id = container_id.strip()
    info('committing id: {} to image: {}'.format(container_id, name))
    _docker(['commit', container_id, name])


def enter(name):
    info('enter image {}'.format(name))
    _docker(['run', '-it', name, '/bin/bash'])


def proc_run(container_name, image, working_dir, port, cmd, envs, volumes):
    info('run proc {} with image {}'.format(container_name, image))
    working_dir_opt = ['-w', working_dir] if working_dir else []
    port_opt = ['-p', str(port)] if port else []
    env_opt = sum([['-e', env] for env in envs], [])
    volume_opt = sum([
        ['-v', '{}:{}'.format(k, v)]
        for k, v in volumes.iteritems()
    ], [])
    docker_args = ['run', '-d', '--name={}'.format(container_name)] \
        + working_dir_opt + port_opt + env_opt + volume_opt + [image] + cmd
    _docker(docker_args)


def proc_debug(container_name):
    info('attach proc instance {}'.format(container_name))
    _docker(['exec', '-it', container_name, 'bash'])


def proc_stop(container_name):
    info('stop proc instance {}'.format(container_name))
    _docker(['stop', container_name])


def proc_rm(container_name, host_volume_base):
    info('rm proc instance {}'.format(container_name))
    _docker(['rm', '-v', container_name])
    info('rm proc instance volume at host: {}'.format(host_volume_base))
    subprocess.call(['rm', '-rf', host_volume_base])


def inspect(container_name):
    output = _docker(['inspect', container_name], capture_output=True)
    info(output)


def inspect_port(container_name):
    info('port mapping:')
    output = _docker(['port', container_name], capture_output=True)
    info(output)


def tag(src, dest):
    info('tag {} as {}'.format(src, dest))
    retcode = _docker(['tag', src, dest])
    return retcode


def exist(name):
    retcode = _docker(['inspect', name], print_stdout=False)
    return retcode == 0


def pull(name):
    info('pulling image %s ...' % name)
    retcode = _docker(['pull', name])
    return retcode


def push(name):
    info('pushing image %s ...' % name)
    retcode = _docker(['push', name])
    return retcode


def login(username, password=None, registry=None):
    need_auth, auth_url = parse_registry_auth(registry)
    if not need_auth:
        return True

    retcode = _docker(['login', '-u', username, '-p', password, registry])
    if retcode == 0:
        return True

    return False


def logout(registry=None):
    need_auth, auth_url = parse_registry_auth(registry)
    if not need_auth:
        return
    _docker(['logout', registry])


def get_tag_list_in_registry(registry, appname):
    tag_list_url = "http://%s/v2/%s/tags/list" % (registry, appname)
    need_auth, auth_url = parse_registry_auth(registry)
    if need_auth:
        jwt = get_jwt_for_registry(auth_url, registry, appname)
        headers = {'Authorization': 'Bearer %s' % jwt}
    else:
        headers = None
    try:
        r = requests.get(tag_list_url, headers=headers,
                         timeout=(REGISTRY_CONNECT_TIMEOUT, REGISTRY_READ_TIMEOUT))
        return r.json()['tags']
    except:
        return []


def get_tag_list_in_docker_daemon(registry, appname):
    tag_list = []
    c = docker.from_env()
    imgs = c.images.list()
    for img in imgs:
        repo_tags = img.tags
        if not repo_tags:
            continue
        for repo_tag in repo_tags:
            try:
                s_list = repo_tag.split(":")
                tag = s_list[-1]
                repo = ":".join(s_list[:-1])
                if repo == "%s/%s" % (registry, appname) and tag not in tag_list:
                    tag_list.append(tag)
            except Exception as e:
                print(e)
    return tag_list


def get_tag_list_using_by_containers(registry, appname):
    tag_list = []
    c = docker.from_env()
    containers = c.containers.list()
    for container in containers:
        repo, tag = container.attrs['Config']['Image'].split(":")
        if repo == "%s/%s" % (registry, appname) and tag not in tag_list:
            tag_list.append(tag)
    return tag_list


def get_image(image_name):
    c = docker.from_env()
    return c.images.get(image_name)
