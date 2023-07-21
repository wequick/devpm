# -*- coding:utf-8 -*-

# This file is part of devpm.
#
# Copyright (c) 2023 wequick
# This software is distributed under the MIT license.

from argparse import ArgumentParser
import os
import sys
from devpm._internal.cli.base_command import Command
from devpm._internal.commands import commands_dict, create_command

def create_argument_parser(context) -> tuple[ArgumentParser, dict[str, Command]]:
    """Create the argument parser."""

    parser = ArgumentParser(add_help=False)
    parser.usage = "devpm <commands> [options]"
    parser.description = "Development package manager."
    parser.epilog = "See <http://github.com/wequick/devpm> for the full manual."

    parser.add_argument('-h', '--help', action="help")
    parser.add_argument('-v', '--version', dest='version', action="store_true", default=False)
    parser.add_argument('-r', '--root', dest='root', help='The dirname for devpackage.json')

    commands = {}
    subparsers = parser.add_subparsers(dest='command', help='commands')
    for k in commands_dict:
        command = create_command(context, k)
        command.create_parser(subparsers)
        commands[k] = command

    return parser, commands


def version():
    try:
        import pkg_resources
        return pkg_resources.get_distribution('devpm').version
    except:
        return ''


def main(args = None):
    from devpm._internal.utils.context import Context
    context = Context()
    parser, commands = create_argument_parser(context)
    parser.version = 'devpm ' + version()
    options = parser.parse_args(args)
    if options.version:
        sys.stdout.write(parser.version)
        sys.stdout.write(os.linesep)
        sys.exit()
    if not options.command:
        parser.print_help()
        sys.exit(1)
    if options.root:
        context.cwd = options.root
    command = commands[options.command]
    command.options = options
    command_args = sys.argv[1:]
    command.parse_args(command_args)
    commands[options.command].main(command_args)


if __name__ == '__main__':
    main()
