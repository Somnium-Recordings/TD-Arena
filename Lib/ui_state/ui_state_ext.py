import traceback
from typing import Any, Callable, TypedDict, Union, cast

from logger import logging_mixins
from oscDispatcher import (
	OSCDispatcher,
	OSCHandler,
	OSCHandlerAddressCallback,
	OSCMappings,
	OSCValue,
)

# TODO: Once we migrate to python 3.11 and are able to use generic typed dicts
# See: https://github.com/python/cpython/issues/89026#issuecomment-1116093221
# class CtrlState(TypedDict, Generic[OSCValue]):
# 	# key is sourceName
# 	handlers: dict[str, Callable]
# 	currentValue: Union[OSCValue, None]


class CtrlState(TypedDict):
	# key is sourceName
	handlers: dict[str, Callable]
	currentValue: Union[OSCValue, None]


class UIStateExt(logging_mixins.ComponentLoggerMixin):

	def __init__(self, ownerComponent: OP):
		self.ownerComponent = ownerComponent
		self.oscIn = cast(oscinDAT, ownerComponent.op('oscin1'))

		self.dispatcher = OSCDispatcher(
			ownerComponent, defaultMapping={'handler': self.onOSCReply}
		)

		self.InitOSCControls()

		self.logInfo('initialized')

	def InitOSCControls(self):
		"""
		TODO: call this on composition [re]load
		"""
		self.oscControlState: dict[str, CtrlState] = {}

	def SendMessage(self, address: str, *args: OSCValue):
		if address:
			self.logDebug(f'UI -> Render -- {address} with {args}')
			self.oscIn.sendOSC(address, args)
		else:
			self.logWarning(f'attempted to send to invalid address {address}')

	def Dispatch(self, address: str, *args: OSCValue):
		self.dispatcher.Dispatch(address, *args)

	def MapOSCHandler(self, address: str, handler: OSCHandler):
		self.dispatcher.Map(address, handler)

	def MapOSCHandlers(self, mappings: OSCMappings):
		self.dispatcher.MapMultiple(mappings)

	def DumpCtrlState(self):
		debug(self.oscControlState)

	def RegisterCtrl(
		self,
		address: str,
		sourceName: str,
		setCtrlValueHandler: OSCHandlerAddressCallback,
		*,
		alwaysRequestValue: bool = False
	) -> None:
		self.logDebug(f'registering control {sourceName} handler @ {address}')

		# TODO: should this be a part of the OSCDispatcher rather than a parallel system?
		if (ctrlState := self.oscControlState.get(address, None)) is None:
			ctrlState = CtrlState(
				handlers={sourceName: setCtrlValueHandler}, currentValue=None
			)
			self.oscControlState[address] = ctrlState
		else:
			if sourceName in ctrlState['handlers']:
				# This can happen if DeregisterCtrl isn't called on cleanup,
				# or if a ctrl is registered more than once
				self.logWarning(
					f'duplicate ctrl handler registered for {sourceName} @ {address}'
				)
			ctrlState['handlers'][sourceName] = setCtrlValueHandler

		if (
			alwaysRequestValue
			or (ctrlState['currentValue'] is None and len(ctrlState['handlers']) == 1)
		):
			self.logDebug(f'requesting initial value @ {address}')
			self.SendMessage(address, '?')

		if ctrlState['currentValue'] is not None:
			self.logDebug(
				f'currentValue in state, calling handler immediately @ {address}'
			)
			# TODO: remove cast once we can make this generic in python 3.11
			setCtrlValueHandler(address, cast(Any, ctrlState['currentValue']))

	def DeregisterCtrl(self, address: str, sourceName: str):
		if (ctrlState := self.oscControlState.get(address, None)) is None:
			self.logWarning(
				f'attempted to deregister an unknown ctrl for {sourceName} @ {address}'
			)
			return

		if sourceName not in ctrlState['handlers']:
			self.logWarning(
				f'attempted to deregister unknown handler {sourceName} @ {address}'
			)
			return

		if len(ctrlState['handlers']) > 1:
			self.logDebug(f'deregistering {sourceName} handler @ {address}')
			del ctrlState['handlers'][sourceName]
		else:
			self.logDebug(
				f'deregistering ctrl since {sourceName} is the last handler @ {address}'
			)
			del self.oscControlState[address]

	def UpdateCtrlValue(
		self,
		address: str,
		newValue: OSCValue,
		source: str,
		*,
		pickup: bool = False
	) -> None:
		if (controlState := self.oscControlState.get(address, None)) is None:
			self.logWarning(
				f'attempted to update CTRL value for unknown address {address}'
			)
			return

		if newValue == controlState['currentValue']:
			return

		debug(type(controlState['currentValue']))
		debug(type(newValue))
		if (
			pickup and isinstance(controlState['currentValue'], float)
			and isinstance(newValue, float)
			and abs(controlState['currentValue'] - newValue) > 1 / 27
		):
			debug('diff is: ', controlState['currentValue'] - newValue)
			return

		controlState['currentValue'] = newValue

		# Optimistically update any other UI controls
		for sourceName, handler in controlState['handlers'].items():
			if sourceName != source:
				try:
					handler(address, newValue)
				except:  # noqa: E722
					self.logError(
						f'failed to apply CtrlValue change handler ({sourceName}) @ {address}:'
						f'\n{traceback.format_exc()}'
					)

		# Send change to renderer
		self.SendMessage(address, newValue)

	def onOSCReply(self, address, *args):  # noqa: ANN001, ANN002
		if (controlState := self.oscControlState.get(address, None)) is None:
			self.logWarning(f'received OSC reply for unknown address {address}')
			return

		if len(args) != 1:
			self.logWarning(
				f'expected OSC reply to have exactly 1 arg but got {len(args)}, ignoring message'
			)
			return

		currentValue = args[0]
		controlState['currentValue'] = currentValue
		for handler in controlState['handlers'].values():
			handler(address, currentValue)
