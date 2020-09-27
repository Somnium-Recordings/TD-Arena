"""
TODO: this would probably be much simpler with an FSM...
Or at least some sort of Ctrl base class
"""
import json
from collections import OrderedDict

from tda import LoadableExt
from tdaUtils import (addressToValueLocation, clearChildren, getLayerId,
                      layoutComps, mapAddressToClipLocation)


class CompositionCtrl(LoadableExt):
	@property
	def compositionName(self):
		return self.render.par.Compositionname

	@property
	def saveFilePath(self):
		return tdu.expandPath('composition://{}.json'.format(self.compositionName))

	# TODO: This is gross. Decompose this into smaller classes.
	def __init__(
		self, ownerComponent, logger, dispatcher, render, clipCtrl, deckCtrl,
		layerCtrl, thumbnails
	):  # pylint: disable=too-many-arguments
		super().__init__(ownerComponent, logger)
		self.dispatcher = dispatcher
		self.render = render
		self.clipCtrl = clipCtrl
		self.deckCtrl = deckCtrl
		self.layerCtrl = layerCtrl
		self.thumbnails = thumbnails
		self.ctrls = OrderedDict(
			{
				'clips': self.clipCtrl,
				'decks': self.deckCtrl,
				'layers': self.layerCtrl
			}
		)
		self.selectPrevis = ownerComponent.op('../select_previs')
		# self.nullControls = ownerComponent.op('../null_controls')
		self.compositionContainer = ownerComponent.op('../composition')

		self.logInfo('clearing composition container')
		self.Init()

		# self.nullControls.export = 0
		# self.Reload()

	def Init(self):
		self.setUnloaded()
		self.clearCompositionContents()
		self.initControllers()
		self.bindOSCHandlers()
		self.layoutCompositionContainer()

		# TODO: manage previs selection
		# self.nullControls.export = 0
		self.logInfo('initialized')

	def New(self):
		# Call loadControllers with `None` save state?
		self.logInfo('TODO: New')
		# self.Reload(createNew=True)

	def Load(self):
		self.Init()
		self.setLoading()
		self.logInfo('loading composition')

		# TODO: handle case wherestate file doesn't exist
		saveState = self.readSaveFile()
		self.loadControllers(saveState)
		self.setLoaded()

		# TODO: why don't we treat thumbnails as a ctrl?
		self.thumbnails.Sync()

		# self.nullControls.export = 1
		self.logInfo('loaded')

	# TODO: saveAs
	def Save(self):
		if not self.Loaded:
			self.logWarning('composition not loaded, cannot save')
			return

		saveState = {}
		for ctrlName, ctrl in self.ctrls.items():
			saveState[ctrlName] = ctrl.GetSaveState()
		self.writeSaveFile(saveState)

	def OnCompNameChange(self):
		# TODO: noop if not different?
		# setPath = self.compositionContainer.par.externaltox
		# newPath = self.compositionToxPath
		# self.logInfo('composition changed from {} to {}'.format(setPath, newPath))
		self.logInfo(
			'TODO: is there anything we need to do here other than call Load?'
		)

	def bindOSCHandlers(self):
		self.dispatcher.Init()
		self.dispatcher.MapMultiple(
			{
				'?': {
					'handler': self.returnCurrentValueAtAddress
				},
				'/composition/load': {
					'handler': self.Load,
					'sendAddress': False
				},
				'/composition/reinit': {
					'handler': self.Init,
					'sendAddress': False
				},
				'/composition/new': {
					'handler': self.New,
					'sendAddress': False
				},
				'/composition/save': {
					'handler': self.Save,
					'sendAddress': False
				},
				'/composition/layers/*/select': {
					'handler': self.SelectLayer
				},
				'/composition/layers/*/clips/*/connect': {
					'handler': self.deckCtrl.ConnectClip,
					'mapAddress': mapAddressToClipLocation
				},
				'/composition/layers/*/clips/*/clear': {
					'handler': self.deckCtrl.ClearClip,
					'mapAddress': mapAddressToClipLocation
				},
				'/composition/layers/*/clips/*/source/load': {
					'handler': self.deckCtrl.LoadClip,
					'mapAddress': mapAddressToClipLocation
				},
			}
		)
		self.logInfo('osc handlers bound')

	def initControllers(self):
		self.logInfo('reinitilizing controllers')
		for ctrl in self.ctrls.values():
			ctrl.Init()

	def loadControllers(self, saveState):
		self.logInfo('loading controllers')
		for ctrlName, ctrl in self.ctrls.items():
			ctrl.Load(saveState[ctrlName])

	def clearCompositionContents(self):
		self.logInfo('clearing composition container')
		clearChildren(self.compositionContainer)

	def SelectLayer(self, address):
		"""
		TODO: move this into layerCtrl?
		"""
		layerId = getLayerId(address)
		self.selectPrevis.par.top = 'composition/layers/layer{}/null_previs'.format(
			layerId
		)

	def layoutCompositionContainer(self):
		layoutComps(self.compositionContainer.findChildren(depth=1))

	def AddressToOpPath(self, address):  # pylint: disable=no-self-use
		layerId = getLayerId(address)

		return 'composition/layers/layer{}'.format(layerId)

	def returnCurrentValueAtAddress(self, address, _):
		(controlPath, parName) = addressToValueLocation(
			address,
			self.compositionContainer.path
		) # yapf: disable

		controlOp = op(controlPath)
		if controlOp is None:
			self.logWarning(
				'could not lookup current value for non-existent op {}'.
				format(controlPath)
			)
			return

		par = getattr(controlOp.par, parName, None)
		if par is None:
			self.logWarning(
				'requested par {} does not exist on {}'.format(parName, controlPath)
			)
			return

		self.logDebug('replying with current value at {}'.format(address))
		self.dispatcher.OSCReply(address, par.eval())

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
