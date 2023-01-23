#!/usr/bin/env bash

# Borrowed from https://github.com/saily/pre-commit-yapf-isort/blob/master/pre_commit_hooks/yapf-isort.sh

set -o errexit
set -o pipefail
set -o nounset

DEBUG=${DEBUG:=0}
[[ $DEBUG -eq 1 ]] && set -o xtrace

echo 'Begin yapf'
if ! which yapf &>/dev/null; then
  >&2 echo 'yapf command not found'
  exit 1
fi
yapf -i -vv "$@"

echo 'Begin isort'
if ! which isort &>/dev/null; then
  >&2 echo 'isort command not found'
  exit 1
fi
isort --ac "$@"
