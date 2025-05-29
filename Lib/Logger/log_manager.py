import logging
import sys
from logging.handlers import RotatingFileHandler
from types import TracebackType
from typing import Optional, TypeVar

from .json_log_formatter import TdContextJsonFormatter

HANDLER_TYPE = TypeVar('HANDLER_TYPE')

rootLogger = logging.getLogger()


def getHandlers(
	logger: logging.Logger, HandlerClass: type[HANDLER_TYPE]
) -> list[HANDLER_TYPE]:  # yapf-disable
	return [
		handler for handler in logger.handlers if isinstance(handler, HandlerClass)
	]


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

	sys.excepthook = sys.__excepthook__


def ensureLogHandlersPresent(logName: Optional[str] = None):
	logger = logging.getLogger(logName)
	if not logger.hasHandlers():
		configureJsonHandler(logger)

	if sys.__excepthook__ is sys.excepthook:
		registerGlobalExceptionHandler()


def reloadLogHandlers(logName: Optional[str] = None):
	clearLogHandlers(logName)
	ensureLogHandlersPresent(logName)


def getComponentLogger(component: OP) -> logging.LoggerAdapter:
	# Convert component path to dot notation for logger name
	# e.g. "/td-arena/ui/status" -> "td-arena.ui.status"
	logName = component.path[1:].replace('/', '.')

	logger = logging.getLogger(logName)

	return logging.LoggerAdapter(logger, {
		'component': component,
	})


def rotateLogs(logName: Optional[str] = None):
	for handler in getHandlers(logging.getLogger(logName), RotatingFileHandler):
		handler.doRollover()


def registerGlobalExceptionHandler():
	debug('registering global exception handler')
	sys.excepthook = globalExceptionHandler


def globalExceptionHandler(
	exc_type: type, exc_value: BaseException, exc_traceback: TracebackType | None
):
	if not hasattr(  # noqa: SIM102
		exc_value, '__traceback__'
	) or exc_value.__traceback__ is None:
		if exc_traceback:
			exc_value.__traceback__ = exc_traceback
			debug('propagating traceback')

	# Call the default excepthook to print the exception to the console
	sys.__excepthook__(exc_type, exc_value, exc_traceback)

	try:
		# Use provided traceback if available, otherwise get it from the exception
		traceback = exc_traceback if exc_traceback is not None else exc_value.__traceback__

		# Forward exception to the logging system
		rootLogger.error(
			'%s: %s',
			exc_type.__name__,
			exc_value,
			exc_info=(exc_type, exc_value, traceback),
			stack_info=True
		)

	except Exception as e:  # noqa: BLE001
		# If logging fails, at least print the error
		print(f'Error in global exception handler: {e}')  # noqa: T201
		sys.__excepthook__(type(e), e, e.__traceback__)
