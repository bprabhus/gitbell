#!/usr/bin/python3

import re
import json
import requests
import subprocess

with open("packages.json") as f:
    packages_list = json.load(f)


# for item in repolist.keys():
#     rpath = repolist[item]['git']
#     repo = re.findall(r'.com\/(.+)',rpath)[0]
#     r = requests.get(f'https://api.github.com/repos/{repo}/releases/latest')
#     resp = r.text
#     ver = re.findall(r'tag_name":"(.+?)"',resp)
#     print(repo, ver)

def exec_cmd(cmd_list):
    # Exec command to get installed version

    process = subprocess.Popen(cmd_list, 
                            stdout=subprocess.PIPE,
                            universal_newlines=True)
    while True:
        output = process.stdout.readline()
        break

    return output.strip()


def get_ver(tool_dict):
    # Returns dict of installed versions for the tools in dict

    installed_ver = {}

    for item in tool_dict.keys():
        try: 
            cmd_list = [item, tool_dict[item]['cmd']]
        except KeyError:
            cmd_list = [item, '--version']

        installed_ver[item] = exec_cmd(cmd_list)

    return installed_ver



# Gather installed versions
installed_ver = get_ver(packages_list)

# Display installed versions
print('{:<20} {:<20}'.format('Package', 'Installed Version'))
for package,ver in installed_ver.items():
    print('{:<20} {:<20}'.format(package, ver))