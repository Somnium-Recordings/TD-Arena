import json
from typing import Union

from tda import BaseExt, Par
from tdaUtils import syncToDat


class State(BaseExt):
	"""
    TODO: Can we use osc return values for things like active clip/deck to reduce UI delay?
    """
	def __init__(self, ownerComponent, logger):
		super().__init__(ownerComponent, logger)
		self.state = ownerComponent.op('touchin_state')

		self.deckState = ownerComponent.op('deckState')
		self.deckList = self.deckState.op('table_deckList')
		self.deckLayers = self.deckState.op('table_deckLayers')

		self.SelectedDeck: Union(int, None)
		self._SelectedDeck: Par(Union(int, None))
		TDF = op.TDModules.mod.TDFunctions
		TDF.createProperty(self, 'SelectedDeck', value=None, readOnly=True)

		self.clipState = ownerComponent.op('clipState')
		self.clipList = self.clipState.op('table_clipList')

		self.layerState = ownerComponent.op('layerState')
		self.layerList = self.layerState.op('table_layers')

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
			self.oscOut.sendOSC(address, args)

	def OnChange(self, message):
		if absTime.seconds < 5:
			# TODO: Figure out why updateDeckState(None) causes crash
			# For some reason if the project is saved with a compositon
			# loaded, then re-opened, touch will hang when
			# syncToDat(None, self.deckLayers) is called
			self.logInfo('ignoring state updates during init')
			return

		state = json.loads(message)
		# TODO: map state props to dats rathar than doing this manually
		if 'layers' in state:
			self.updateLayerState(state['layers'])
		if 'decks' in state:
			self.updateDeckState(state['decks'])
		if 'clips' in state:
			self.updateClipState(state['clips'])

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

		self.logDebug('setting initial value for {}'.format(address))
		ctrlState = self.oscControlState[address]
		ctrlState['op'].par.Value0 = args[0]
		self.initializedControlList.appendRow(
			[address, '{}/valueOut'.format(ctrlState['op'].path)]
		)

	def updateClipState(self, clips):
		syncToDat(clips, self.clipList)

	def updateDeckState(self, decks):
		if decks is None:
			syncToDat(None, self.deckList)
			syncToDat(None, self.deckLayers)
			self._SelectedDeck.val = None
			return

		selectedIndex = int(decks['selected'])
		syncToDat([[deck['name']] for deck in decks['list']], self.deckList)
		syncToDat(decks['list'][selectedIndex]['layers'], self.deckLayers)
		self._SelectedDeck.val = selectedIndex

	def updateLayerState(self, layers):
		syncToDat(layers, self.layerList)
