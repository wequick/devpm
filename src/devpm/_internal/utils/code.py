# -*- coding:utf-8 -*-

# This file is part of devpm.
#
# Copyright (c) 2023 wequick
# This software is distributed under the MIT license.

# Visual studio code cli and user settings editor

import json
import os
from contextlib import contextmanager
from devpm._internal.utils.bin import Bin


class Code(Bin):
    def __init__(self):
        super().__init__()
        self.name = 'code'
        platform = 'mac' if 'darwin' == self.platform else self.platform
        self.help_url = f'https://code.visualstudio.com/docs/setup/{platform}#_launching-from-the-command-line'
        self.shell = self.platform == 'win32'
        # https://code.visualstudio.com/docs/getstarted/settings#_settings-file-locations
        if self.platform == 'win32':
            self.settings_root = os.getenv('APPDATA')
            self.search_paths = [os.path.join(self.home, 'AppData', 'Local', 'Programs', 'Microsoft VS Code', 'bin', 'code')]
        elif self.platform == 'darwin':
            self.settings_root = os.path.join(self.home, 'Library', 'Application Support')
            self.search_paths = ['/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code']
        else:
            self.settings_root = os.path.join(self.home, '.config')
        self.user_settings_path = os.path.join(self.settings_root, 'Code', 'User', 'settings.json')
        if os.environ.get('NODE_OPTIONS'):
            os.environ.pop('NODE_OPTIONS')

    def install_vsix(self, path, ver):
        args = ['--install-extension']
        if ver == 'latest':
            args.append('--force')
        elif ver:
            args.append(path + '@' + ver)
        else:
            args.append(path)
        self.call(args)

    def check_install_vsix(self, ext, ver):
        args = ['--list-extensions', '--show-versions']
        installed_ver = None
        if ver == '':
            ver = None
        output = self.run(args)
        if output:
            for line in output.splitlines():
                index = line.find('@')
                if index > 0:
                    if str(line[:index]).lower() == ext:
                        installed_ver = str(line[index+1:])
        if not installed_ver or (ver and installed_ver != ver):
            self.install_vsix(ext, ver)
        else:
            print('Version %s installed.' % installed_ver)

    @contextmanager
    def open_user_settings(self):
        f = open(self.user_settings_path, 'r')
        s = f.read()
        f.close()
        settings = json.loads(s)
        yield settings
        s2 = json.dumps(settings, indent=4)
        if s != s2:
            f = open(self.user_settings_path, 'w')
            f.write(s2)
            f.close()
