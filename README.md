# TD Areana

![TD Arena Tests](https://github.com/llwt/TD-Arena/workflows/TD%20Arena%20Tests/badge.svg)

This project is heavily inspired by [Resolume Arena](https://resolume.com/). I wanted something that allowed me to preform like you might with arena, but allowing for sources other than just video (`tox`, `notch`, etc.) and custom effects built in TD.

## 🚧 Under Active Development 🚧

This is not yet in a working state. If you're curious about any of this, please reach out through a github issue or ping me over in the [TouchDesigner discord](http://td-discord.com/) `@lolwut#2076`.

![UI Screenshot](docs/images/2020-05-20-ui.png)

## Contributing

I'm currently developing this using [VS Code](https://code.visualstudio.com/) on Windows. Instructions for setting up a development environment as I'm using it are below.

**Note:** I don't use python, or windows for that matter, in my day job much. If there are better ways to manage any of this I'd love to improve!

### Python

Install the [version of python touch is using](https://docs.derivative.ca/Release_Notes#New_Python), currently `3.7.2`.

_My personal preference is through [pyenv-win](https://github.com/pyenv-win/pyenv-win)_

```
pyenv install 3.7.2
pyenv rehash
pip install --upgrade pip
```

### Pipenv

Project dependencies are currently managed through [pipenv](https://pipenv.pypa.io/en/latest/install/#installing-pipenv). At the moment this is just linting and formatting configuration with pre-commits to run them automatically.

```sh
pip install --user pipenv
pipenv install --dev
pipenv shell
pre-commit install
```

### A Note about code style

_I was originally using [black](https://github.com/psf/black) but have switched to [yapf](https://github.com/google/yapf) with a modified config to allow python generated from touch to be in the same format as the project files. The primary incompatabilities with `black` were `tabs` and `single quotes`._
