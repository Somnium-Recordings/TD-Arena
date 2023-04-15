#!/usr/bin/env pwsh

yapf -i -vv $args

ruff check `
  --force-exclude `
  --fix `
  --exit-non-zero-on-fix `
  --config=./pyproject.toml `
  $args
