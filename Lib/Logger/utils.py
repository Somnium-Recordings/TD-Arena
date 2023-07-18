import logging
import re
from typing import Optional, TypeVar

HANDLER_TYPE = TypeVar('HANDLER_TYPE')


def getHandlers(
	logger: logging.Logger, HandlerClass: type[HANDLER_TYPE]
) -> list[HANDLER_TYPE]:  # yapf-disable
	return [
		handler for handler in logger.handlers if isinstance(handler, HandlerClass)
	]


def isConfigured(logName: str):
	return logName in logging.Logger.manager.loggerDict


def clearLogHandlers(logName: Optional[str]):
	logger = logging.getLogger(logName)

	while logger.hasHandlers():
		handler = logger.handlers[0]
		handler.close()
		logger.removeHandler(handler)


RENDER_ROOT_PATH_RE = re.compile(r'^/render')


def normalizeSourcePath(path: str) -> str:
	return re.sub(RENDER_ROOT_PATH_RE, '/tdArena/engine_render', path)
