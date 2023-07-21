# 1.1.0 (2023-07-21)
## feat
* support command pr/cr/run/lint/test/start/stop/restart/version
* support run scripts in devpackage.json

# 1.0.4 (2023-07-20)
## fix
* commit-msg hook - ensure add DEVPME script

# 1.0.3 (2023-07-20)
## refactor
* rename SCFEXE to DEVPME
## docs
* rename wequick.cpp-creator to wequick.filegen

# 1.0.2 (2023-07-17)
## fix
* copy hook args for pre-commit-config.yaml
## docs
* update README and schema
* udpate devpackage.json, add example for cppcheck args

# 1.0.1 (2023-07-16)
## feat
* git hooks support submodules and compat for windows


# 1.0.0 (2023-07-15)
## feat
* devpm install - Install packages by devpackage.json in current directory which support config:
  - vscodeDependencies for vscode extensions
  - vscodeUserSettings for edit vscode user settings file
  - pythonDependencies for python modules
  - bashDependencies for custom bash script
  - gitHooks for add git hooks like `pre-commit`, `commit-msg`