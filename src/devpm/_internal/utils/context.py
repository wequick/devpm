# -*- coding:utf-8 -*-

# This file is part of devpm.
#
# Copyright (c) 2023 wequick
# This software is distributed under the MIT license.

# System context manager

import json
import os
import re
import subprocess
import sys
from devpm._internal.utils.git import Git
from devpm._internal.utils.bash import Bash
from devpm._internal.utils.log import Log
from devpm._internal.utils.code import Code
from devpm._internal.utils.pip import Pip


class Context:
    def __init__(self):
        self.cwd = os.getcwd()
        self.config_name = 'devpackage.json'
        self.log = Log()
        self.code = Code()
        self.pip = Pip()
        self.bash = Bash()
        self.git = Git()


    def get_config_name(self) -> str:
        return self.config_name


    def load_config(self) -> dict:
        config = {}
        if not sys.stdin.isatty():
            # Read from stdin
            s = ''
            for line in sys.stdin:
                s += line.strip()
            try:
                config = json.loads(s)
            except:
                self.log.abort('Invalid config data')
        else:
            # Read from file
            config_file = os.path.join(self.cwd, self.config_name)
            if not os.path.exists(config_file):
                self.log.abort(f'Missing {self.config_name}.')
            with open(config_file, 'r', encoding='utf-8') as file:
                config = json.load(file)
        return config


    def write_config(self, config) -> bool:
        config_file = os.path.join(self.cwd, self.config_name)
        if not os.path.exists(config_file):
            self.log.abort(f'Missing {self.config_name}.')
        with open(config_file, 'w', encoding='utf-8') as file:
            json.dump(config, file, indent=2)


    def check_install_exe(self, exe, url):
        installed_ver = None
        args = [exe, '-h']
        try:
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = p.communicate()
            if p.returncode != 1:
                if len(output) == 0:
                    output = error.decode('utf-8')
                else:
                    output = output.decode('utf-8')
                if len(output) > 0:
                    lines = output.splitlines()
                    installed_ver = lines[0]
        except:
            pass
        return installed_ver


    def evaluate_package_config(self, exp, config: dict={}) -> str:
        def get_package_config(match_obj):
            if match_obj.group() is not None:
                s = match_obj.group(2)
                arr = s[1:].split('.')
                val = config
                for key in arr:
                    if not key in val:
                        val = None
                        break
                    val = val[key]
                return str(val) if val else match_obj.group()
        return re.sub(r"(\$devpackage((\.[\d|\w|_]+){1,}))", get_package_config, exp)


    def evaluate_func(self, exp) -> str:
        index = exp.find(':', 1)
        if index > 0:
            func = exp[1:index]
            args = exp[index+1:]
        else:
            func = exp[1:]
            args = None
        if func == 'pip.which':
            return self.pip.which(args)
        elif func == 'bash.which':
            return self.bash.which(args)
        return exp


    def evaluate(self, exp, config: dict={}) -> str:
        if not exp or not '$' in exp:
            return exp
        # evaluate devpackage.json
        value = self.evaluate_package_config(exp, config)
        # evaluate functions
        value = self.evaluate_func(value)
        return value
