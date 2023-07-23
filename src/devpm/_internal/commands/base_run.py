# -*- coding:utf-8 -*-

# This file is part of devpm.
#
# Copyright (c) 2023 wequick
# This software is distributed under the MIT license.

# devpm pr - pull request


import os
from devpm._internal.cli.base_command import Command


class BaseRunCommand(Command):
    def run(self, args=None):
        if args:
            args = args[1:]
        self.run_script_group(self.name, args)


    def show_scripts(self, scripts) -> None:
        print("Available scripts:")
        for name in scripts:
            print(f"  {name}")
            print(f"    {scripts[name]}")
        exit(1)


    def run_script_group(self, name: str | None, args=None, config: dict={}) -> None:
        if not config:
            config = self.context.load_config()
        scripts = {}
        if 'scripts' in config:
            scripts = config['scripts']
        if not name:
            # show scripts
            self.show_scripts(scripts)
        if not name in scripts:
            print(f"Missing script \"{name}\".\n")
            self.show_scripts(scripts)
        self.run_script(f"pre{name}", scripts, config, args)
        ret = self.run_script(name, scripts, config, args)
        if ret != 0:
            exit(ret)
        self.run_script(f"post{name}", scripts, config, args)


    def run_script(self, name: str, scripts: dict, config: dict={}, args=None) -> int:
        if name in scripts:
            script = self.context.evaluate(scripts[name], config)
            if args:
                script += ' ' + ' '.join(args)
            print(f"> {name}")
            print(f"> {script}")
            return os.system(script)
        return 0
