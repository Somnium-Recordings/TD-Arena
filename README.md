# TD Areana

![TD Arena Tests](https://github.com/somnium-recordings/TD-Arena/workflows/TD%20Arena%20Tests/badge.svg)

This project is heavily inspired by [Resolume Arena](https://resolume.com/). I wanted something that allowed me to perform like you might with arena, but allowing for sources other than just video (`tox`, `notch`, etc.) and custom effects built in TD.

## 🚧 Under Active Development 🚧

[Current backlog of planned features.](https://github.com/llwt/TD-Arena/projects/1)

This is not yet in a working state. If you're curious about any of this, please reach out through a github issue or ping me over in the [TouchDesigner discord](http://td-discord.com/) `@lolwut#2076`.

![UI Screenshot](Docs/images/ui.png)

## Contributing

I'm currently developing this using [VS Code](https://code.visualstudio.com/) on Windows. Instructions for setting up a development environment as I'm using it are below.

**Note:** I don't use python much in my day job, or windows for that matter. If there are better ways to manage any of this I'd love to hear how it can be improved!

### Development Setup

1. Install Python version currently shipped with TouchDesigner

   _This version can be found by opening a a textport from the menu `Dialogs -> Textports and DATs`. It will be output in the console or can be found by entering `sys.version`._

   I use [`pyenv-win`](https://github.com/pyenv-win/pyenv-win) to manage my python versions, but that's by no means a requirement.

   ```ps1
   Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"

   # reload terminal
   pyenv install 3.9.5

   # Optionally set this to your global version of python
   pyenv global 3.9.5
   ```

1. Install Poetry

   I use [`pipx`](https://pypa.github.io/pipx/) to manage [poetry](https://python-poetry.org/), but similar to `pyenv-win` this is not a requirement. Install it however you see fit.

   ```ps1
   # If not already installed, upgrade pip and install pipx
   pip install --upgrade pip
   pip install --user pipx
   pipx ensure path

   # Install Poetry
   pipx install poetry
   ```

   Once installed, the virtual env for the project can be entered using `poetry shell`, however this is typically done auto-magically by vscode when opening a new powershell terminal.

1. Install project dependencies

   _From the poetry shell:_

   ```ps1
   poetry install
   ```

1. Local site-packages

[`TODO(#87)`](https://github.com/Somnium-Recordings/TD-Arena/issues/87)

### A Note about code style

_I was originally using [black](https://github.com/psf/black) but have switched to [yapf](https://github.com/google/yapf) with a modified config to allow python generated from touch to be in the same format as the project files. The primary incompatabilities with `black` were `tabs` and `single quotes`._

### Module + Extension Conventions

🚧 **Note: I'm actively migrating from the old structure to the new as I touch things. Once a good chunk has been migrated, I'll sit down and wrap up the rest** 🚧

- semi-flat structure with extensions colocated with tox files in `Lib` folder
- `__init__.py` created for any module that should be auto-created (See `Libe/auto-Module`)
- `ui` or `render` modules prefixed accordingly.
  - e.g. `Lib/ui_state`
- modules and toxes in `snake_case`
- extensions with `_ext` suffix and class name matching file name in `PascalCase`
  - e.g. `ui_foo/ui_foo_ext.py` -> `UiFooExt`
- Extensions attached to components with the following config:
  - `opshortcut`: snake case name
    - e.g. `ui_state`
  - `extension1` initialized using `mod` reference
    - e.g. `mod.ui_state.ui_state_ext.UIStateExt(me, ...)`
  - `extname1` set to initialized class name
    - e.g. `UIStateExt`
    - _NOTE: this is the default and can be excluded in most cases_

#### Referencing Other Extensions

When referencing one extension from another:

- Use the `op` shortcut in combination with the `ext` member to get a reference to the instance
- Cast the extension reference it to the type of the extension class
  - This should be imported using the module name which should correspond to the shortcut name
  - This cast ensures both type safety as well as allowing TD to understand the extension dependency

For example, to use the `UIStateExt` in a module:

```py

from ui_state import ui_state_ext

class SomeDependentExt:
    def __init__(self, ownerComponent):
        self.ownerComponent = ownerComponent
        self.uiState = cast(ui_state_ext.UIStateExt, op.ui_state.ext.UIStateExt)

```

From TD, using promoted extension members is the preferred way:

```py
op.ui_state.SomePromotedMember(...)
```

#### The Rationale

- Enable importing extensions from other extensions and retain typesafety in VsCode along with pyright
- Colocate extensions with tox files without having one giant folder for all modules
- Allow touchdesigner to track module dependencies and automatically reload extensions and their dependencies on change
- Auto generate module definitions in touchdesigner

I've gone through a few different iterations of structuring tox files along with their python extensions and have finally landed on a somewhat happy middle ground that allows for retaining typesafety with out a ton of extra overhead. The secret sauce is in `Lib/auto_module` which will
