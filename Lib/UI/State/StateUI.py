from typing import Union

from tda import Par

TDJ = op.TDModules.mod.TDJSON
TDF = op.TDModules.mod.TDFunctions

MAX_WAIT_CYCLES = 10


def syncToDat(data, targetDat):
	rowCount = len(data)
	columnCount = len(data[0]) if rowCount > 0 else 0
	targetDat.setSize(rowCount, columnCount)

	for rowIndex, row in enumerate(data):
		for columnIndex, cell in enumerate(row):
			targetDat[rowIndex, columnIndex] = cell or ''


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
		self.SelectedDeck: Union(bool, None)
		self._SelectedDeck: Par(bool)
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

	def OnChange(self):
		state = TDJ.datToJSON(self.state)
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
		syncToDat(decks['list'], self.deckList)
		syncToDat(decks['layers'], self.deckLayers)
		self._SelectedDeck.val = decks['selected']

	def updateLayerState(self, layers):
		syncToDat(layers, self.layerList)
