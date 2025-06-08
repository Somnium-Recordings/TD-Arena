import logging
import sys
from pathlib import Path

# Global reference to the startup span
startup_span = None
startup_span_ctx = None

logger = logging.getLogger()


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
	mod.tda_telemetry.bootstrap_otel.bootstrap()

	logger.debug('td-arena bootstrap complete')
	enter_startup_span()


def enter_startup_span():
	global startup_span, startup_span_ctx  # noqa: PLW0603

	# We need to import here since they won't be available before
	# calling setupPythonPath
	from opentelemetry import trace  # pylint: disable=import-outside-toplevel
	from opentelemetry.trace import use_span  # pylint: disable=import-outside-toplevel

	# Start a global span for application startup
	tracer = trace.get_tracer('td-arena.startup')
	startup_span = tracer.start_span('startup')
	startup_span_ctx = use_span(startup_span, end_on_exit=False)
	# Manually enter context since we cant use `with:` here
	startup_span_ctx.__enter__()  # pylint: disable=unnecessary-dunder-call

	logger.info('beginning startup')

	# TODO: remove this once we have other traces
	mod.tda_telemetry.verify_tracing.sendTestTraces()

	run('args[0]()', end_startup_span, endFrame=True)


def end_startup_span():
	logger.debug('startup complete')

	global startup_span, startup_span_ctx  # noqa: PLW0603
	if startup_span_ctx is not None:
		startup_span_ctx.__exit__(None, None, None)  # Manually exit context
		startup_span_ctx = None
	else:
		logger.warning('expected to find startup span context, but did not find it')

	if startup_span is not None:
		startup_span.end()
		startup_span = None
	else:
		logger.warning('expected to find startup span, but did not find it')
