# -*- coding:utf-8 -*-

# This file is part of devpm.
#
# Copyright (c) 2023 wequick
# This software is distributed under the MIT license.

# Package contains all devpm commands.

import importlib
from collections import namedtuple
from typing import Any, Dict, Optional

from devpm._internal.cli.base_command import Command
from devpm._internal.utils.context import Context

CommandInfo = namedtuple("CommandInfo", "summary")

# This dictionary does a bunch of heavy lifting for help output:
# - Enables avoiding additional (costly) imports for presenting `--help`.
# - The ordering matters for help display.
#
# Even though the module path starts with the same "devpm._internal.commands"
# prefix, the full path makes testing easier (specifically when modifying
# `commands_dict` in test setup / teardown).
commands_dict: Dict[str, CommandInfo] = {
    "install": CommandInfo("Install packages from devpackage.json."),
    "pr": CommandInfo("Create a Pull Request."),
    "cr": CommandInfo("Create a Code Review, same to pr."),
    "run": CommandInfo("Run [NAME] script in devpackage.json."),
    "lint": CommandInfo("Run lint script in devpackage.json."),
    "test": CommandInfo("Run test script in devpackage.json."),
    "start": CommandInfo("Run start script in devpackage.json."),
    "stop": CommandInfo("Run stop script in devpackage.json."),
    "restart": CommandInfo("Run restart script in devpackage.json."),
    "version": CommandInfo("Bump a package version and auto-gen CHANGELOG."),
    "githook": CommandInfo("Run git hook."),
}


def create_command(context: Context, name: str, **kwargs: Any) -> Command:
    """
    Create an instance of the Command class with the given name.
    """
    summary, = commands_dict[name]
    module_path = f'devpm._internal.commands.{name}'
    class_name = f'{name.capitalize()}Command'
    module = importlib.import_module(module_path)
    command_class = getattr(module, class_name)
    command = command_class(context=context, name=name,
                            summary=summary, **kwargs)

    return command


def get_similar_commands(name: str) -> Optional[str]:
    """Command name auto-correct."""
    from difflib import get_close_matches

    name = name.lower()

    close_commands = get_close_matches(name, commands_dict.keys())

    if close_commands:
        return close_commands[0]
    else:
        return None
