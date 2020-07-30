from tda import LoadableExt

# TODO: make this configurable ?
# TODO: derive row count from layers?
DECK_ROW_COUNT = 3
DECK_COLUMN_COUNT = 10

STATE_KEY = 'decks'


def createDeckState(deckName: str):
	return {
		'name': deckName,
		'layers': [[None] * DECK_COLUMN_COUNT for _ in range(DECK_ROW_COUNT)]
	}


def createInitalState():
	return {
		'list': [createDeckState(n) for n in ['Deck One', 'Deck Two', 'Deck Three']],
		'selected': 0
	}


class DeckCtrl(LoadableExt):
	@property
	def selectedDeckLayerState(self):
		state = self.getState()
		if state is None:
			return None
		return state['list'][state['selected']]['layers']

	def __init__(
		self, ownerComponent, logger, state, render, clipCtrl, layerCtrl, thumbnails
	):  # pylint: disable=too-many-arguments
		super().__init__(ownerComponent, logger)
		self.render = render
		self.state = state
		self.clipCtrl = clipCtrl
		self.layerCtrl = layerCtrl
		self.thumbnails = thumbnails
		self.composition = ownerComponent.op('../composition')
		assert self.composition, 'could not find composition component'

	# Set default state
	def Init(self):
		self.setUnloaded()
		self.sendState(None)
		self.logInfo('initialized')

	def Load(self):
		self.setLoading()
		self.logInfo('loading composition')

		state = self.getState()
		if state is None:
			self.logInfo('no existing deck state. Initalizing...')
			state = createInitalState()
		else:
			self.logInfo('existing deck state found. Skipping init.')

		self.sendState(state)

		self.logInfo('loaded {} decks in composition'.format(len(state['list'])))
		self.setLoaded()

	def AddDeck(self):
		self.logInfo('TODO: add Deck')
		# TODO: show add button if DeckCtrl not initialized
		# TODO: find way to prompt for deck name
		assert False, 'update AddDeck to work with new state system (sans replicator)'
		# self.deckList.appendRow(['Deck {}'.format(self.deckList.numRows)])
		# self.layoutDeckContainer()
		# call layout after creating

	def ConnectClip(self, clipLocation):
		(layerNumber, _) = clipLocation
		clipID = self.getClipID(clipLocation)

		self.logInfo(
			'connecting clip #{} at {} to layer {}'.format(
				clipID, clipLocation, layerNumber
			)
		)
		self.layerCtrl.SetClip(layerNumber, clipID)

	def LoadClip(self, clipLocation, sourceType, name, path):
		clipID = self.getClipID(clipLocation)
		self.logInfo(
			'laoding {} "{}" into {}'.format(sourceType, name, clipLocation)
		)

		if clipID is not None:
			self.clipCtrl.ReplaceSource(sourceType, name, path, clipID)
		else:
			clip = self.clipCtrl.CreateClip(sourceType, name, path)
			self.setClipID(clipLocation, clip.digits)

	def ClearClip(self, clipLocation):
		self.logInfo('clearing clip at {}'.format(clipLocation))
		clipID = self.getClipID(clipLocation)

		if clipID is not None:
			self.setClipID(clipLocation, None)
			self.layerCtrl.ClearClipID(clipID)

	def getClipID(self, clipLocation):
		(layerNumber, clipNumber) = clipLocation
		return self.selectedDeckLayerState[layerNumber][clipNumber]

	def setClipID(self, clipLocation, clipID):
		(layerNumber, clipNumber) = clipLocation
		# TODO: this mutation is kind of gross but the alternative is also gross
		self.selectedDeckLayerState[layerNumber][clipNumber] = clipID
		self.sendState(self.getState())

	def sendState(self, state):
		self.logDebug('sending state')
		self.state.Update(STATE_KEY, state)
		self.thumbnails.OnSelectedDeckStateUpdate(self.selectedDeckLayerState)

	def getState(self):
		return self.state.Get(STATE_KEY, None)

	# def getLayerState(self):
	# 	return [
	# 		getCellValues(layer) for layer in self.decks[self.SelectedDeck].rows()
	# 	]

	# def getDeckListState(self):
	# 	return [getCellValues(deck) for deck in self.deckList.rows()]

	# def clipCell(self, clipLocation):
	# 	(layerNumber, clipNumber) = clipLocation

	# 	deckOpName = 'deck{}'.format(self.SelectedDeck)
	# 	deck = self.deckContainer.op(deckOpName)
	# 	assert deck, 'could not find requested deck ({})to add clip to'.format(
	# 		deckOpName
	# 	)

	# 	return deck[layerNumber, clipNumber]

	# def deckName(self, deckNumber):
	# 	return self.deckList[deckNumber, 0].val
