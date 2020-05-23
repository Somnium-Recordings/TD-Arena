from tdaUtils import getCellValues, intIfSet, layoutComps


class DeckCtrl:
	@property
	def DeckList(self):
		return self.deckList

	@property
	def StateDATs(self):
		"""
        paths to DATs that RenderState should watch for changes
        TODO: use dependency here and update when loadComposition is fired
        """
		compPath = self.composition.path
		return ' '.join(
			['{}/decks/deckList'.format(compPath), '{}/decks/deck*'.format(compPath)]
		)

	@property
	def ActiveDeck(self):
		"""
        TODO: is there a better way to handle this than referencing
              the par from self.render?
		This should be stored on the composition and passed back through state.
		Controlled through OSC.
        """
		return self.render.par.Activedeck.val

	def __init__(self, ownerComponent, logger, state, render):
		self.ownerComponent = ownerComponent
		self.logger = logger
		self.render = render
		self.state = state
		self.deckTemplate = ownerComponent.op('deckTemplate')

		# NOTE: These lines should be mirrored in Reinit
		self.composition = None
		self.deckContainer = None
		self.deckList = None
		self.decks = None
		self.logInfo('initialized')
		# self.SendState()

	def Reinit(self):
		self.composition = None
		self.deckContainer = None
		self.deckList = None
		self.decks = None
		self.logInfo('reinitialized')

	def Load(self):
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
			self.deckList.replaceCol(0, ['deck0', 'deck1', 'deck2'])

		self.decks = {}
		for deckName in [d.val for d in self.deckList.col(0)]:
			self.decks[deckName] = self.findOrCreateDeck(deckName)

		self.layoutDeckContainer()

		self.logInfo('loaded {} decks in composition'.format(self.deckList.numRows))

	def AddDeck(self):
		# TODO: show add button if DeckCtrl not initialized
		# TODO: find way to prompt for deck name
		assert False, 'update AddDeck to work without replicator'
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
		newState = [] if not self.decks else [
			{
				'name': deckName,
				'layers': [getCellValues(layer) for layer in deck.rows()],
			} for deckName, deck in self.decks
		]

		self.state.Update('decks', newState)

	def clipCell(self, clipLocation):
		(layerNumber, clipNumber) = clipLocation

		deckOpName = 'deck{}'.format(self.ActiveDeck)
		deck = self.deckContainer.op(deckOpName)
		assert deck, 'could not find requested deck ({})to add clip to'.format(
			deckOpName
		)

		return deck[layerNumber, clipNumber]

	def createDeck(self, deckName):
		self.logInfo('creating deck: {}'.format(deckName))
		return self.deckContainer.copy(self.deckTemplate, name=deckName)

	def findOrCreateDeck(self, deckName):
		existingDeck = self.deckContainer.op('./' + deckName)

		return existingDeck or self.createDeck(deckName)

	def layoutDeckContainer(self):
		# TODO: my python foo is weak, there's gotta be a better way to combine lists...
		comps = [self.deckList]
		comps.extend(self.decks.values())
		layoutComps(comps)

	def logInfo(self, *args):
		self.logger.Info(self.ownerComponent, *args)

	def logDebug(self, *args):
		self.logger.Debug(self.ownerComponent, *args)
