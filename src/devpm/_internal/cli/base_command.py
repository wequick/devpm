# -*- coding:utf-8 -*-

# This file is part of devpm.
#
# Copyright (c) 2023 wequick
# This software is distributed under the MIT license.

# Base command

from argparse import _SubParsersAction, ArgumentParser
from devpm._internal.utils.context import Context


class Command:
    def __init__(self, context: Context, name: str, summary: str):
        self.context = context
        self.name = name
        self.summary = summary

    def add_parser(self, parser: ArgumentParser):
        pass

    def create_parser(self, subparsers: _SubParsersAction):
        parser = subparsers.add_parser(self.name, help=self.summary)
        parser.usage = f'devpm {self.name} [options]'
        self.add_parser(parser)

    def run(self, args=None):
        pass

    def main(self, args=None):
        self.run(args)
