from typing import Callable, Dict, List, TypedDict, Union

from oscDispatcher import OSCDispatcher
from tda import BaseExt

OSCValue = Union[str, int, float]

# CtrlState = Typed


class CtrlState(TypedDict, total=False):
	handlers: List[Callable]
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

		# TODO: remove below this line
		return
		self.initializedControlList.clear()
		self.OnCtrlOPListChange()

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

	def RegisterCtrl(
		self, address: str, setCtrlValueHandler: Callable[[str, OSCValue], None]
	) -> Union[None, OSCValue]:
		self.logDebug(f'registering control handler for {address}')

		if ctrlState := self.oscControlState.get(address, None) is None:
			ctrlState = {'currentValue': None, 'handlers': [setCtrlValueHandler]}
			self.oscControlState[address] = ctrlState
		else:
			ctrlState['handlers'].append(setCtrlValueHandler)

		if ctrlState['currentValue'] is None:
			self.logDebug(f'requesting initial value for {address}')
			self.SendMessage(address, '?')
		else:
			setCtrlValueHandler(address, ctrlState['currentValue'])

	def UnRegisterCtrl(self):
		pass

	def onOSCReply(self, address, *args):
		if address not in self.oscControlState:
			self.logWarning(f'received OSC reply for unknown address {address}')
			return

		if len(args) != 1:
			self.logWarning(
				f'expected OSC reply to have exactly 1 arg but got {len(args)}, ignoring message'
			)
			return

		return
		# TODO: delete below this line
		self.logDebug(f'setting value of {address} to {args[0]}')

		ctrlState = self.oscControlState[address]
		# TODO: rather than set Value0 here, store value on state and call handlers
		# the "local UI" handler should handle mapping changes
		# TODO: call registered ctrl handlers
		ctrlState['op'].par.Value0 = args[0]

		# If this is the message with the initial value for a control,
		# mark it as initialized so that we start sending data out through
		# OSC
		if self.initializedControlList.row(address) is None:
			valueOutAddress = '{}/valueOut'.format(ctrlState['op'].path)
			opFamily = op(valueOutAddress).family  # CHOP, DAT, etc.

			self.initializedControlList.appendRow([address, valueOutAddress, opFamily])

	###################################################
	##              Deprecated                       ##
	###################################################
	def OnCtrlOPListChange(self):
		return
		inactiveAddresses = set(self.oscControlState.keys())
		for row in self.oscControlList.rows()[1:]:
			[path, address] = [c.val for c in row]

			inactiveAddresses.discard(address)
			if address not in self.oscControlState:
				self.logDebug('initializing ui state for {address}')
				self.oscControlState[address] = {'op': op(path)}

				# TODO: don't do this here, do it in RegisterCtrl instead
				self.SendMessage(address, '?')  # request initial value
				# NOTE: on receipt of initial value, address will be added to initializedControlList

		for inactiveAddress in inactiveAddresses:
			self.logDebug(f'clearing ui state for {inactiveAddress}')
			del self.oscControlState[inactiveAddress]
			if self.initializedControlList.row(inactiveAddress) is not None:
				self.initializedControlList.deleteRow(inactiveAddress)
