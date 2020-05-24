from tda import LoadableExt
from tdaUtils import getCellValues, intIfSet, layoutComps


class DeckCtrl(LoadableExt):
	@property
	def SelectedDeck(self):
		return self.composition.par.Selecteddeck.val

	def __init__(self, ownerComponent, logger, state, render):
		super().__init__(ownerComponent, logger)
		self.render = render
		self.state = state
		self.deckTemplate = ownerComponent.op('deckTemplate')

		self.composition = None
		self.deckContainer = None
		self.deckList = None
		self.decks = None
		self.SendState()
		self.logInfo('initialized')

	def Reinit(self):
		self.setUnloaded()
		self.SendState()
		self.composition = None
		self.deckContainer = None
		self.deckList = None
		self.decks = None
		self.logInfo('reinitialized')

	def Load(self):
		self.setLoading()
		self.logInfo('loading composition')

		self.composition = self.ownerComponent.op('../composition')
		assert self.composition, 'could not find composition component'

		self.deckContainer = self.composition.op('decks')
		if not self.deckContainer:
			self.logInfo('decks op not found in composition, initalizing')
			self.deckContainer = self.composition.create(baseCOMP, 'decks')

		# NOTE: deck list needs to stay in the composition so we can store names
		self.deckList = self.deckContainer.op('deckList')
		if not self.deckList:
			self.logInfo('decklist not found in composition, initalizing')
			self.deckList = self.deckContainer.create(tableDAT, 'deckList')
			self.deckList.replaceCol(0, ['One', 'Two', 'Three'])

		self.decks = [
			self.findOrCreateDeck(i) for i, _ in enumerate(self.deckList.col(0))
		]

		self.layoutDeckContainer()

		self.logInfo('loaded {} decks in composition'.format(len(self.decks)))
		self.setLoaded()
		self.SendState()

	def AddDeck(self):
		# TODO: show add button if DeckCtrl not initialized
		# TODO: find way to prompt for deck name
		assert False, 'update AddDeck to work with new state system (sans replicator)'
		self.deckList.appendRow(['Deck {}'.format(self.deckList.numRows)])
		self.layoutDeckContainer()
		# call layout after creating

	def SetClip(self, clipLocation, clipID):
		self.clipCell(clipLocation).val = clipID

	def GetClipID(self, clipLocation):
		return intIfSet(self.clipCell(clipLocation).val)

	def ClearClip(self, clipLocation):
		cell = self.clipCell(clipLocation)
		clipID = cell.val
		cell.val = ''

		return intIfSet(clipID)

	def SendState(self):
		self.logDebug('sending state')

		state = {
			'list': self.getDeckListState() if self.Loaded else [],
			'layers': self.getLayerState() if self.Loaded else [],
			'selected': self.SelectedDeck if self.Loaded else None
		}

		self.state.Update('decks', state)

	def getLayerState(self):
		return [
			getCellValues(layer) for layer in self.decks[self.SelectedDeck].rows()
		]

	def getDeckListState(self):
		return [getCellValues(deck) for deck in self.deckList.rows()]

	def clipCell(self, clipLocation):
		(layerNumber, clipNumber) = clipLocation

		deckOpName = 'deck{}'.format(self.SelectedDeck)
		deck = self.deckContainer.op(deckOpName)
		assert deck, 'could not find requested deck ({})to add clip to'.format(
			deckOpName
		)

		return deck[layerNumber, clipNumber]

	def createDeck(self, deckOpName: str):
		self.logDebug('creating deck op: {}'.format(deckOpName))
		return self.deckContainer.copy(self.deckTemplate, name=deckOpName)

	def findOrCreateDeck(self, deckNumber: int):
		deckOpName = 'deck{}'.format(deckNumber)
		existingDeck = self.deckContainer.op('./{}'.format(deckOpName))

		return existingDeck or self.createDeck(deckOpName)

	def deckName(self, deckNumber):
		return self.deckList[deckNumber, 0].val

	def layoutDeckContainer(self):
		# TODO: my python foo is weak, there's gotta be a better way to combine lists...
		comps = [self.deckList]
		comps.extend(self.decks)
		layoutComps(comps)
