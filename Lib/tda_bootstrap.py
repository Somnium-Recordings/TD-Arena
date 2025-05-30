import logging
import sys
from pathlib import Path


def setupPythonPath():
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


def onStart():
	debug('bootstrapping td-arena')

	setupPythonPath()
	mod.logger.log_handlers.bootstrap()
	mod.tda_telemetry.config.bootstrap()

	logger = logging.getLogger()
	logger.info('td-arena bootstrap complete')
