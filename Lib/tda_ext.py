from pathlib import Path
from typing import Callable, Optional, cast

from oscDispatcher import OSCMappings
from tda import LoadableExt
from ui_state import ui_state_ext

BOUND_USER_SETTINGS = {
	# Composition
	'Renderresw': {
		'target': 'both',
		'par': 'Renderw'
	},
	'Renderresh': {
		'target': 'both',
		'par': 'Renderh'
	},
	# Resolutions
	'Clipthumbnailresw': {
		'target': 'both',
		'par': 'Clipthumbw'
	},
	'Clipthumbnailresh': {
		'target': 'both',
		'par': 'Clipthumbh'
	},
	# Networking
	'Localoscinport': {
		'target': 'local',
		'par': 'Oscinport'
	},
	'Engineoscinport': {
		'target': 'engine',
		'par': 'Oscinport'
	},
}

RENDER_OUTPUT_MAP = [
	{
		'local': 'null_renderLocalErrors',
		'engine': 'merge_renderEngineErrors'
	},
	'null_renderState',
	'null_compositionState',
	'null_clipState',
	'null_deckState',
	'null_selectedDeckState',
	'null_layerState',
	'null_parameterState',
	None,  # 'null_finalOut',
	'null_finalPrevis',
	'null_finalThumbnails',
	'null_finalLayerThumbnails',
]

DEFAULT_COMPOSITIONS_DIR = 'Compositions'
COMPOSITION_EXTENSION = 'tdac'


def isValidSaveFile(saveFile: str):
	return saveFile.endswith(COMPOSITION_EXTENSION) and Path(saveFile).is_file()


STATE_UNLOADED = 'unloaded'
STATE_LOADING = 'loading'
STATE_LOADED = 'loaded'


# TODO: rename this class. "TD..." prefix should be reserved for system things
# @see https://forum.derivative.ca/t/simple-error-logging/8894/5?u=llwt
class TDAExt(LoadableExt):

	@property
	def useEngine(self) -> bool:
		return self.userSettings.par.Useengine.eval()

	@useEngine.setter
	def useEngine(self, newVal: bool):  # noqa: ANN202
		self.userSettings.par.Useengine.val = newVal

	def __init__(  # noqa: PLR0913
		self,
		ownerComponent,  # noqa: ANN001
		logger,  # noqa: ANN001
		userSettings,  # noqa: ANN001
		renderLocal,  # noqa: ANN001
		renderEngine,  # noqa: ANN001
		uiGrid,  # noqa: ANN001
	):
		super().__init__(ownerComponent, logger)
		self.uiState = cast(ui_state_ext.UIStateExt, op.ui_state.ext.UIStateExt)
		self.uiState.MapOSCHandlers(
			OSCMappings(
				{
					'/render/initialized': {
						'handler': self.onRenderInitialized
					},
					'/composition/loaded': {
						'handler': self.onCompositionLoaded,
						'sendAddress': False
					}
				}
			)
		)

		self.userSettings = userSettings
		self.renderLocal = renderLocal
		self.renderEngine = renderEngine
		self.uiGrid = uiGrid

		self.CompositionState: str
		TDF = op.TDModules.mod.TDFunctions
		TDF.createProperty(self, 'CompositionState', value=STATE_UNLOADED)

		self.onRenderLoaded: Optional[Callable] = None

		self.logInfo('initialized')
		self.StartRenderer()

	def StartRenderer(self, useEngine=None):  # noqa: ANN001
		self.setLoading()
		self.CompositionState = STATE_UNLOADED

		if not self.userSettings.Loaded:
			raise RuntimeError(
				'TDArena initialized before user settings, '
				'add logic to delay system init until user settings loaded'
			)

		self.uiGrid.Init()

		if useEngine is None:
			useEngine = self.useEngine
		else:
			self.useEngine = useEngine

		# will be reconnected in onEngineStart callback if we use engine
		# without this, the engine init pulse can trigger errors due to
		# not enough inputs to the nulls
		self.ConnectRenderOutputs(useEngine=False)

		if useEngine:
			self.logInfo('starting engine renderer')
			self.renderLocal.allowCooking = False
			self.renderEngine.par.initialize.pulse()
			# NOTE: we finish engine setup in OnEngineRendererStart
			#       to ensure render tox has had a chance to initialize
		else:
			self.logInfo('starting local renderer')
			self.renderLocal.allowCooking = True
			self.bindUserSettings()
			self.renderLocal.par.Reinitctrls.pulse()
			self.renderEngine.par.unload.pulse()

	def OnEngineRendererStart(self):
		self.logInfo('finishing engine renderer setup')
		self.bindUserSettings()
		self.ConnectRenderOutputs()
		self.renderEngine.par.Syncouts.pulse()

	def ConnectRenderOutputs(self, useEngine=None):  # noqa: ANN001
		if useEngine is None:
			useEngine = self.useEngine

		if useEngine:
			targetName = 'engine'
			renderOp = self.renderEngine
		else:
			targetName = 'local'
			renderOp = self.renderLocal

		for outputIndex, target in enumerate(RENDER_OUTPUT_MAP):
			targetOpName = target[targetName] if isinstance(target, dict) else target
			if targetOpName is None:  # Unmapped outputs
				continue

			targetOp = self.ownerComponent.op(targetOpName)

			if targetOp is None:
				self.logError(f'could not find render connection target {targetOpName}')
				continue

			renderOp.outputConnectors[outputIndex].connect(targetOp)

	def NewComposition(self):
		self.CompositionState = STATE_LOADING
		self.logInfo('creating new composition')
		self.userSettings.par.Composition = ''

		self.uiState.SendMessage('/composition/new')

	# TODO: what happens when we fail to load a composition?
	# TODO: How do we get the failure message/state back?
	# 		since we're only keying off of layer state length
	# 		right now which won't change on failure
	def OpenComposition(self, promptIfConfigured=True):  # noqa: ANN001, FBT002
		saveFile = self.getSaveFile(promptIfConfigured, load=True)
		if not saveFile:
			self.logInfo('no save file selected, aborting open')
			return

		self.CompositionState = STATE_LOADING

		self.logInfo(f'opening composition: {saveFile}')
		self.uiState.SendMessage('/composition/load', saveFile)

	def SaveComposition(self, saveAs=False):  # noqa: ANN001, FBT002
		saveFile = self.getSaveFile(promptIfConfigured=saveAs, load=True)
		if not saveFile:
			self.logInfo('no save file selected, aborting save')
			return

		self.logInfo(f'saving composition to {saveFile}')

		self.uiState.SendMessage('/composition/save', saveFile)

	def ReinitComposition(self):
		if self.useEngine:
			self.renderEngine.par.Reinitctrls.pulse()
		else:
			self.renderLocal.par.Reinitctrls.pulse()

	def ReloadEngine(self):
		# will be reconnected in onEngineStart callback
		self.ConnectRenderOutputs(useEngine=False)
		self.renderEngine.par.reload.pulse()

	def ToggleEngine(self):
		useEngine = self.useEngine

		if useEngine or self.CompositionState == STATE_UNLOADED:
			self.logInfo(f'toggling useEngine to {useEngine}')
			self.StartRenderer(not useEngine)
		else:
			self.logInfo('clearing local render before enabling engine')
			self.onRenderLoaded = lambda: self.StartRenderer(not useEngine)
			self.StartRenderer(useEngine)

	def Unload(self):
		if self.useEngine:
			# will be reconnected in onEngineStart callback
			self.ConnectRenderOutputs(useEngine=False)
			self.renderEngine.par.unload.pulse()
			self.renderLocal.allowCooking = True

		self.renderLocal.par.Reinitctrls.pulse()
		self.clearBoundUserSettings()

		self.uiGrid.Unload()

		self.setUnloaded()
		self.CompositionState = STATE_UNLOADED

	def getSaveFile(self, promptIfConfigured: bool, load: bool):  # noqa: FBT001
		saveFile = self.userSettings.par.Composition.eval()

		if saveFile and not isValidSaveFile(saveFile):
			self.logWarning(
				f'invalid composition file configured, ignoring value: "{saveFile}"'
			)
			saveFile = ''

		if not saveFile or promptIfConfigured:
			saveFile = ui.chooseFile(
				load=load,
				fileTypes=[COMPOSITION_EXTENSION],
				start=DEFAULT_COMPOSITIONS_DIR,
				title=f'{"Open" if load else "Save"} Composition'
			)
			self.userSettings.par.Composition = saveFile

		return saveFile

	# TODO: why is this not in the ui_state?
	def onRenderInitialized(self, address):  # noqa: ANN001
		self.uiState.SendMessage(f'/ack{address}')
		self.CompositionState = STATE_UNLOADED

		if self.onRenderLoaded is not None:
			self.onRenderLoaded()
			self.onRenderLoaded = None
		elif self.Loading:
			self.setLoaded()

	def onCompositionLoaded(self):
		self.CompositionState = STATE_LOADED

	########################################################################
	# Code below is to deal with the fact that a bound param attached to
	# a saved tox will cause issues when that tox is loaded into an engine
	# Issue #1 in https://forum.derivative.ca/t/problems-with-engine-and-parameter-binding/132927
	########################################################################

	def clearBoundUserSettings(self):
		"""
		Saving the render comp with bound parameters causes conflicts
		when the same parameter is bound on the tox loaded into an engine
		Clearing these before saving and re-applying at runtime seems
		to fix the issue
		"""
		self.logDebug('unbinding user settings')
		for comp in [self.renderEngine, self.renderLocal]:
			for par in comp.customPars:
				par.bindExpr = ''

	def bindUserSettings(self):
		if self.useEngine:
			targetName = 'engine'
			targetOp = self.renderEngine
		else:
			targetName = 'local'
			targetOp = self.renderLocal

		self.logDebug(f'binding user settings to {targetName}Engine')

		applicableBindings = [
			(parName, self.getTargetPar(targetOp, bindConfig))
			for (parName, bindConfig) in BOUND_USER_SETTINGS.items()
			if bindConfig['target'] in ['both', targetName]
		]

		for (parName, targetPar) in applicableBindings:
			if targetPar is not None:
				self.logDebug(
					f'binding {parName} setting to {targetPar.owner.name}.par.{targetPar.name}'
				)
				# targetPar.bindExpr = f'op.userSettings.par.{parName}'
				targetPar.val = op.userSettings.par[parName].eval()
			else:
				self.logError(
					f'could not bind {parName} setting to {targetName}, configured parameter not found'
				)

	def getTargetPar(self, targetOp, mapConfig):  # noqa: ANN001
		target = getattr(targetOp.par, mapConfig['par'], None)
		if target is None:
			self.logError(
				f'mapping expected {targetOp.name} to have parameter {mapConfig["par"]}, parameter will not be bound'
			)

		return target
