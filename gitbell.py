#!/usr/bin/env python3

from dataclasses import replace
import os
import subprocess
import re
import json
import requests
import argparse

API_RELEASE = 'https://api.github.com/repos/{repo}/releases/latest'

parser = argparse.ArgumentParser(description='Git Package Manager')
parser.add_argument('--package','-p', dest='package_json', 
                    default='packages.json',
                    help='Package json file')
parser.add_argument('--skip-remote','-s', dest='skip_remote', 
                    action='store_true',
                    default=False,
                    help='Skip checking Remote versions')

def colorprint(text, **kwargs):
    print(f'\033[1;32m{text}\033[0m',**kwargs)

def exec_cmd(cmd_list):
    process = subprocess.Popen(cmd_list, 
                            stdout=subprocess.PIPE,
                            universal_newlines=True)
    while True:
        output = process.stdout.readline()
        break

    return output.strip()


def get_installed(cmd):

    out = exec_cmd(cmd)
    pattern = re.compile(r'(\d+\.)?(\d+\.)?(\*|\d+)')
    ver = re.search(pattern, out).group(0)
    return ver

def get_tags(url):
    import git

    g = git.cmd.Git()
    if 'fio' in url:
        refs = g.ls_remote(url,'fio*', sort='-v:refname', tags=True).split('\n')
    else:
        refs = g.ls_remote(url, sort='-v:refname', tags=True).split('\n')

    ver = re.search(r'tags/v?(.+)', refs[0]).group(1)
    ver = re.sub('.*-', '' , ver)
    
    return ver.replace('^{}', '')

def get_latest(url):

    repo = re.search(r'.com\/(.+)',url).group(1)
    r = requests.get(API_RELEASE.format(repo=repo))
    resp = r.text
    try:
        ver = re.search(r'tag_name":"v?(.+?)"',resp).group(1)
    except AttributeError:
        ver = get_tags(url)

    return ver

def get_command(app,app_dict):

    try: 
        executable = app_dict['exe']
    except KeyError:
        executable = app

    try: 
        cmd = [executable, app_dict['ver']]
    except KeyError:
        cmd = [executable, '--version']
    
    return cmd

def get_all(p_list, skip_remote, print_inline=False):

    data = {}
    if print_inline:
        table_header(skip_remote)

    for app in sorted(p_list.keys()):
        data[app] = {}

        cmd = get_command(app, p_list[app])
        data[app]['inst'] = get_installed(cmd)

        if not skip_remote:
            try:
                repo_url = p_list[app]['git']
            except KeyError:
                ver = '-'
            else:
                ver = get_latest(repo_url)
            data[app]['new'] = ver

        if print_inline:
            table_versions(data, skip_remote)
            data={}

    return data

def table_header(skip_remote):
    if not skip_remote:
        colorprint('{:20} {:10} {:10}'.format('App', 'Installed' , 'Latest'))
    else:
        colorprint('{:20} {:10}'.format('App', 'Installed'))

def table_versions(data, skip_remote):
    if not skip_remote:
        for app in data.keys():
            print('{:20} {:10} {:10}'.format(app, 
                                    data[app]['inst'],
                                    data[app]['new']))
    else:
        for app in data.keys():
            print('{:20} {:10}'.format(app,data[app]['inst']))

def load_json(json_file):
    if os.path.isfile(json_file):
        with open("packages.json") as package_file:
            p_list = json.load(package_file)
    else:
        print('File not found')
        exit()
    return p_list

def main():

    args = parser.parse_args()

    p_list = load_json(args.package_json)
    data = get_all(p_list, args.skip_remote)
    table_header(args.skip_remote)
    table_versions(data, args.skip_remote)


if __name__ == '__main__':
    main()