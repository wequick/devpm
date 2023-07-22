# -*- coding:utf-8 -*-

# This file is part of devpm.
#
# Copyright (c) 2023 wequick
# This software is distributed under the MIT license.

# System context manager

import json
import os
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
        self.log = Log()
        self.code = Code()
        self.pip = Pip()
        self.bash = Bash()
        self.git = Git()

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
            config_file = os.path.join(self.cwd, 'devpackage.json')
            if not os.path.exists(config_file):
                self.log.abort('devpackage.json no found.')
            with open(config_file, 'r', encoding='utf-8') as file:
                config = json.load(file)
        return config

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

    def evaluate(self, exp, cwd):
        if not exp or exp[0] != '$':
            return exp
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
        return None
