# -*- coding:utf-8 -*-

# This file is part of devpm.
#
# Copyright (c) 2023 wequick
# This software is distributed under the MIT license.

import os
import stat
import subprocess
import sys
from collections import namedtuple
from devpm._internal.utils.bin import Bin

GitModule = namedtuple('GitModule', field_names=[
    'host_root_path', 'root_path', 'git_path', 'rel_path', 'is_submodule'])

# Git管理
class Git(Bin):
    def __init__(self) -> None:
        super().__init__()
        self.name = 'git'
        self.help_url = 'https://git-scm.com/downloads'

    def root_path(self, cwd):
        dir = os.path.join(cwd, '.git')
        if os.path.exists(dir):
            return cwd
        dir = self.run(['rev-parse', '--show-toplevel'], cwd=cwd)

    def git_path(self, cwd = None):
        cwd = cwd or self.cwd or os.getcwd()
        path = self.run(['rev-parse', '--git-dir'], cwd=cwd)
        if not path:
            return None
        return os.path.abspath(os.path.join(cwd, path))
    
    def create_regexp_hook_script(self, root_path, name, pattern, tips):
        tips_echo = ''
        for tip in tips:
            tips_echo += 'echo "%s"\n' % tip
        # note: grep -P for posix, which support \d match, compat for windows.
        grep_mode = 'P' if sys.platform == 'win32' else 'E'
        s = '''#!/bin/bash
# Auto-generated by devpm.

if [ $(grep -%s '%s' "$1" | wc -l) -eq 0 ]; then
%s
exit 1
fi
''' % (grep_mode, pattern, tips_echo)
        script_dir = os.path.join(root_path, 'dev_modules', 'git-hooks')
        if not os.path.exists(script_dir):
            os.makedirs(script_dir)
        script_file = os.path.join(script_dir, name)
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(s)
        self.make_exec(script_file)
        return 'dev_modules/git-hooks/%s' % name
    
    def append_hook(self, root_path, git_path, name, hook, apply_submodules):
        t = hook['type'] if 'type' in hook else None
        if not t:
            return
        available_types = ['regexp', 'pre-commit']
        if not t in available_types:
            return

        modules = self.get_modules(root_path)
        if t == 'regexp':
            self.append_hook_script(modules, name)
        elif t == 'pre-commit':
            self.install_pre_commit(modules, hook['repos'], root_path)

    def make_exec(self, file):
        st = os.stat(file)
        mode = st.st_mode & stat.S_IEXEC
        if mode == 0:
            os.chmod(file, st.st_mode | stat.S_IEXEC)

    def get_modules(self, host):
        modules = []
        git_path = os.path.join(host, '.git')
        if not os.path.exists(git_path):
            return modules
        modules.append(GitModule(host, host, git_path, '.', False))
        output = self.run(['submodule'], cwd=host)
        if output:
            for line in output.splitlines():
                arr = line.strip().split(' ')
                if len(arr) > 1:
                    sub = arr[1]
                    modules.append(GitModule(
                        host,
                        os.path.join(host, sub),
                        os.path.join(git_path, 'modules', sub),
                        os.path.relpath('.', sub).replace('\\', '/'),
                        True))
        return modules

    def append_hook_script(self, modules, name):
        for module in modules:
            hook_path = os.path.join(module.git_path, 'hooks')
            self.append_hook_script_sub(module.host_root_path, hook_path, name, module.rel_path)

    def append_hook_script_sub(self, host, hook_path, name, root):
        devpm = 'exec devpm'
        script = f'cat {root}/devpackage.json | {devpm} githook {name} "$@"'
        if os.path.exists(hook_path):
            hook_file = os.path.join(hook_path, name)
            new_file_content = None
            if not os.path.exists(hook_file):
                new_file_content = '#!/bin/bash\n\n# Auto-generated by devpm.\n' + script + '\n'
            else:
                with open(hook_file, 'r', encoding='utf-8') as f:
                    needs_update = False
                    file_content = ''
                    added = False
                    for line in f.readlines():
                        index = line.find(devpm)
                        if index < 0:
                            file_content += line
                        else:
                            if not added:
                                added = True
                                needs_update = line.strip() != script
                                file_content += script + '\n'
                            else:
                                needs_update = True  # Remove old scripts
                    if not added:
                        needs_update = True
                        file_content += script + '\n'
                    if needs_update:
                        new_file_content = file_content
            result = '%s installed at %s' % (name, os.path.relpath(hook_file, host))
            if new_file_content:
                with open(hook_file, 'w', encoding='utf-8') as f:
                    f.write(new_file_content)
                    result += ' [updated]'
            self.make_exec(hook_file)
            print(result)

    def update_pre_commit_config_yaml(self, name, cfg_repos, cwd):
        import yaml
        target_pre_commit_config = os.path.join(cwd, name)
        new_file_content = None
        data = {}
        if not os.path.exists(target_pre_commit_config):
            data['repos'] = cfg_repos
            new_file_content = yaml.dump(data)
        else:
            file_content = ''
            with open(target_pre_commit_config, 'r', encoding='utf-8') as f:
                file_content = f.read()
                data = yaml.load(file_content, Loader=yaml.FullLoader)
            if not 'repos' in data:
                data['repos'] = cfg_repos
            else:
                for cfg_repo in cfg_repos:
                    has_repo = False
                    data['repos'] = [x for x in data['repos'] if 'repo' in x]
                    for repo in data['repos']:
                        if repo['repo'] != cfg_repo['repo']:
                            continue
                        has_repo = True
                        repo['rev'] = cfg_repo['rev']
                        if not 'hooks' in repo:
                            repo['hooks'] = cfg_repo['hooks']
                        else:
                            for cfg_hook in cfg_repo['hooks']:
                                id = cfg_hook['id']
                                found = None
                                for hook in repo['hooks']:
                                    if id == hook['id']:
                                        found = True
                                        for key in cfg_hook:
                                            hook[key] = cfg_hook[key]
                                        break
                                if not found:
                                    repo['hooks'].append(cfg_hook)
                    if not has_repo:
                        data['repos'].append(cfg_repo)
            new_file_content = yaml.dump(data, sort_keys=False)
            if file_content == new_file_content:
                new_file_content = None
        if new_file_content:
            print('update %s' % (name))
            with open(target_pre_commit_config, 'w', encoding='utf-8') as f:
                f.write(new_file_content)

    def install_pre_commit(self, modules, repos, host):
        # Create config yaml from user hook config.
        host_yaml = '.pre-commit-config.yaml'
        self.update_pre_commit_config_yaml(host_yaml, repos, host)
        # Install pre-commit at host module.
        try:
            # Exec `pre-commit install` for submodules
            subprocess.check_call(['pre-commit', 'install'], cwd=host)
        except:
            return
        # Copy pre-commit to submodules.
        host_pre_commit = os.path.join(host, '.git', 'hooks', 'pre-commit')
        for module in modules:
            if module.is_submodule:
                sub_pre_commit = os.path.join(module.git_path, 'hooks', 'pre-commit')
                sub_yaml = module.rel_path + '/' + host_yaml
                self.install_pre_commit_sub(host, host_pre_commit, sub_pre_commit, host_yaml, sub_yaml)

    def install_pre_commit_sub(self, host, host_pre_commit, sub_pre_commit, host_yaml, sub_yaml):
        s = ''
        with open(host_pre_commit, 'r') as f:
            s = f.read()
        s = s.replace(host_yaml, sub_yaml)
        with open(sub_pre_commit, 'w') as f:
            f.write(s)
            print('pre-commit installed at %s' % os.path.relpath(sub_pre_commit, host))

if __name__ == '__main__':
    # test
    # git = Git()
    # git.init()
    # print(os.getcwd())
    # print(git.root_path(os.getcwd()))
    # git_path = git.git_path(os.getcwd())
    # git.append_hook(git_path, 'commit-msg', 'scaffold/git-hooks/commit-msg', '.', True)    # scaffold/git-hooks/commit-msg
    # git.run_all_modules('hello', git.root_path(os.getcwd()))
    pass
