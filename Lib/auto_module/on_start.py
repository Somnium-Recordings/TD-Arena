import sys
from pathlib import Path


def onStart():
	localPythonPath = Path(project.folder) / '.venv' / 'Lib' / 'site-packages'

	if not localPythonPath.is_dir():
		raise OSError(
			'expected local python path not found, did you forget to run "poetry install"?\n'
			f'  expected directory: {localPythonPath}'
		)

	pathString = str(localPythonPath)
	if pathString not in sys.path:
		debug(f'adding local install to python path: {pathString}')
		sys.path = [str(pathString), *sys.path]


def onCreate():
	# Within TouchEngine, what we use for rendering, onStart doesn't fire.
	# Instead the recommendation is to use onCreate
	# See: https://docs.derivative.ca/Engine_COMP
	onStart()
