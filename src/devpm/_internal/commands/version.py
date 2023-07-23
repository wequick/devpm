# -*- coding:utf-8 -*-

# This file is part of devpm.
#
# Copyright (c) 2023 wequick
# This software is distributed under the MIT license.

# devpm pr - pull request

import re
from argparse import ArgumentParser
from dataclasses import dataclass
from devpm._internal.commands.base_run import BaseRunCommand

@dataclass
class VersionInfo:
    major: int
    minor: int
    patch: int


class VersionCommand(BaseRunCommand):
    def add_parser(self, parser: ArgumentParser):
        parser.add_argument('ver', nargs='?', help='<newversion>|major|minor|patch')


    def parse_version(self, s: str) -> VersionInfo:
        results = re.match('(\\d+)\\.(\\d+)\\.(\\d+)', s)
        if not results:
            return VersionInfo(-1, 0, 0)
        return VersionInfo(int(results[1]), int(results[2]), int(results[3]))


    def run(self, args=None):
        git_status = self.context.git.run(['status', '-s'])
        if git_status is None:
            self.context.log.abort('Unknown git status.')
        elif git_status != '':
            self.context.log.abort('Git working directory not clean.')

        config = self.context.load_config()
        config_name = self.context.get_config_name()
        changed = False
        if not 'version' in config:
            self.context.log.abort(f'Missing "version" in {config_name}')
        version_str = config['version']
        if not self.options.ver:
            print(version_str)
            exit(0)

        scripts = {}
        if 'scripts' in config:
            scripts = config['scripts']
        self.run_script(f"pre{self.name}", scripts, config, args)

        if self.options.ver in ['major', 'minor', 'patch']:
            version = self.parse_version(version_str)
            if version.major < 0:
                self.context.log.abort(f'Invalid version "{version_str}" in {config_name}.')
            if self.options.ver == 'patch':
                version.patch += 1
            elif self.options.ver == 'minor':
                version.minor += 1
                version.patch = 0
            elif self.options.ver == 'major':
                version.major += 1
                version.minor = 0
                version.patch = 0
            config['version'] = f'{version.major}.{version.minor}.{version.patch}'
            changed = True
        elif version_str != self.options.ver:
            version = self.parse_version(self.options.ver)
            if version.major < 0:
                self.context.log.abort('Invalid version "{self.options.ver}"')
            config['version'] = f'{version.major}.{version.minor}.{version.patch}'
            changed = True

        if not changed:
            self.context.log.info('Version no changed.')
            exit(0)

        print(f'Bump version: {version_str} -> {version.major}.{version.minor}.{version.patch}')

        self.context.write_config(config)
        ret = self.run_script(self.name, scripts, config, args)
        if ret != 0:
            exit(ret)

        self.run_script(f"post{self.name}", scripts, config, args)
