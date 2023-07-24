import logging
import logging.handlers

from .log_manager import rotateLogs
from .logging_mixins import ComponentLoggerMixin

LOG_FORMAT = '{source}\t{message}\t{absframe}\t{frame}\t{type}'

IGNORED_ERROR_SOURCES = ['/probe/instance', '/probe/dataType/items']


def escapeLogMessage(message: str) -> str:
	# TODO: can we use encode for this?
	return message.replace('\n', '\\n').replace('\t', '\\t')


def formatLog(comp, message):  # noqa: ANN001
	return LOG_FORMAT.format(
		source=comp.path,
		message=escapeLogMessage(message),
		absframe=absTime.frame,
		frame=comp.time.frame,
		type=comp.type,
	)


class LoggerExt(ComponentLoggerMixin):

	@property
	def logName(self):
		return self.ownerComponent.par.Logname.eval()

	@property
	def debug(self):
		return self.ownerComponent.par.Debug.eval()

	def __init__(self, ownerComponent: OP):
		self.ownerComponent = ownerComponent
		self.logFile = tdu.expandPath(f'Logs/TDArena.{self.logName}.log')
		self.rootLogger = logging.getLogger()

		self.logInfo('initialized')

	def Clear(self):
		rotateLogs()

	def ClearErrors(self):
		self.ownerComponent.par.Clearerrors.pulse()

	def LogCurrentErrors(self):
		self.ownerComponent.par.Logcurrenterrors.pulse()

	# TODO: can we use a custom formatter for this instead?
	def LogTouchError(  # noqa: PLR0913
		self, message, absFrame, frame, severity, compType, source  # noqa: ANN001
	):
		errorContext = {
			'source': source,
			'absframe': absFrame,
			'frame': frame,
			'type': compType
		}

		# NOTE: The documented numbers don't seem to line up with reality
		# See: https://forum.derivative.ca/t/error-dat-is-saing-severity-warning-while-its-python-callbacks-are-reporting-severity-error/286370/2
		# Docs(incorrect): https://docs.derivative.ca/ErrorDAT_Class#Callbacks
		if severity <= 1:
			self.rootLogger.info(message, extra=errorContext)
		elif severity == 2:  # noqa: PLR2004
			self.rootLogger.warning(message, extra=errorContext)
		elif severity == 3:  # noqa: PLR2004
			self.rootLogger.error(message, extra=errorContext)
		else:  # severity == 3
			self.rootLogger.critical(message, extra=errorContext)
