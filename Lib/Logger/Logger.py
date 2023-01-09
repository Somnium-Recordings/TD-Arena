import logging
import logging.handlers
import sys

LOG_FORMAT = '{source}\t{message}\t{absframe}\t{frame}\t{type}'

IGNORED_ERROR_SOURCES = [
	'/probe/instance',
	'/probe/dataType/items',
]


def escapeLogMessage(message: str) -> str:
	# TODO: can we use encode for this?
	return message.replace('\n', '\\n').replace('\t', '\\t')


def formatLog(comp, message):
	return LOG_FORMAT.format(
		source=comp.path,
		message=escapeLogMessage(message),
		absframe=absTime.frame,
		frame=comp.time.frame,
		type=comp.type,
	)


class Logger:
	@property
	def logName(self):
		return self.ownerComp.par.Logname.eval()

	@property
	def debug(self):
		return self.ownerComp.par.Debug.eval()

	def __init__(self, ownerComp):
		self.ownerComp = ownerComp
		self.logFile = tdu.expandPath(f'Logs/TDArena.{self.logName}.log')
		self.logger = logging.getLogger(self.logName)

		if self.logger.hasHandlers():
			if not self.debug:
				self.fileHandler = self.logger.handlers[0]

				self.Debug(self.ownerComp, 'logger already initialized, skipping re-init')
				return

			for handler in self.logger.handlers:
				self.logger.removeHandler(handler)

		fileHandler = logging.handlers.RotatingFileHandler(
			self.logFile,
			maxBytes=1024 * 256,
			backupCount=1,
		)
		formatter = logging.Formatter('%(message)s\t%(levelname)s\t%(asctime)s')
		fileHandler.setFormatter(formatter)
		self.fileHandler = fileHandler

		self.logger.addHandler(self.fileHandler)

		if self.debug:
			consoleHandler = logging.StreamHandler(sys.stdout)
			consoleHandler.setFormatter(formatter)
			self.logger.addHandler(consoleHandler)

		self.logger.setLevel(logging.DEBUG)

		self.Info(self.ownerComp, '%s logger initialized', self.logName)

	def Clear(self):
		assert self.fileHandler, 'Logger.Clear() cannot be called before the handler is initialized'
		self.fileHandler.doRollover()

	def ClearErrors(self):
		self.ownerComp.par.Clearerrors.pulse()

	def LogCurrentErrors(self):
		self.ownerComp.par.Logcurrenterrors.pulse()

	def LogTouchError(self, message, absFrame, frame, severity, compType, source):  # pylint: disable=too-many-arguments
		if source in IGNORED_ERROR_SOURCES:
			return

		message = LOG_FORMAT.format(
			source=source,
			message=escapeLogMessage(message),
			absframe=absFrame,
			frame=frame,
			type=compType
		)

		# NOTE: The documented numbers don't seem to line up with reality
		# See: https://forum.derivative.ca/t/error-dat-is-saing-severity-warning-while-its-python-callbacks-are-reporting-severity-error/286370/2
		# Docs(incorrect): https://docs.derivative.ca/ErrorDAT_Class#Callbacks
		if severity <= 1:
			self.logger.info(message)
		elif severity == 2:
			self.logger.warning(message)
		elif severity == 3:
			self.logger.error(message)
		else:  # severity == 3
			self.logger.critical(message)

	def Debug(self, comp, msg, *args):
		self.logger.debug(formatLog(comp, msg), *args)

	def Info(self, comp, msg, *args):
		self.logger.info(formatLog(comp, msg), *args)

	def Error(self, comp, msg, *args):
		self.logger.error(formatLog(comp, msg), *args)

	def Warning(self, comp, msg, *args):
		self.logger.warning(formatLog(comp, msg), *args)

	def Critical(self, comp, msg, *args):
		self.logger.critical(formatLog(comp, msg), *args)
