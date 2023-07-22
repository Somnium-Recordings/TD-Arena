import traceback
from typing import Any, Callable, TypedDict, TypeVar, Union, cast

from oscDispatcher import OSCDispatcher
from tda import BaseExt

OSCValue = Union[str, int, float, bool, list[int]]
_OSCValue = TypeVar('_OSCValue', str, int, float, bool, list[int])

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


class UIStateExt(BaseExt):

	def __init__(self, ownerComponent: OP, logger):  # noqa: ANN001
		super().__init__(ownerComponent, logger)
		self.oscIn = cast(oscinDAT, ownerComponent.op('oscin1'))

		self.dispatcher = OSCDispatcher(
			ownerComponent, logger, defaultMapping={'handler': self.onOSCReply}
		)

		self.oscControlList = ownerComponent.op('opfind_oscControls')
		self.initializedControlList = ownerComponent.op('table_initializedControls')
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

	def Dispatch(self, *args):  # noqa: ANN002
		self.dispatcher.Dispatch(*args)

	def MapOSCHandler(self, *args):  # noqa: ANN002
		self.dispatcher.Map(*args)

	def MapOSCHandlers(self, *args):  # noqa: ANN002
		self.dispatcher.MapMultiple(*args)

	def DumpCtrlState(self):
		print(self.oscControlState)  # noqa: T201

	def RegisterCtrl(
		self,
		address: str,
		sourceName: str,
		setCtrlValueHandler: Callable[[str, _OSCValue], None],
		alwaysRequestValue=False  # noqa: ANN001, FBT002
	) -> Union[None, _OSCValue]:
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
		self, address: str, newValue: OSCValue, source: str
	) -> None:
		if (controlState := self.oscControlState.get(address, None)) is None:
			self.logWarning(
				f'attempted to update CTRL value for unknown address {address}'
			)
			return

		if newValue == controlState['currentValue']:
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

	def UnRegisterCtrl(self):
		pass

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
