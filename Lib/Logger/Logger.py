import logging
import logging.handlers
import sys

LOG_FORMAT = '{source}\t{message}\t{absframe}\t{frame}\t{type}'


def formatLog(comp, message):
	return LOG_FORMAT.format(
		source=comp.path,
		message=message,
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
		self.logFile = tdu.expandPath(
			'lib://../Logs/TDArena.{}.log'.format(self.logName)
		)
		self.logger = logging.getLogger(self.logName)

		if self.logger.hasHandlers():
			if not self.debug:
				self.fileHandler = self.logger.handlers[0]

				self.Debug(self.ownerComp, 'logger already inialized, skipping re-init')
				return

			for handler in self.logger.handlers:
				self.logger.removeHandler(handler)

		fileHandler = logging.handlers.RotatingFileHandler(
			self.logFile,
			maxBytes=1024 * 256,
			backupCount=1,
		)
		formatter = logging.Formatter('%(levelname)s\t%(message)s\t%(asctime)s')
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
		assert self.fileHandler, 'Logger.Clear() cannot be called before the handler is inialized'
		self.fileHandler.doRollover()

	def LogTouchError(self, message, absFrame, frame, severity, compType, source):  # pylint: disable=too-many-arguments
		message = LOG_FORMAT.format(
			source=source,
			message=message.replace('\n', ''),
			absframe=absFrame,
			frame=frame,
			type=compType
		)

		if severity == 0:
			self.logger.info(message)
		elif severity == 1:
			self.logger.warning(message)
		elif severity == 2:
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
