"""
TODO: this would probably be much simpler with an FSM...
Or at least some sort of Ctrl base class
"""
import json
from collections import OrderedDict

from tda import LoadableExt


class StateCtrl(LoadableExt):
	@property
	def compositionName(self):
		return self.render.par.Compositionname

	# TODO: take save filename as OSC parameter
	# Q: during dev, do we get that name during reload?
	# Save on composition container?
	@property
	def saveFilePath(self):
		return tdu.expandPath('composition://{}.json'.format(self.compositionName))

	def __init__(
		self, ownerComponent, logger, render, compositionCtrl, clipCtrl, deckCtrl,
		layerCtrl, effectCtrl, parameterCtrl
	):  # pylint: disable=too-many-arguments
		super().__init__(ownerComponent, logger)
		self.render = render
		self.ctrls = OrderedDict(
			{
				# I think effects and parameters need to be initialized _before_ clips/layers/decks
				# This is due to the lazy init of those controllers expecting saveState to
				# be loaded for parameters/effects
				# TODO: Verify this assumption is correct and doesn't cause issues
				'parameters': parameterCtrl,
				'effects': effectCtrl,
				'composition': compositionCtrl,
				'clips': clipCtrl,
				'decks': deckCtrl,
				'layers': layerCtrl
			}
		)

		self.Init()

	def Init(self):
		self.setUnloaded()
		self.initControllers()
		self.logInfo('initialized')

	def New(self):
		self.Init()
		self.setLoading()
		self.logInfo('creating new state')

		newState = {k: None for k in self.ctrls.keys()}
		self.loadControllers(newState)

		self.setLoaded()
		self.logInfo('new state loaded')

	# TODO: implement versioned save files
	def Load(self):
		self.Init()
		self.setLoading()
		self.logInfo('loading state')

		# TODO: handle case wherestate file doesn't exist
		saveState = self.readSaveFile()
		self.loadControllers(saveState)
		self.setLoaded()

		self.logInfo('loaded')

	# TODO: saveAs
	def Save(self):
		if not self.Loaded:
			self.logWarning('state not loaded, cannot save')
			return

		saveState = {}
		self.logInfo('getting save state')
		for ctrlName, ctrl in self.ctrls.items():
			self.logDebug(f'getting save state for {ctrlName}')

			saveState[ctrlName] = ctrl.GetSaveState()
		self.writeSaveFile(saveState)

	def initControllers(self):
		self.logInfo('reinitilizing controllers')
		for ctrl in self.ctrls.values():
			ctrl.Init()

	def loadControllers(self, saveState):
		self.logInfo('loading controllers')
		for ctrlName, ctrl in self.ctrls.items():
			if ctrlName in saveState:
				ctrl.Load(saveState[ctrlName])

	def writeSaveFile(self, saveState):
		filePath = self.saveFilePath
		self.logInfo('saving state to {}'.format(filePath))

		with open(filePath, 'w') as saveFile:
			json.dump(saveState, saveFile, indent='\t')

	def readSaveFile(self):
		filePath = self.saveFilePath
		self.logInfo('loading save file from {}'.format(filePath))

		with open(filePath) as saveFile:
			return json.load(saveFile)
