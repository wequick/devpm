# -*- coding:utf-8 -*-

# This file is part of devpm.
#
# Copyright (c) 2023 wequick
# This software is distributed under the MIT license.

# devpm pr - pull request

from devpm._internal.cli.base_command import Command


class PrCommand(Command):
    def run(self, args=None):
        branch = self.context.git.run(['branch', '--show-current'])
        if branch:
            self.context.git.run(['push', 'origin', f'HEAD:refs/for/{branch}'])
