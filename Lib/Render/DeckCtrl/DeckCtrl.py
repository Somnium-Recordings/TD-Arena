import typing as T

from tda import LoadableExt
from tdaUtils import (DeckLocation, clearChildren, getCellValues, getClipID,
                      getDeckID, intIfSet, layoutComps,
                      mapAddressToDeckLocation)

DECK_COLUMNS = 10

DEFAULT_STATE = [['Id', 'Deckname', 'State']] + [
	[deckID, deckName, [[None] * DECK_COLUMNS for _ in range(3)]]
	for deckID, deckName in enumerate(['Deck One', 'Deck Two', 'Deck Three'])
] # yapf: disable


def clipPrevisTarget(clipID: int) -> str:
	return f'composition/clips/clip{clipID}/video/null_previs'


class DeckCtrl(LoadableExt):
	@property
	def selectedDeckState(self):
		# TODO: make this dynamic
		return self.decks[int(self.composition.par.Selecteddeck)]['state']

	def __init__(
		self, ownerComponent, logger, render, clipCtrl, layerCtrl, effectCtrl
	):  # pylint: disable=too-many-arguments
		super().__init__(ownerComponent, logger)
		self.render = render
		self.clipCtrl = clipCtrl
		self.layerCtrl = layerCtrl
		self.effectCtrl = effectCtrl
		self.deckTemplate = ownerComponent.op('./deckTemplate')
		self.deckList = ownerComponent.op('./table_deckIDs')
		self.deckState = ownerComponent.op('./null_deckState')
		self.composition = ownerComponent.op('../composition')
		assert self.composition, 'could not find composition component'

	def Init(self, _renderState):
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

		state = saveState or DEFAULT_STATE
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

	def AddDeck(self):
		self.logInfo('TODO: add Deck')
		# TODO: show add button if DeckCtrl not initialized
		# TODO: find way to prompt for deck name
		assert False, 'update AddDeck to work with new state system (sans replicator)'
		# self.deckList.appendRow(['Deck {}'.format(self.deckList.numRows)])
		# self.layoutDeckContainer()
		# call layout after creating

	def ConnectClip(self, clipLocation: DeckLocation):
		(layerNumber, _) = clipLocation
		clipID = self.getClipID(clipLocation)

		self.logInfo(
			'connecting clip #{} at {} to layer {}'.format(
				clipID, clipLocation, layerNumber
			)
		)

		# NOTE: we offset by one because decks are 0 indexed and layer 0 is the composition
		self.layerCtrl.SetClip(layerNumber + 1, clipID)

		if clipID is not None:
			self.SelectClip(clipID)

	def LoadClip(self, clipLocation: DeckLocation, sourceType, name, path):
		clipID = self.getClipID(clipLocation)
		self.logInfo(f'loading {sourceType} "{name}" into {clipLocation}')

		if clipID is not None:
			self.clipCtrl.ReplaceSource(sourceType, name, path, clipID)
		else:
			clip = self.clipCtrl.CreateClip(sourceType, name, path)
			self.setClipID(clipLocation, clip.digits)

	def AddEffect(self, clipLocation: DeckLocation, effectPath):
		clipID = self.getClipID(clipLocation)
		self.logInfo(f'adding effect to {clipLocation}')

		if clipID is None:
			self.logWarning('cannot add effect to clip without source')
			return

		self.effectCtrl.AddEffect(
			f'/composition/clips/{clipID}/video/effects', effectPath
		)

	def ClearClip(self, clipLocation: DeckLocation, deckID: int = None):
		self.logInfo('clearing clip at {}'.format(clipLocation))
		clipID = self.getClipID(clipLocation, deckID)

		if clipID is not None:
			self.setClipID(clipLocation, None)
			self.layerCtrl.ClearClipID(clipID)
			if self.composition.par.Previstarget.eval() == clipPrevisTarget(clipID):
				self.composition.par.Previstarget = ''
			if self.composition.par.Selectedclip.eval() == clipID:
				self.composition.par.Selectedclip.val = self.composition.par.Selectedclip.default

	def MoveClip(self, clipLocation: DeckLocation, targetClip: str):
		targetLocation = mapAddressToDeckLocation(targetClip)
		self.logInfo(f'moving clip at {clipLocation} to {targetLocation}')

		targetClipID = self.getClipID(targetLocation)

		self.setClipID(targetLocation, self.getClipID(clipLocation))
		self.setClipID(clipLocation, targetClipID)

	def SelectDeck(self, address):
		self.composition.par.Selecteddeck = getDeckID(address)

	def SelectClip(self, address: T.Union[str, int]):
		clipID = getClipID(address) if isinstance(address, str) else address
		self.clipCtrl.ActivateClip(clipID, fromSelect=True)
		self.composition.par.Previstarget = clipPrevisTarget(clipID)
		self.composition.par.Selectedclip = clipID

	def InsertLayer(self, layerNumber: int, direction: str):
		newDeckLayer = [''] * DECK_COLUMNS
		targetIndex = layerNumber if direction == 'above' else layerNumber + 1

		for deck in self.decks:
			self.logInfo(
				f'inserting new layer into deck {deck["op"].digits} {direction} layer {layerNumber}'
			)
			deck['state'].insertRow(newDeckLayer, targetIndex)

		# NOTE: we offset by one because decks are 0 indexed and layer 0 is the composition
		self.layerCtrl.Insert(layerNumber + 1, direction)

	def RemoveLayer(self, layerNumber: int):
		for deckID, deck in enumerate(self.decks):
			self.logInfo(f'removing layer {layerNumber} from deck {deck["op"].digits}')
			for clipNumber in range(deck['state'].numCols):
				self.ClearClip((layerNumber, clipNumber), deckID)
			deck['state'].deleteRow(layerNumber)

		# NOTE: +1 because layer 0 is the composition
		self.layerCtrl.Remove(layerNumber + 1)

	def getClipID(self, clipLocation: DeckLocation, deckID: int = None):
		(layerNumber, clipNumber) = clipLocation
		if deckID is None:
			deckState = self.selectedDeckState
		else:
			deckState = self.decks[deckID]['state']

		return intIfSet(deckState[layerNumber, clipNumber])

	def setClipID(self, clipLocation: DeckLocation, clipID):
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
		numRows = len(deckState)
		numCols = len(deckState[0])
		newDeckState.setSize(numRows, numCols)

		for r, row in enumerate(deckState):
			for c, clipId in enumerate(row):
				newDeckState[r, c] = clipId or ''

		self.decks.append({'op': newDeck, 'state': newDeckState})
		self.deckList.appendRow([deckID])

		self.layoutDeckContainer()

		return newDeck

	def layoutDeckContainer(self):
		layoutComps([d['op'] for d in self.decks], columns=3)
