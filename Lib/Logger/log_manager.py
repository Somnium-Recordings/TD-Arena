import logging
from logging import LogRecord
from logging.handlers import RotatingFileHandler
from typing import Optional

from .utils import clearLogHandlers, getHandlers, normalizeSourcePath


class TdContextFilter(logging.Filter):

	def filter(self, record: LogRecord) -> bool:
		# TODO: can/should we use encode for this?
		record.msg = record.msg.replace('\n', '\\n').replace('\t', '\\t')

		if not hasattr(record, 'absframe'):
			record.absframe = absTime.frame

		component: Optional[OP] = getattr(record, 'component', None)

		if not hasattr(record, 'source'):
			record.source = normalizeSourcePath(
				component.path if component else f'/{record.name.replace(".", "/")}'
			)

		if not hasattr(record, 'type'):
			record.type = component.type if component else 'UNKNOWN'

		if not hasattr(record, 'frame'):
			record.frame = component.time.frame if component else me.time.frame

		return True


def configureLogHandler(logger: logging.Logger):
	logName = 'engine' if op('/render') else 'ui'

	fileHandler = RotatingFileHandler(
		filename=tdu.expandPath(f'Logs/{logName}.log'),
		maxBytes=1024 * 256,
		backupCount=1,
	)
	fileHandler.addFilter(TdContextFilter())
	fileHandler.setFormatter(
		logging.Formatter(
			'%(source)s\t%(message)s\t%(absframe)s\t%(frame)s\t%(type)s\t%(levelname)s\t%(asctime)s'
		)
	)
	logger.addHandler(fileHandler)

	logger.setLevel(logging.DEBUG)


def ensureLogHandlersPresent(logName: Optional[str] = None):
	logger = logging.getLogger(logName)
	if not logger.hasHandlers():
		configureLogHandler(logger)


def reloadLogHandlers(logName: Optional[str] = None):
	clearLogHandlers(logName)
	ensureLogHandlersPresent(logName)


def getComponentLogger(component: OP) -> logging.LoggerAdapter:
	ensureLogHandlersPresent()

	logName = normalizeSourcePath(component.path)[1:].replace('/', '.')

	logger = logging.getLogger(logName)

	return logging.LoggerAdapter(logger, {
		'component': component,
	})


def rotateLogs(logName: Optional[str] = None):
	for handler in getHandlers(logging.getLogger(logName), RotatingFileHandler):
		handler.doRollover()
