import logging
import sys
from logging.handlers import RotatingFileHandler
from types import TracebackType
from typing import Optional

from .json_log_formatter import TdContextJsonFormatter
from .logger_utils import getHandlers, normalizeSourcePath


def configureJsonHandler(logger: logging.Logger):
	fileHandler = RotatingFileHandler(
		filename=tdu.expandPath('Logs/td-arena.log'),
		maxBytes=10 * 1024 * 1024,  # 10MB
		backupCount=5,
	)

	fileHandler.setFormatter(TdContextJsonFormatter())

	logger.addHandler(fileHandler)

	logger.setLevel(logging.DEBUG)

	debug('json log handler registered')


def clearLogHandlers(logName: Optional[str]):
	logger = logging.getLogger(logName)

	# Only remove our custom handlers (RotatingFileHandler with TdContextJsonFormatter)
	# so that we don't remove anything added by the touchdesigner logger
	handlers_to_remove = []
	for handler in logger.handlers:
		if (
			isinstance(handler, RotatingFileHandler)
			and isinstance(handler.formatter, TdContextJsonFormatter)
		):
			handlers_to_remove.append(handler)

	for handler in handlers_to_remove:
		handler.close()
		logger.removeHandler(handler)


def ensureLogHandlersPresent(logName: Optional[str] = None):
	# global _previous_excepthook  # noqa: PLW0603
	# if _previous_excepthook is None:
	# 	_previous_excepthook = sys.excepthook
	# 	sys.excepthook = globalExceptionHandler

	logger = logging.getLogger(logName)
	if not logger.hasHandlers():
		configureJsonHandler(logger)


def reloadLogHandlers(logName: Optional[str] = None):
	clearLogHandlers(logName)
	ensureLogHandlersPresent(logName)


def getComponentLogger(component: OP) -> logging.LoggerAdapter:
	ensureLogHandlersPresent()

	# Convert component path to dot notation for logger name
	# e.g. "/td-arena/ui/status" -> "td-arena.ui.status"
	logName = normalizeSourcePath(component.path)[1:].replace('/', '.')

	logger = logging.getLogger(logName)

	return logging.LoggerAdapter(logger, {
		'component': component,
	})


def rotateLogs(logName: Optional[str] = None):
	for handler in getHandlers(logging.getLogger(logName), RotatingFileHandler):
		handler.doRollover()


def registerGlobalExceptionHandler():
	sys.excepthook = globalExceptionHandler


def globalExceptionHandler(
	exc_type: type, exc_value: BaseException, exc_traceback: TracebackType | None
):
	try:
		# Call the default excepthook to print the exception to the console
		sys.__excepthook__(exc_type, exc_value, exc_traceback)

		# Ensure logging is available, sometimes we get logging can't be found issues
		import logging

		# Forward exception to the logging system
		logging.error(
			'%s: %s',
			exc_type.__name__,
			exc_value,
			exc_info=(exc_type, exc_value, exc_traceback),
			stack_info=True
		)
	except Exception as e:  # noqa: BLE001
		# If logging fails, at least print the error
		print(f'Error in global exception handler: {e}')
		sys.__excepthook__(type(e), e, e.__traceback__)
