#!/bin/env python3

from os import getcwd, getuid
import subprocess
from sys import argv, stderr
import apt

def help():
    print('''Usage:
    raspi-backup.py <action> <source> <target>

    actions
    --help\tPrint this help
    --backup\tBackup source directory to target(.tar.gz)
    --restore\tRestore source(.tar.gz) to target directory
    ''')
    quit()

def check_privileges():
    print('Checking privileges...', end='')
    if getuid() != 0:
            print('error')
            print('Elevated privileges needed.\nPlease run as admin or with sudo.')
            quit()
    else:
        print('OK')

def check_requirements():
    cache = apt.Cache()
    print('Checking if tar is installed...', end='')
    if not(cache['tar'].is_installed):
        print('error')
        print('Tar is not installed.\nPlease install tar to use raspi-backup.')
        quit()
    else:
        print('OK')
    print('Checking if pigz is installed...', end='')
    if not(cache['pigz'].is_installed):
        print('error')
        print('Pigz is not installed.\nPlease install pigz to use raspi-backup.')
        quit()
    else:
        print('OK')

def relative_path_to_absolute(path):
    return path if path[0] == '/' else getcwd() + '/' + path

def setup_process(parameters=argv):
    process = {
        'action': 'undefined',
        'source': 'undefined',
        'target': 'undefined',
    }
    if '--help' in parameters:
        help()
    parameters = parameters[1:]
    if len(parameters) == 3:
        process['action'] = parameters.pop(0).strip('--')
        process['source'] = parameters.pop(0)
        process['target'] = parameters.pop(0)
    elif len(parameters) < 3:
        print('Missing parameters')
        help()
    elif len(parameters) > 3:
        print('Too many parameters')
        help()
    process['source'] = relative_path_to_absolute(process['source'])
    process['target'] = relative_path_to_absolute(process['target'])
    if process['action'] == 'backup':
        if len(process['source'].split('.')) >= 2:
            if process['source'].split('.')[-2] == 'tar' and process['source'].split('.')[-1] == 'gz':
                print('Cannot specify .tar.gz file as source for backup')
                help()
        if len(process['target'].split('.')) >= 2:
            if process['target'].split('.')[-2] != 'tar' and process['target'].split('.')[-1] != 'gz':
                print('A .tar.gz file has to be specified as target')
                help()
    elif process['action'] == 'restore':
        if len(process['source'].split('.')) >= 2:
            if process['source'].split('.')[-2] != 'tar' and process['source'].split('.')[-1] != 'gz':
                print('A .tar.gz file has to be set as source to restore')
                help()
        if len(process['target'].split('.')) >= 2:
            if process['target'].split('.')[-2] == 'tar' and process['target'].split('.')[-1] == 'gz':
                print('Cannot specify .tar.gz file as target to restore')
                help()
    else:
        print('Action could not be identified')
        help()
    return process

def execute_single(command, verbose=True):
    task = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if verbose:
        for stdout_line in iter(task.stdout.readline, ""):
            print(stdout_line, end="")
        task.stdout.close()
    return_code = task.wait()
    if verbose:
        if return_code:
            raise subprocess.CalledProcessError(return_code, command)
        return True

def execute(process):
    action = process['action']
    source = process['source']
    target = process['target']
    target_dir = '/'.join(target.split('/')[:2])
    exclusions = [
        '--exclude=./proc/*',
        '--exclude=./tmp/*',
        '--exclude=./mnt/*',
        '--exclude=./dev/*',
        '--exclude=./sys/*',
        '--exclude=./run/*',
        '--exclude=./media/*',
        '--exclude=./var/log/*',
        '--exclude=./var/cache/apt/archives/*',
        '--exclude=./usr/src/linux-headers*',
        '--exclude=./home/*/.gvfs/*',
        '--exclude=./home/*/.cache/*'
        '--exclude=./home/*/.local/share/Trash/*'
        f'--exclude=.{target_dir}/*',
        f'--exclude=.{target}',
    ]
    
    commands = {
        'backup': f"tar -cpv -I pigz -C {source} {' '.join(exclusions)} ./ -f {target}",
        'delete': f'rm {target}/*',
        'restore': f'tar -xpv -I pigz -f {source} -C {target}',
    }
    if action == 'restore':
        print(f'Deleting {target}/*...', end='')
        execute_single(commands['delete'], False)
        print('DONE')
    return execute_single(commands[action])


if __name__ == '__main__':
    check_privileges()
    check_requirements()
    process = setup_process(argv)
    if execute(process):
        output = f"{process['source']} {process['action']} to {process['target']} successful."
        print(len(output) * '*')
        print(output)
        print(len(output) * '*')
