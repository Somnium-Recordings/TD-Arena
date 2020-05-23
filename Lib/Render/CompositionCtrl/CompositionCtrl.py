import re

from tdaUtils import layoutComps


def getClipLocation(address):
	m = re.match(r'/composition/layers/(\d+)/clips/(\d+)/?.*', address)
	assert m, 'expected to match layer and clip number in {}'.format(address)

	return (int(m.group(1)), int(m.group(2)))


class CompositionCtrl:
	@property
	def Loading(self):
		return self.ownerComponent.par.Loading.val

	@Loading.setter
	def Loading(self, isLoading):
		self.ownerComponent.par.Loading = isLoading

	@property
	def Loaded(self):
		return self.ownerComponent.par.Loaded.val

	@Loaded.setter
	def Loaded(self, isLoading):
		self.ownerComponent.par.Loaded = isLoading

	def __init__(
		self, ownerComponent, logger, dispatcher, clipCtrl, deckCtrl, layerCtrl
	):  # pylint: disable=too-many-arguments
		self.ownerComponent = ownerComponent
		self.logger = logger
		self.dispatcher = dispatcher
		self.clipCtrl = clipCtrl
		self.deckCtrl = deckCtrl
		self.layerCtrl = layerCtrl

		self.Loading = False
		self.Loaded = False

		self.compositionContainer = ownerComponent.op('../composition')

		dispatcher.MapMultiple(
			{
				'/composition/reload': {
					'handler': self.Reload,
					'sendAddress': False
				},
				'/composition/reinit': {
					'handler': self.Reinit,
					'sendAddress': False
				},
				'/composition/new': {
					'handler': self.New,
					'sendAddress': False
				},
				'/composition/layers/*/clips/*/connect': {
					'handler': self.ConnectClip
				},
				'/composition/layers/*/clips/*/clear': {
					'handler': self.ClearClip
				},
				'/composition/layers/*/clips/*/source/load': {
					'handler': self.LoadClip
				},
			}
		)

		self.logInfo('initialized')

	def Reinit(self):
		"""
		This is mainly for debugging the initial state before things are loaded
		"""

		self.Loading = False
		self.Loaded = False
		self.reinitControllers()
		self.clearCompositionContents()
		self.logInfo('reinitalized')

	def New(self):
		self.Reload(createNew=True)

	def Reload(self, createNew=False):
		self.setLoading()
		if createNew:
			self.logInfo('creating new composition')
		else:
			self.logInfo('reloading composition')

		self.reinitControllers()
		self.clearCompositionContents()

		if not createNew:
			# composition.reinitnet.pulse
			# composition should ahv a callback that calls "Load"
			return

		# copy "init script" into composition
		self.Load()

	def Load(self):
		self.loadControllers()
		self.setLoadingComplete()
		self.layoutCompositionContainer()
		self.logInfo('loaded')

	def reinitControllers(self):
		self.clipCtrl.Reinit()
		self.deckCtrl.Reinit()
		self.layerCtrl.Reinit()

	def loadControllers(self):
		self.clipCtrl.Load()
		self.deckCtrl.Load()
		self.layerCtrl.Load()

	def clearCompositionContents(self):
		for op in self.compositionContainer.findChildren(depth=1):
			op.destroy()

	def LoadClip(self, clipAddress, sourceType, name, path):
		clipLocation = getClipLocation(clipAddress)
		clipID = self.deckCtrl.GetClipID(clipLocation)

		# TODO: return None from DeckCtrl to avoid runnig into this again
		if isinstance(clipID, int):  # clipID is "" when empty clip
			self.clipCtrl.ReplaceSource(sourceType, name, path, clipID)
		else:
			clip = self.clipCtrl.CreateClip(sourceType, name, path)
			self.deckCtrl.SetClip(clipLocation, clip.digits)

	def ClearClip(self, clipAddress):
		clipLocation = getClipLocation(clipAddress)
		clipID = self.deckCtrl.ClearClip(clipLocation)

		if isinstance(clipID, int):  # clipID is "" if an empty clip
			self.clipCtrl.DeleteClip(clipID)
			self.layerCtrl.ClearClipID(clipID)

	def ConnectClip(self, clipAddress):
		clipLocation = getClipLocation(clipAddress)
		clipID = self.deckCtrl.GetClipID(clipLocation)
		previousClipID = self.layerCtrl.SetClip(clipLocation[0], clipID)

		if isinstance(clipID, int):  # clipID is "" when launching an empty clip
			self.clipCtrl.ActivateClip(clipID)

		if isinstance(previousClipID, int) and previousClipID != clipID:
			self.clipCtrl.DeactivateClip(previousClipID)

	def logInfo(self, *args):
		self.logger.Info(self.ownerComponent, *args)

	def setLoading(self):
		self.Loaded = False
		self.Loading = True

	def setLoadingComplete(self, wasSuccessful=True):
		self.Loaded = wasSuccessful
		self.Loading = True

	def layoutCompositionContainer(self):
		layoutComps(self.compositionContainer.findChildren(depth=1))
