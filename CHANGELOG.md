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