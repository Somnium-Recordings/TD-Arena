from tda import BaseExt


class State(BaseExt):
	"""
    TODO: Can we use osc return values for things like active clip/deck to reduce UI delay?
    """
	def __init__(self, ownerComponent, logger):
		super().__init__(ownerComponent, logger)
		self.oscOut = ownerComponent.op('oscout1')

		self.oscControlList = ownerComponent.op('opfind_oscControls')
		self.initializedControlList = ownerComponent.op('table_initializedControls')
		self.InitOSCControls()

		self.logInfo('UIState initialized')

	def InitOSCControls(self):
		"""
		TODO: call this on composition [re]load
		"""
		self.oscControlState = {}
		self.initializedControlList.clear()
		self.OnCtrlOPListChange()

	def SendMessage(self, address, *args):
		"""
		TODO: move this out of State and into OSC/Client?
		"""
		if address:
			self.logDebug('sending message to {}: {}'.format(address, args))
			self.oscOut.sendOSC(address, args)
		else:
			self.logWarning('attempted to send to invalid address {}'.format(address))

	def OnCtrlOPListChange(self):
		activeAddresses = set()
		for row in self.oscControlList.rows()[1:]:
			[path, address] = [c.val for c in row]

			activeAddresses.add(address)
			if address not in self.oscControlState:
				self.logDebug('initilizing ui state for {}'.format(address))
				self.oscControlState[address] = {'op': op(path)}
				self.SendMessage(address, '?')  # request initial value

		inactiveAddresses = set(self.oscControlState.keys()) - activeAddresses
		for address in inactiveAddresses:
			self.logDebug('clearing ui state for {}'.format(address))
			del self.oscControlState[address]
			if self.initializedControlList.row(address) is not None:
				self.initializedControlList.deleteRow(address)

	def OnOSCReply(self, address, *args):
		if address not in self.oscControlState:
			self.logWarning('recieved OSC reply for unkonwn address {}'.format(address))
			return

		if len(args) != 1:
			self.logWarning(
				'expected OSC reply to have exactly 1 arg but got {}, ignoring message'.
				format(len(args))
			)
			return

		self.logDebug('setting initial value for {} to {}'.format(address, args[0]))
		ctrlState = self.oscControlState[address]
		ctrlState['op'].par.Value0 = args[0]
		self.initializedControlList.appendRow(
			[address, '{}/valueOut'.format(ctrlState['op'].path)]
		)
