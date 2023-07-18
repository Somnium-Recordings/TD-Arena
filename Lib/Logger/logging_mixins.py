from collections.abc import Mapping
from logging import LoggerAdapter
from types import TracebackType
from typing import Optional, Union

from .log_manager import getComponentLogger

# Copied from the logger types T_T
_SysExcInfoType = Union[(
	tuple[type[BaseException], BaseException,
							Union[TracebackType, None]], tuple[None, None, None]
)]
_ExcInfoType = Union[None, bool, _SysExcInfoType, BaseException]


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

	# TODO: there has got to be a better way to copy the types from the logger to these functions...
	def logInfo(
		self,
		msg: object,
		*args: object,
		exc_info: _ExcInfoType = None,
		stack_info: bool = False,
		extra: Optional[Mapping[str, object]] = None,
	) -> None:
		self.componentLogger.info(
			msg, *args, exc_info=exc_info, stack_info=stack_info, extra=extra
		)

	def logDebug(
		self,
		msg: object,
		*args: object,
		exc_info: _ExcInfoType = None,
		stack_info: bool = False,
		extra: Optional[Mapping[str, object]] = None,
	) -> None:
		self.componentLogger.debug(
			msg, *args, exc_info=exc_info, stack_info=stack_info, extra=extra
		)

	def logWarning(
		self,
		msg: object,
		*args: object,
		exc_info: _ExcInfoType = None,
		stack_info: bool = False,
		extra: Optional[Mapping[str, object]] = None,
	) -> None:
		self.componentLogger.warning(
			msg, *args, exc_info=exc_info, stack_info=stack_info, extra=extra
		)

	def logError(
		self,
		msg: object,
		*args: object,
		exc_info: _ExcInfoType = None,
		stack_info: bool = False,
		extra: Optional[Mapping[str, object]] = None,
	) -> None:
		self.componentLogger.error(
			msg, *args, exc_info=exc_info, stack_info=stack_info, extra=extra
		)
