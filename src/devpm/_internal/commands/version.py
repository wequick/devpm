# -*- coding:utf-8 -*-

# This file is part of devpm.
#
# Copyright (c) 2023 wequick
# This software is distributed under the MIT license.

# devpm pr - pull request

from argparse import ArgumentParser
from devpm._internal.commands.base_run import BaseRunCommand


class VersionCommand(BaseRunCommand):
    def add_parser(self, parser: ArgumentParser):
        parser.add_argument('ver', nargs='?', help='<newversion>|major|minor|patch')


    def run(self, args=None):
        git_status = self.context.git.run(['status', '-s'])
        if not git_status or git_status != '':
            self.context.log.warn('Git working directory not clean.')
            exit(1)
        print(f"TODO: version {self.options.ver}")
