from os import path
from typing import Callable

from tda import LoadableExt
from tdaUtils import addressToToxPath

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
	'Localoscctrlinport': {
		'target': 'local',
		'par': 'Oscctrlinport'
	},
	'Engineoscinport': {
		'target': 'engine',
		'par': 'Oscinport'
	},
	'Engineoscctrlinport': {
		'target': 'engine',
		'par': 'Oscctrlinport'
	},
}

DEFAULT_COMPOSITIONS_DIR = 'Compositions'
COMPOSITION_EXTENSION = 'tdac'


def isValidSaveFile(saveFile: str):
	return saveFile.endswith(COMPOSITION_EXTENSION) and path.isfile(saveFile)


STATE_UNLOADED = 'unloaded'
STATE_LOADING = 'loading'
STATE_LOADED = 'loaded'


# TODO: rename this class. "TD..." prefix should be reserved for system things
# @see https://forum.derivative.ca/t/simple-error-logging/8894/5?u=llwt
class TdArena(LoadableExt):
	@property
	def useEngine(self) -> bool:
		return self.userSettings.par.Useengine.eval()

	@useEngine.setter
	def useEngine(self, newVal: bool):
		self.userSettings.par.Useengine.val = newVal

	# pylint: disable=too-many-arguments
	def __init__(
		self, ownerComponent, logger, uiState, userSettings, renderLocal,
		renderEngine, uiGrid
	):
		super().__init__(ownerComponent, logger)
		self.uiState = uiState
		self.uiState.MapOSCHandlers(
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

		self.userSettings = userSettings
		self.renderLocal = renderLocal
		self.renderEngine = renderEngine
		self.uiGrid = uiGrid

		self.CompositionState: str
		TDF = op.TDModules.mod.TDFunctions
		TDF.createProperty(self, 'CompositionState', value=STATE_UNLOADED)

		self.onRenderLoaded: Callable = None

		self.logInfo('TdArena initialized')
		self.StartRenderer()

	def StartRenderer(self, useEngine=None):
		self.setLoading()
		self.CompositionState = STATE_UNLOADED

		if not self.userSettings.Loaded:
			raise RuntimeError(
				'TDArena initialized before user settings, ' +
				'add logic to delay system init until user settings loaded'
			)

		self.uiGrid.Init()
		self.bindUserSettings()

		if useEngine is None:
			useEngine = self.useEngine
		else:
			self.useEngine = useEngine

		if useEngine:
			self.logInfo('starting engine renderer')
			self.renderLocal.allowCooking = False
			self.renderEngine.par.initialize.pulse()
		else:
			self.logInfo('starting local renderer')
			self.renderLocal.allowCooking = True
			self.renderLocal.par.Reinitctrls.pulse()
			self.renderEngine.par.unload.pulse()

	def NewComposition(self):
		self.CompositionState = STATE_LOADING
		self.logInfo('creating new composition')
		self.userSettings.par.Composition = ''

		self.uiState.SendMessage('/composition/new')

	# TODO: what happens when we fail to load a composition?
	# TODO: How do we get the failure message/state back?
	# 		since we're only keying off of layer state length
	# 		right now which won't change on failure
	def OpenComposition(self, promptIfConfigured=True):
		saveFile = self.getSaveFile(promptIfConfigured, load=True)
		if not saveFile:
			self.logInfo('no save file selected, aborting open')
			return

		self.CompositionState = STATE_LOADING

		self.logInfo(f'opening composition: {saveFile}')
		self.uiState.SendMessage('/composition/load', saveFile)

	def SaveComposition(self, saveAs=False):
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
			self.renderEngine.par.unload.pulse()
			self.renderLocal.allowCooking = True

		self.renderLocal.par.Reinitctrls.pulse()
		self.clearBoundUserSettings()

		self.uiGrid.Unload()

		self.setUnloaded()
		self.CompositionState = STATE_UNLOADED

	def EditTox(self, address):
		# TODO(#7): reuse previous panel if still open
		# TODO(#7): show indicator in UI that thing is being edited
		# TODO(#7): show indicator in UI when edited by not saved
		toxPath = addressToToxPath(address, op.composition.path)
		self.logDebug(f'editing tox at {toxPath}')
		p = ui.panes.createFloating(type=PaneType.NETWORKEDITOR, name='Edit Tox')
		p.owner = op(toxPath)

	def SaveTox(self, address):
		# TODO(#7): save / increment to Backup folder
		toxPath = addressToToxPath(address, op.composition.path)
		self.logDebug(f'saving tox at {toxPath}')
		tox = op(toxPath)

		savePath = tox.par.externaltox.eval()
		assert savePath, 'cannot save tox without externaltox property set'
		tox.save(tdu.expandPath(savePath))

		self.logDebug(f'saved tox to {savePath}')

	def getSaveFile(self, promptIfConfigured: bool, load: bool):
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

	def onRenderInitialized(self, address):
		self.uiState.SendMessage(f'/ack{address}')
		self.CompositionState = STATE_UNLOADED

		if self.onRenderLoaded is not None:
			# pylint: disable=not-callable
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
		self.logDebug('binding user settings')

		for (parName, bindConfig) in BOUND_USER_SETTINGS.items():
			for targetPar in self.getUpdateTargets(parName, bindConfig):
				self.logDebug(
					f'binding {parName} setting to {targetPar.owner.name}.par.{targetPar.name}'
				)
				targetPar.bindExpr = f'op.userSettings.par.{parName}'

	def getUpdateTargets(self, parName, bindConfig):
		if 'par' not in bindConfig:  # default target par to config name
			bindConfig['par'] = parName

		targets = []
		if bindConfig['target'] == 'both':
			targets.append(self.renderLocal)
			targets.append(self.renderEngine)
		elif bindConfig['target'] == 'engine':
			targets.append(self.renderEngine)
		elif bindConfig['target'] == 'local':
			targets.append(self.renderLocal)
		else:
			raise AssertionError(
				'unexpected mapType of {}'.format(bindConfig['target'])
			)

		targets = [self.getTargetPar(target, bindConfig) for target in targets]
		return filter(lambda x: x is not None, targets)

	def getTargetPar(self, targetOp, mapConfig):
		target = getattr(targetOp.par, mapConfig['par'], None)
		if target is None:
			self.logError(
				'mapping expected {} to have paremeter {}, parameter will not be bound'.
				format(targetOp.name, mapConfig['par'])
			)

		return target
