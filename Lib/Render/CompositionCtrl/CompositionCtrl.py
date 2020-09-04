"""
TODO: this would probably be much simpler with an FSM...
Or at least some sort of Ctrl base class
"""

from tda import LoadableExt
from tdaUtils import (clearChildren, getLayerId, layoutComps,
                      mapAddressToClipLocation)


class CompositionCtrl(LoadableExt):
	@property
	def compositionName(self):
		return self.render.par.Compositionname

	# TODO: This is gross. Decompose this into smaller classes.
	def __init__(
		self, ownerComponent, logger, dispatcher, render, clipCtrl, deckCtrl,
		layerCtrl, thumbnails, renderState
	):  # pylint: disable=too-many-arguments
		super().__init__(ownerComponent, logger)
		self.dispatcher = dispatcher
		self.render = render
		self.clipCtrl = clipCtrl
		self.deckCtrl = deckCtrl
		self.layerCtrl = layerCtrl
		self.thumbnails = thumbnails
		self.renderState = renderState
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
		self.logInfo('TODO: New')
		# self.Reload(createNew=True)

	def Reload(self, createNew=False):
		self.logInfo('TODO: Reload? Do we still need this {}'.format(createNew))
		# self.setLoading()

		# self.reinitControllers()
		# self.clearCompositionContents()

		# # TODO: if not createNew and not os.path.isfile(self.compositionFilePath):
		# # what do?

		# if createNew:
		# 	# TODO: load state from file?
		# 	self.logInfo('creating new composition')
		# else:
		# 	# TODO: re-initialize state?
		# 	self.logInfo('reloading composition')

		# self.Load()
		# self.layoutCompositionContainer()

	def Load(self):
		self.Init()
		self.setLoading()
		self.logInfo('loading composition')

		# TODO: what happens if state file doesn't exist?
		self.renderState.Load(self.compositionName)
		self.loadControllers()
		self.setLoaded()

		# TODO: why don't we treat thumbnails as a ctrl?
		self.thumbnails.Sync()

		# self.nullControls.export = 1
		self.logInfo('loaded')

	def bindOSCHandlers(self):
		self.dispatcher.Init()
		self.dispatcher.MapMultiple(
			{
				'/composition/reload': {
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

	# TODO: saveAs
	def Save(self):
		if not self.Loaded:
			self.logWarning('composition not loaded, cannot save')
			return

		self.renderState.Save(self.compositionName)

	def OnCompNameChange(self):
		# TODO: noop if not different?
		# setPath = self.compositionContainer.par.externaltox
		# newPath = self.compositionToxPath
		# self.logInfo('composition changed from {} to {}'.format(setPath, newPath))
		self.logInfo(
			'TODO: is there anything we need to do here other than call Reload?'
		)
		self.Reload()

	def initControllers(self):
		self.logInfo('reinitilizing controllers')
		self.clipCtrl.Init()
		self.deckCtrl.Init()
		self.layerCtrl.Init()

	def loadControllers(self):
		self.logInfo('loading controllers')
		self.clipCtrl.Load()
		self.deckCtrl.Load()
		self.layerCtrl.Load()

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
