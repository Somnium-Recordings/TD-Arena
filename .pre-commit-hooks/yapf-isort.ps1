#!/usr/bin/env pwsh

yapf -i -vv $args

isort --atomic $args
