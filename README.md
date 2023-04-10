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


## Development Setup

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

   `TODO`

### A Note about code style

_I was originally using [black](https://github.com/psf/black) but have switched to [yapf](https://github.com/google/yapf) with a modified config to allow python generated from touch to be in the same format as the project files. The primary incompatabilities with `black` were `tabs` and `single quotes`._
