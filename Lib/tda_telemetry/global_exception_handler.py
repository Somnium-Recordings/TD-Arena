import logging
import sys
from types import TracebackType

logger = logging.getLogger(__name__)


def register_global_exception_handler():
	logger.info('registering global exception handler')
	sys.excepthook = global_exception_handler

	logger.debug('Global exception handler registered')


def global_exception_handler(
	exc_type: type, exc_value: BaseException, exc_traceback: TracebackType | None
):
	if not hasattr(  # noqa: SIM102
		exc_value, '__traceback__'
	) or exc_value.__traceback__ is None:
		if exc_traceback:
			exc_value.__traceback__ = exc_traceback

	# Call the default excepthook to print the exception to the console
	sys.__excepthook__(exc_type, exc_value, exc_traceback)

	try:
		# Use provided traceback if available, otherwise get it from the exception
		traceback = exc_traceback if exc_traceback is not None else exc_value.__traceback__

		# Forward exception to the logging system
		logger.error(
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
