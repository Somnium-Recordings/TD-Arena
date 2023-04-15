"""
Based on pre-commit-hooks/check_added_large_files

We want to check all files, not just added. This removes the
--diff-filter=A and drops git lfs since we aren't using it.
"""
import argparse
import math
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Optional


class CalledProcessError(RuntimeError):
	pass


def cmd_output(
	*cmd: str,
	retcode: Optional[int] = 0,
	**kwargs: Any  # noqa: ANN401
) -> str:
	kwargs.setdefault('stdout', subprocess.PIPE)
	kwargs.setdefault('stderr', subprocess.PIPE)

	with subprocess.Popen(cmd, **kwargs) as proc:
		stdout, stderr = proc.communicate()
		stdout = stdout.decode()
		if retcode is not None and proc.returncode != retcode:
			raise CalledProcessError(cmd, retcode, proc.returncode, stdout, stderr)

	return stdout


def staged_files() -> set[str]:
	cmd = ('git', 'diff', '--staged', '--name-only')
	return set(cmd_output(*cmd).splitlines())


def find_large_files(filenames: Sequence[str], maxkb: int) -> int:
	# Find all added files that are also in the list of files pre-commit tells
	# us about
	retv = 0
	for filename in staged_files() & set(filenames):
		kb = int(math.ceil(Path(filename).stat().st_size / 1024))
		if kb > maxkb:
			print(f'{filename} ({kb} KB) exceeds {maxkb} KB.')  # noqa: T201
			retv = 1

	return retv


def main(argv: Optional[Sequence[str]] = None) -> int:
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'filenames',
		nargs='*',
		help='Filenames pre-commit believes are changed.',
	)
	parser.add_argument(
		'--maxkb',
		type=int,
		default=500,
		help='Maxmimum allowable KB for added files',
	)

	args = parser.parse_args(argv)
	return find_large_files(args.filenames, args.maxkb)


if __name__ == '__main__':
	sys.exit(main())
