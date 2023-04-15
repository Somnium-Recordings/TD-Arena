"""
TODO: this would probably be much simpler with an FSM...
Or at least some sort of Ctrl base class
"""
import json
from collections import OrderedDict

from oscDispatcher import OSCDispatcher
from tda import LoadableExt
from tdaUtils import (
	getLayerID,
	mapAddressToDeckLocation,
	mapAddressToEffectContainer,
	mapAddressToEffectLocation,
)


class StateCtrl(LoadableExt):

	def __init__(
		self,
		ownerComponent,  # noqa: ANN001
		logger,  # noqa: ANN001
		compositionCtrl,  # noqa: ANN001
		clipCtrl,  # noqa: ANN001
		deckCtrl,  # noqa: ANN001
		layerCtrl,  # noqa: ANN001
		effectCtrl,  # noqa: ANN001
		parameterCtrl  # noqa: ANN001
	):  # pylint: disable=too-many-arguments
		super().__init__(ownerComponent, logger)

		self.oscOut = ownerComponent.op('./oscout1')
		self.ctrls = OrderedDict(
			{
				# I think effects and parameters need to be initialized _before_ clips/layers/decks
				# This is due to the lazy init of those controllers expecting saveState to
				# be loaded for parameters/effects
				# TODO(#45): Verify this assumption is correct and doesn't cause issues
				'parameters': parameterCtrl,
				'effects': effectCtrl,
				'composition': compositionCtrl,
				'clips': clipCtrl,
				'decks': deckCtrl,
				'layers': layerCtrl
			}
		)
		self.dispatcher = OSCDispatcher(
			ownerComponent,
			logger,
			mappings=OrderedDict(
				{
					'?': {
						'handler': parameterCtrl.ReplyWithCurrentValue
					},
					'/ack/render/initialized': {
						'handler': self.acknowledgeInitialization,
						'sendAddress': False
					},
					'/composition/load': {
						'handler': self.load,
						'sendAddress': False
					},
					'/composition/reinit': {
						'handler': self.init,
						'sendAddress': False
					},
					'/composition/new': {
						'handler': self.new,
						'sendAddress': False
					},
					'/composition/save': {
						'handler': self.save,
						'sendAddress': False
					},
					'/composition/*:*': {
						'handler': parameterCtrl.SetParameter
					},
					'/composition/clips/*/select': {
						'handler': deckCtrl.SelectClip
					},
					'/composition/clips/*/video/effects/add': {
						'handler': effectCtrl.AddEffect,
						'mapAddress': mapAddressToEffectContainer
					},
					'/composition/clips/*/video/effects/*/clear': {
						'handler': effectCtrl.ClearEffect,
						'mapAddress': mapAddressToEffectLocation
					},
					'/composition/clips/*/video/effects/*/move': {
						'handler': effectCtrl.MoveEffect,
						'mapAddress': mapAddressToEffectLocation
					},
					'/composition/layers/*/video/effects/add': {
						'handler': effectCtrl.AddEffect,
						'mapAddress': mapAddressToEffectContainer
					},
					'/composition/layers/*/video/effects/*/clear': {
						'handler': effectCtrl.ClearEffect,
						'mapAddress': mapAddressToEffectLocation
					},
					'/composition/layers/*/video/effects/*/move': {
						'handler': effectCtrl.MoveEffect,
						'mapAddress': mapAddressToEffectLocation
					},
					'/composition/layers/*/clear': {
						'handler': layerCtrl.Clear,
						'mapAddress': getLayerID
					},
					'/composition/decks/*/select': {
						'handler': deckCtrl.SelectDeck
					},
					'/composition/layers/*/select': {
						'handler': layerCtrl.SelectLayer
					},
					'/selecteddeck/layers/*/clips/*/connect': {
						'handler': deckCtrl.ConnectClip,
						'mapAddress': mapAddressToDeckLocation
					},
					'/selecteddeck/layers/*/clips/*/clear': {
						'handler': deckCtrl.ClearClip,
						'mapAddress': mapAddressToDeckLocation
					},
					'/selecteddeck/layers/*/clips/*/move': {
						'handler': deckCtrl.MoveClip,
						'mapAddress': mapAddressToDeckLocation
					},
					'/selecteddeck/layers/*/clips/*/source/load': {
						'handler': deckCtrl.LoadClip,
						'mapAddress': mapAddressToDeckLocation
					},
					'/selecteddeck/layers/*/clips/*/video/effects/add': {
						'handler': deckCtrl.AddEffect,
						'mapAddress': mapAddressToDeckLocation
					},
					'/selecteddeck/layers/*/insert': {
						'handler': deckCtrl.InsertLayer,
						'mapAddress': getLayerID
					},
					'/selecteddeck/layers/*/remove': {
						'handler': deckCtrl.RemoveLayer,
						'mapAddress': getLayerID
					},
				}
			)
		)

		self.init()

	def Dispatch(self, *args):  # noqa: ANN002
		self.dispatcher.Dispatch(*args)

	def SendMessage(self, address, *args):  # noqa: ANN001, ANN002
		self.logDebug(f'Render -> UI -- {address}:{args}')
		self.oscOut.sendOSC(address, args)

	def init(self):
		self.setUnloaded()
		self.initControllers()
		self.logInfo('initialized')
		self.initializedAcknowledged = False
		self.replyWithInitialized()

	def acknowledgeInitialization(self):
		self.initializedAcknowledged = True

	def replyWithInitialized(self, attempts=0):  # noqa: ANN001
		"""
		We do this over OSC rather than through something like a dat to ensure
		the OSC messaging ports have had a chance to bind and attach
		"""
		if self.initializedAcknowledged:
			return

		if attempts > 20:
			self.logError(
				'timed out waiting for acknowledgement of initialization from ui'
			)
			return

		self.SendMessage('/render/initialized')
		run(
			f'args[0].replyWithInitialized(attempts={attempts + 1})',
			self,
			delayMilliSeconds=500
		)

	def new(self):
		self.init()
		self.setLoading()
		self.logInfo('creating new state')

		newState = {k: None for k in self.ctrls.keys()}
		self.loadControllers(newState)

		self.setLoaded()
		self.SendMessage('/composition/loaded')
		self.logInfo('new state loaded')

	# TODO: implement versioned save files
	def load(self, compositionFile: str):
		self.init()
		self.setLoading()
		self.logInfo('loading state')

		saveState = self.readSaveFile(compositionFile)
		self.loadControllers(saveState)

		self.setLoaded()
		self.SendMessage('/composition/loaded')
		self.logInfo('loaded')

	def save(self, compositionFile: str):
		if not self.Loaded:
			self.logWarning('state not loaded, cannot save')
			return

		saveState = {}
		self.logInfo('getting save state')
		for ctrlName, ctrl in self.ctrls.items():
			self.logDebug(f'getting save state for {ctrlName}')

			saveState[ctrlName] = ctrl.GetSaveState()
		self.writeSaveFile(saveState, compositionFile)

	def initControllers(self):
		self.logInfo('reinitilizing controllers')
		for ctrl in self.ctrls.values():
			ctrl.Init(self)

	def loadControllers(self, saveState):  # noqa: ANN001
		self.logInfo('loading controllers')
		for ctrlName, ctrl in self.ctrls.items():
			if ctrlName in saveState:
				ctrl.Load(saveState[ctrlName])

	def writeSaveFile(self, saveState, filePath: str):  # noqa: ANN001
		self.logInfo(f'saving state to {filePath}')

		with open(filePath, 'w', encoding='utf-8') as saveFile:
			json.dump(saveState, saveFile, indent='\t')

	def readSaveFile(self, filePath: str):
		self.logInfo(f'loading save file from {filePath}')

		with open(filePath, encoding='utf-8') as saveFile:
			return json.load(saveFile)
