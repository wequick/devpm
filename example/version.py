"""devpm"""
# -*- coding:utf-8 -*-

# This file is part of devpm.
#
# Copyright (c) 2023 wequick
# This software is distributed under the MIT license.

# Update project.toml version


import os
import re
import sys
import subprocess
import toml


def update_toml(root: str, new_version: str) -> None:
    path = os.path.join(root, 'pyproject.toml')
    changed = False
    data = {}
    with open(path, 'r', encoding='utf-8') as file:
        data = toml.load(file)
        old_version = data['project']['version']
        data['project']['version'] = new_version
        changed = old_version != new_version
    
    if changed:
        with open(path, 'w', encoding='utf-8') as file:
            toml.dump(data, file)


def update_changelog(root: str, new_version: str) -> None:
    args = ['git-changelog', '-c', 'conventional', '-t', 'keepachangelog', '-b']
    try:
        output = subprocess.check_output(args, shell=False).decode('utf-8').strip()
        # Replace following ${version}
        #   <!-- insertion marker -->
        #   ## [${version}](https://***/${version}) - 2023-07-24
        #   <small>[Compare with 1.1.1](https://***/1.1.1...${version})</small>
        found_insertion_marker = False
        insertion_marker = '<!-- insertion marker -->'
        complete = False
        content = ''
        for line in output.splitlines():
            if complete:
                content += line + '\n'
                continue
            if not found_insertion_marker:
                found_insertion_marker = insertion_marker in line
                content += line + '\n'
                continue
            else:
                complete = '<small>' in line
                if complete:
                    line = re.sub(r"(.+)\.\.\.(.+)\)</small>",
                                  f"\\1...{new_version})</small>", line)
                else:
                    line = re.sub(r"## \[(.+)\]\((.+)/(.+)\)(.+)",
                                  f"## [{new_version}](\\2/{new_version})\\4", line)
                content += line + '\n'

        with open(os.path.join(root, 'CHANGELOG.md'), 'w', encoding='utf-8') as file:
            file.write(content)
    except:
        pass


def main():
    if len(sys.argv) < 2:
        exit(1)

    new_version = sys.argv[1]
    root = os.getcwd()

    update_toml(root, new_version)

    update_changelog(root, new_version)


if __name__ == '__main__':
    main()
