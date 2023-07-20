# -*- coding:utf-8 -*-

# This file is part of devpm.
#
# Copyright (c) 2023 wequick
# This software is distributed under the MIT license.

# Python pip manager

import os
import sys
from devpm._internal.utils.bin import Bin


class Pip(Bin):
    def __init__(self):
        super().__init__()
        self.name = 'pip'
        self.help_url = 'https://www.python.org/downloads/'
        self.shell = sys.platform == 'win32'

    def verify_version(self, v) -> str | None:
        if 'python 2' in v:
            return 'requires v3+'
    
    def install(self, lib, ver):
        args = ['install']
        if ver:
            args.append('-v')
            args.append('%s==%s' % (lib, ver))
        else:
            args.append(lib)
        self.call(args)

    def show(self, lib):
        info = {}
        args = ['show', lib]
        output = self.run(args)
        if output:
            for line in output.splitlines():
                token = ': '
                index = line.find(token)
                if index > 0:
                    info[line[:index]] = line[index+len(token):]
        return info

    def check_install(self, lib, ver):
        installed_ver = None
        info = self.show(lib)
        if 'Version' in info:
            installed_ver = info['Version']
        if not installed_ver or (ver and installed_ver != ver):
            self.install(lib, ver)
        else:
            print('Version %s installed.' % installed_ver)

    def which(self, lib):
        info = self.show(lib)
        bin_name = lib if sys.platform != 'win32' else lib + '.exe'
        if 'Location' in info:
            bin_path = info['Location']
            bin = os.path.join(bin_path, bin_name)
            if os.path.exists(bin):
                return bin
            bin_path = os.path.abspath(os.path.join(bin_path, '..', '..', 'Scripts'))
            bin = os.path.join(bin_path, bin_name)
            if os.path.exists(bin):
                return bin
        return None
