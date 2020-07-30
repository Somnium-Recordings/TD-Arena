import json
from typing import Union

from tda import Par
from tdaUtils import syncToDat

TDF = op.TDModules.mod.TDFunctions


class StateUI:
	"""
	TODO: rename op shorcut to uiState to be consistent with renderState
    TODO: Can we use osc return values for things like active clip/deck to reduce UI delay?

    """
	def __init__(self, ownerComponent):
		self.ownerComponent = ownerComponent
		self.state = ownerComponent.op('touchin_state')

		self.deckState = ownerComponent.op('deckState')
		self.deckList = self.deckState.op('table_deckList')
		self.deckLayers = self.deckState.op('table_deckLayers')
		self.SelectedDeck: Union(int, None)
		self._SelectedDeck: Par(Union(int, None))
		TDF.createProperty(self, 'SelectedDeck', value=None, readOnly=True)

		self.clipState = ownerComponent.op('clipState')
		self.clipList = self.clipState.op('table_clipList')

		self.layerState = ownerComponent.op('layerState')
		self.layerList = self.layerState.op('table_layers')

		self.oscOut = ownerComponent.op('oscout1')

	def SendMessage(self, address, *args):
		"""
		TODO: move this out of State and into OSC/Client?
		"""
		self.oscOut.sendOSC(address, args)

	def OnChange(self, message):
		state = json.loads(message)
		# TODO: map state props to dats rathar than doing this manually
		if 'decks' in state:
			self.updateDeckState(state['decks'])
		if 'clips' in state:
			self.updateClipState(state['clips'])
		if 'layers' in state:
			self.updateLayerState(state['layers'])

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
