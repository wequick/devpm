# -*- coding:utf-8 -*-

# This file is part of devpm.
#
# Copyright (c) 2023 wequick
# This software is distributed under the MIT license.

# devpm pr - pull request


import os
from argparse import ArgumentParser
from devpm._internal.commands.base_run import BaseRunCommand


class RunCommand(BaseRunCommand):
    def add_parser(self, parser: ArgumentParser):
        parser.add_argument('script', nargs='?', type=str, help='script name defined in devpackage.json.')


    def run(self, args=None):
        if args:
            args = args[1:]
        self.run_script_group(self.options.script, args)
