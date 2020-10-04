"""
TODO: this would probably be much simpler with an FSM...
Or at least some sort of Ctrl base class
"""
from tda import LoadableExt
from tdaUtils import clearChildren, getDeckID, getLayerID, layoutComps


class CompositionCtrl(LoadableExt):
	def __init__(self, ownerComponent, logger):
		super().__init__(ownerComponent, logger)
		self.selectPrevis = ownerComponent.op('../select_previs')
		self.compositionContainer = ownerComponent.op('../composition')

		self.Init()

	def Init(self):
		self.setUnloaded()
		self.clearCompositionContents()
		self.layoutCompositionContainer()

		# TODO: Set defaults on compositionContainer

		self.logInfo('initialized')

	def Load(self, state=None):  # pylint: disable=unused-argument
		self.setLoading()
		self.logInfo('loading composition')

		# TODO: process state
		# TODO: set values from state on compositionContainer
		# TODO: set previs selection from state? (can we derive from prop comCtrl prop instead)

		self.setLoaded()

		self.logInfo('loaded')

	def GetSaveState(self):  # pylint: disable=no-self-use
		return {}

	def clearCompositionContents(self):
		self.logInfo('clearing composition container')
		clearChildren(self.compositionContainer)

	def SelectLayer(self, address):
		"""
		TODO: move this into layerCtrl?
		"""
		layerId = getLayerID(address)
		self.selectPrevis.par.top = 'composition/layers/layer{}/null_previs'.format(
			layerId
		)

	def SelectDeck(self, address):
		self.compositionContainer.par.Selecteddeck = getDeckID(address)

	def layoutCompositionContainer(self):
		# delay a frame so that other controlls can create their ops
		run(
			'args[0](args[1].findChildren(depth=1))',
			layoutComps,
			self.compositionContainer,
			delayFrames=1
		)
