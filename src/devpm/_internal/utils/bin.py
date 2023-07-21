# -*- coding:utf-8 -*-

# This file is part of devpm.
#
# Copyright (c) 2023 wequick
# This software is distributed under the MIT license.

# Binary

import os
import subprocess
import sys


class Bin:
    def __init__(self) -> None:
        self.name = None
        self.help_url = None
        self.bin = None
        self.version = None
        self.shell = False
        self.cwd = None
        self.not_found = False
        self.err = None
        self.home = os.path.expanduser("~")
        self.platform = sys.platform
        self.version_args = ['--version']
        self.search_paths = []

    def verify_version(self, v) -> str | None:
        return None

    def abort(self) -> None:
        print(f'{self.name} {self.err}. see {self.help_url}')
        exit(1)

    def check_bin(self) -> bool:
        if self.bin:
            return
        if not self.name:
            self.abort()
        if self.err:
            self.abort()
        args = self.version_args
        args.insert(0, self.name)
        try:
            self.version = subprocess.check_output(args, shell=self.shell).decode('utf-8')
            self.err = self.verify_version(self.version)
            if self.err:
                self.abort()
            self.bin = self.name
        except:
            for path in self.search_paths:
                if os.path.exists(path):
                    self.bin = path
            if not self.bin:
                self.err = 'command not found'
            else:
                args = self.version_args
                args.insert(0, self.bin)
                self.version = subprocess.check_output(args, shell=self.shell).decode('utf-8')
            self.abort()

    def run(self, args, cwd=None, echo_only=False) -> str | None:
        self.check_bin()
        args.insert(0, self.bin)
        try:
            if echo_only:
                print(f"> {' '.join(args)}")
                return None
            return subprocess.check_output(args, shell=self.shell, cwd=cwd).decode('utf-8').strip()
        except:
            return None

    def call(self, args, cwd=None) -> None:
        self.check_bin()
        args.insert(0, self.bin)
        subprocess.call(args, shell=self.shell, cwd=cwd)
