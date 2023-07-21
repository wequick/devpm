# -*- coding:utf-8 -*-

# This file is part of devpm.
#
# Copyright (c) 2023 wequick
# This software is distributed under the MIT license.

# devpm pr - pull request

import os
import re
from argparse import ArgumentParser
from devpm._internal.commands.base_run import BaseRunCommand


class GithookCommand(BaseRunCommand):
    def add_parser(self, parser: ArgumentParser):
        subparsers = parser.add_subparsers(dest='hook_name', help='git hook name')
        subparser = subparsers.add_parser('commit-msg', help=self.summary)
        subparser.usage = 'devpm githook commit-msg [options]'
        subparser.add_argument("hook_args", nargs='*')


    def run(self, args=None):
        if self.options.hook_name == 'commit-msg':
            self.verify_commit_msg(self.options.hook_args)


    def verify_commit_msg(self, args: list[str]):
        commit_msg = args[0]
        if os.path.exists(commit_msg):
            with open(commit_msg, 'r', encoding='utf8') as file:
                commit_msg = file.read()
        config = self.context.load_config()
        if not 'gitHooks' in config:
            return
        git_hooks = config['gitHooks']
        if not 'commit-msg' in git_hooks:
            return
        commit_msg_hook = git_hooks['commit-msg']
        if not 'pattern' in commit_msg_hook:
            return
        pattern = commit_msg_hook['pattern']
        if isinstance(pattern, str):
            patterns = [pattern]
        else:
            patterns = pattern
        for item in patterns:
            if re.match(item, commit_msg):
                return
        if 'tips' in commit_msg_hook:
            for line in commit_msg_hook['tips']:
                print(line)
        else:
            self.context.log.warn('Invalid commit-msg format')
        exit(1)
