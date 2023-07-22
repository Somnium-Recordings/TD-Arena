from collections.abc import Mapping
from logging import LoggerAdapter
from types import TracebackType
from typing import Optional, TypedDict, Union

from typing_extensions import Unpack

from .log_manager import getComponentLogger

# Copied from the logger types T_T
_SysExcInfoType = Union[(
	tuple[type[BaseException], BaseException,
							Union[TracebackType, None]], tuple[None, None, None]
)]
_ExcInfoType = Union[None, bool, _SysExcInfoType, BaseException]


class LogKwargs(TypedDict, total=False):
	exc_info: _ExcInfoType
	stack_info: bool
	extra: Mapping[str, object]


class ComponentLoggerMixin():
	ownerComponent: OP
	_componentLogger: Optional[LoggerAdapter] = None

	@property
	def componentLogger(self) -> LoggerAdapter:
		if not self._componentLogger:
			try:
				self._componentLogger = getComponentLogger(self.ownerComponent)
			except AttributeError as e:
				raise NotImplementedError(
					'the ownerComponent property must be set in subclasses'
					' before ComponentLoggerMixins methods can be used'
				) from e

		return self._componentLogger

	def newLog(
		self, msg: object, *args: object, **kwargs: Unpack[LogKwargs]
	) -> None:
		self.componentLogger.info(msg, *args, **kwargs)

	def logInfo(
		self, msg: object, *args: object, **kwargs: Unpack[LogKwargs]
	) -> None:
		self.componentLogger.info(msg, *args, **kwargs)

	def logDebug(
		self, msg: object, *args: object, **kwargs: Unpack[LogKwargs]
	) -> None:
		self.componentLogger.debug(msg, *args, **kwargs)

	def logWarning(
		self, msg: object, *args: object, **kwargs: Unpack[LogKwargs]
	) -> None:
		self.componentLogger.warning(msg, *args, **kwargs)

	def logError(
		self, msg: object, *args: object, **kwargs: Unpack[LogKwargs]
	) -> None:
		self.componentLogger.error(msg, *args, **kwargs)
