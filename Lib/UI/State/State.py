from typing import Callable, Dict, TypedDict, Union

from oscDispatcher import OSCDispatcher
from tda import BaseExt

OSCValue = Union[str, int, float, bool]


class CtrlState(TypedDict, total=False):
	# key is sourceName
	handlers: Dict[str, Callable]
	currentValue: Union[OSCValue, None]


class State(BaseExt):

	oscControlState: Dict[str, CtrlState]

	def __init__(self, ownerComponent, logger):
		super().__init__(ownerComponent, logger)
		self.oscIn = ownerComponent.op('oscin1')

		self.dispatcher = OSCDispatcher(
			ownerComponent, logger, defaultMapping={'handler': self.onOSCReply}
		)

		self.oscControlList = ownerComponent.op('opfind_oscControls')
		self.initializedControlList = ownerComponent.op('table_initializedControls')
		self.InitOSCControls()

		self.logInfo('UIState initialized')

	def InitOSCControls(self):
		"""
		TODO: call this on composition [re]load
		"""
		self.oscControlState = {}

	def SendMessage(self, address, *args):
		if address:
			self.logDebug(f'UI -> Render -- {address} with {args}')
			self.oscIn.sendOSC(address, args)
		else:
			self.logWarning(f'attempted to send to invalid address {address}')

	def Dispatch(self, *args):
		self.dispatcher.Dispatch(*args)

	def MapOSCHandler(self, *args):
		self.dispatcher.Map(*args)

	def MapOSCHandlers(self, *args):
		self.dispatcher.MapMultiple(*args)

	def DumpCtrlState(self):
		print(self.oscControlState)

	def RegisterCtrl(
		self, address: str, sourceName: str,
		setCtrlValueHandler: Callable[[str, OSCValue], None]
	) -> Union[None, OSCValue]:
		self.logDebug(f'registering control {sourceName} handler @ {address}')

		if (ctrlState := self.oscControlState.get(address, None)) is None:
			ctrlState = {
				'currentValue': None,
				'handlers': {
					sourceName: setCtrlValueHandler
				}
			}
			self.oscControlState[address] = ctrlState
		else:
			if sourceName in ctrlState['handlers']:
				# This can happen if DeregisterCtrl isn't called on cleanup,
				# or if a ctrl is registered more than once
				self.logWarning(
					f'duplicate ctrl handler registered for {sourceName} @ {address}'
				)
			ctrlState['handlers'][sourceName] = setCtrlValueHandler

		if ctrlState['currentValue'] is None:  # TODO: an len(handlers) == 1?
			self.logDebug(f'requesting initial value @ {address}')
			self.SendMessage(address, '?')
		else:
			self.logDebug(
				f'currentValue in state, calling handler immediately @ {address}'
			)
			setCtrlValueHandler(address, ctrlState['currentValue'])

	def DeregisterCtrl(self, address, sourceName):
		if (ctrlState := self.oscControlState.get(address, None)) is None:
			self.logWarning(
				f'attempted to deregister an unknown ctrl for {sourceName} @ {address}'
			)
			return

		if not sourceName in ctrlState['handlers']:
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

		# Optimistically update any other UI controls
		for sourceName, handler in controlState['handlers'].items():
			if sourceName != source:
				handler(address, newValue)

		# Send change to renderer
		self.SendMessage(address, newValue)

	def UnRegisterCtrl(self):
		pass

	def onOSCReply(self, address, *args):
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
