import typing as T

from tda import LoadableExt
from tdaUtils import (clearChildren, getCellValues, getClipID, getDeckID,
                      intIfSet, layoutComps)


class DeckCtrl(LoadableExt):
	@property
	def selectedDeckState(self):
		# TODO: make this dynamic
		return self.decks[0]['state']

	def __init__(self, ownerComponent, logger, render, clipCtrl, layerCtrl):  # pylint: disable=too-many-arguments
		super().__init__(ownerComponent, logger)
		self.render = render
		self.clipCtrl = clipCtrl
		self.layerCtrl = layerCtrl
		self.deckTemplate = ownerComponent.op('./deckTemplate')
		self.deckList = ownerComponent.op('./table_deckIDs')
		self.deckState = ownerComponent.op('./null_deckState')
		self.composition = ownerComponent.op('../composition')
		assert self.composition, 'could not find composition component'

	def Init(self):
		self.setUnloaded()

		self.deckContainer = self.composition.op('decks')
		if self.deckContainer:
			self.logDebug('clearing decks in composition')
			clearChildren(self.deckContainer)
		else:
			self.logInfo('decks op not found in composition, initalizing')
			self.deckContainer = self.composition.create(baseCOMP, 'decks')

		self.decks = []
		self.deckList.clear()

		self.logInfo('initialized')

	def Load(self, saveState=None):
		self.setLoading()
		self.logInfo('loading composition')

		state = saveState or self.createDefaultState()
		for deck in state[1:]:
			(deckID, deckName, deckState) = deck
			self.createDeck(deckID, deckName, deckState)

		self.logInfo('loaded {} decks in composition'.format(len(self.decks)))
		self.setLoaded()

	def GetSaveState(self):
		if not self.Loaded:
			return None

		saveState = [getCellValues(deck) for deck in self.deckState.rows()]
		saveState[0].append('state')
		for deck in saveState[1:]:
			deckId = int(deck[0])
			deck.append(
				[getCellValues(layer) for layer in self.decks[deckId]['state'].rows()]
			)

		return saveState

	def createDeckState(self, deckID, deckName):
		return [
			deckID, deckName,
			[
				[None] * self.composition.par.Deckcolumncount.eval()
				for _ in range(self.composition.par.Layercount.eval())
			]
		]

	def createDefaultState(self):
		return [['Id', 'Deckname', 'State']] + [
			self.createDeckState(i, n)
			for i, n in enumerate(['Deck One', 'Deck Two', 'Deck Three'])
		]

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

		if clipID is not None:
			self.SelectClip(clipID)

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

	def SelectDeck(self, address):
		self.composition.par.Selecteddeck = getDeckID(address)

	def SelectClip(self, address: T.Union[str, int]):
		clipID = getClipID(address) if isinstance(address, str) else address
		self.clipCtrl.ActivateClip(clipID, fromSelect=True)
		self.composition.par.Previstarget = f'composition/clips/clip{clipID}/video/null_previs'
		self.composition.par.Selectedclip = clipID

	def getClipID(self, clipLocation):
		(layerNumber, clipNumber) = clipLocation
		return intIfSet(self.selectedDeckState[layerNumber, clipNumber])

	def setClipID(self, clipLocation, clipID):
		(layerNumber, clipNumber) = clipLocation
		cellValue = clipID if clipID is not None else ''
		self.selectedDeckState[layerNumber, clipNumber] = cellValue

	def createDeck(self, deckID, deckName, deckState):
		opName = 'deck{}'.format(deckID)
		self.logDebug('creating deck: {}'.format(opName))

		newDeck = self.deckContainer.copy(self.deckTemplate, name=opName)
		# TODO: be smarter about this, direct map?
		newDeck.par.Deckname = deckName

		newDeckState = newDeck.op('table_deckState')
		for r, row in enumerate(deckState):
			for c, clipId in enumerate(row):
				newDeckState[r, c] = clipId or ''

		self.decks.append({'op': newDeck, 'state': newDeckState})
		self.deckList.appendRow([deckID])

		self.layoutDeckContainer()

		return newDeck

	def layoutDeckContainer(self):
		layoutComps([d['op'] for d in self.decks], columns=3)
