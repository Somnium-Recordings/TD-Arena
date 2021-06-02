"""
TODO: this would probably be much simpler with an FSM...
Or at least some sort of Ctrl base class
"""
from tda import LoadableExt
from tdaUtils import clearChildren, getCellValues, layoutComps


class CompositionCtrl(LoadableExt):
	def __init__(self, ownerComponent, logger):
		super().__init__(ownerComponent, logger)
		self.compositionContainer = ownerComponent.op('../composition')
		self.compositionState = ownerComponent.op('./null_compositionState')

	def Init(self, _renderState):
		self.setUnloaded()
		self.clearCompositionContents()
		self.layoutCompositionContainer()

		self.setDefaultState()
		self.logInfo('initialized')

	def setDefaultState(self):
		for parameter in self.compositionContainer.customPars:
			parameter.val = parameter.default

	def Load(self, state=None):  # pylint: disable=unused-argument
		self.setLoading()
		self.logInfo('loading composition')

		if state is None:
			self.setDefaultState()
		else:
			for (config, value) in state:
				par = getattr(self.compositionContainer.par, config)
				if par is not None:
					par.val = value
					self.logDebug(f'setting coomposition {config} to {value}')
				else:
					self.logWarning(
						f'could not set composition config for unkown name {config}'
					)

		self.setLoaded()

		self.logInfo('loaded')

	def GetSaveState(self):
		return [
			getCellValues(config) for config in self.compositionState.rows()[1:]
		] if self.Loaded else None

	def clearCompositionContents(self):
		self.logInfo('clearing composition container')
		clearChildren(self.compositionContainer)

	def layoutCompositionContainer(self):
		# delay a frame so that other controlls can create their ops
		run(
			'args[0](args[1].findChildren(depth=1))',
			layoutComps,
			self.compositionContainer,
			delayFrames=1
		)
