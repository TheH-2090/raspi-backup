#!/bin/env -S python3 -u

'''
    raspi-backup.py | Create or restore a backup of your Raspberry Pi OS using tar and pigz.
    Copyright (C) 2021  https://github.com/TheH-2090

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, visit www.gnu.org/licenses/
'''

from os import getcwd, getuid
from sys import argv, stdout
import apt, subprocess, getpass



def help():
    print('''Usage:
    raspi-backup.py <action> <source> <target>

    actions
    --help\tPrint this help
    --backup\tBackup source directory to target(.tar.gz)
    --restore\tRestore source(.tar.gz) to target directory
    ''')
    quit()

def disclaimer():
    disclaimer = [
    'raspi-backup.py  Copyright (C) 2021  https://github.com/TheH-2090',
    'This program comes with ABSOLUTELY NO WARRANTY; for details add --warranty.',
    'This is free software, and you are welcome to redistribute it',
    'under certain conditions.',
    '',
    'You should have received a copy of the GNU General Public License',
    'along with this program.  If not, visit https://www.gnu.org/licenses/.',
    ]
    max_length = max([len(line) for line in disclaimer])
    print(max_length * '*')
    print('\n'.join(disclaimer))
    print(max_length * '*')

def show_warranty():
    print('''
        Disclaimer of Warranty.
    THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
    APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
    HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
    OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
    THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
    PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
    IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
    ALL NECESSARY SERVICING, REPAIR OR CORRECTION.

        Limitation of Liability.
    IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
    WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MODIFIES AND/OR CONVEYS
    THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY
    GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE
    USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF
    DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD
    PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS),
    EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF
    SUCH DAMAGES.

        Interpretation of Sections above.
    If the disclaimer of warranty and limitation of liability provided
    above cannot be given local legal effect according to their terms,
    reviewing courts shall apply local law that most closely approximates
    an absolute waiver of all civil liability in connection with the
    Program, unless a warranty or assumption of liability accompanies a
    copy of the Program in return for a fee.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, visit https://www.gnu.org/licenses/.
    ''')
    quit()

def final_confirmation(source, action, target):
    confirmation_message = [
        f'Everything set to {action} {source} to {target}.',
    ]
    if action == 'restore':
        confirmation_message.append(f'PLEASE NOTE: Everything in {target} will be deleted.')
    max_length = max([len(line) for line in confirmation_message])
    confirmation_message.insert(0, max_length * '*')
    confirmation_message.append(max_length * '*')
    return confirm('\n'.join(confirmation_message))

def check_privileges():
    print('Checking privileges...', end='')
    if getuid() != 0:
            print('error')
            print('Elevated privileges needed.\nPlease run as admin or with sudo.')
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
    if '--warranty' in parameters:
        show_warranty()
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

def confirm(message):
    options = ['no', 'yes']
    confirmation = make_selection(options, message)
    return confirmation == 'yes'

def make_selection(options, message):
    options_dict = {}
    options_list = []
    output = f'{message}'
    for pos, option in enumerate(options):
        options_dict[pos] = option
        options_list.append(pos)
        output += (f'\n[{str(pos)}]\t{option}')
    while True:
        error_occured = False
        print(output)
        selection = input('Make selection to proceed or (c)ancel: ')
        print('')
        if selection.lower() == 'c':
            print('Info: Canceled on user request. Exiting')
            quit()
        else:
            try:
                selection = int(selection)
                if selection in options_list:
                    return options_dict[selection]
                else:
                    error_occured = True
            except ValueError as e:
                error_occured = True
        if error_occured:
            print('Error: Option could not be evaluated')

def execute_single(command, verbose=True):
    task = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL if not(verbose) else stdout, universal_newlines=True)
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
        'delete': f'rm {target}/* -r',
    }
    apt_cache = apt.Cache()
    if apt_cache['pigz'].is_installed:
        compressor = 'pigz'
        has_pigz = True
    else:
        has_pigz = False
        compressor = 'gzip'
        print(f'By installing pigz the speed of the {action} can be improved. Using gzip as alternative.')
    has_pv = apt_cache['pv'].is_installed
    if not(has_pv):
        print('By installing pv a statusbar will be shown. Listing processed files instead.')
    commands['backup'] = f'tar -cp{"" if has_pv else "v"} -I {compressor} -C {source} {" ".join(exclusions)} ./ -f {"- | pv > " if has_pv else ""} {target}'
    commands['restore'] = f'{"pv " + source + " |" if has_pv else ""} tar -xp{"" if has_pv else "v"} -I {compressor} -f {"-" if has_pv else source} -C {target}'

    options = ""
    if not(has_pigz):
        options += "pigz "
        if not(has_pv):
            options += "and pv "
    else:
        if not(has_pv):
            options += "pv "
    if not(has_pigz & has_pv):
        getpass.getpass(f'Abort with <ctrl> + <c> to install {options}for best user experience or proceed with <enter>.')
    if action == 'restore':
        print(f'Deleting {target}/*...', end='')
        execute_single(commands['delete'], False)
        print('DONE')
    return execute_single(commands[action])


if __name__ == '__main__':
    disclaimer()
    process = setup_process(argv)
    check_privileges()
    proceed = final_confirmation(process['source'], process['action'], process['target'])
    if not(proceed):
        print('Info: Process not confirmed. Exiting.')
        quit()
    else:
        if execute(process):
            output = f"{process['source']} {process['action']} to {process['target']} successful."
            print(len(output) * '*')
            print(output)
            print(len(output) * '*')
