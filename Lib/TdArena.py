from os import path

from tda import LoadableExt
from tdaUtils import addressToToxPath

VALUE_MAP = {
	# Composition
	'Compositionname': {
		'target': 'both'
	},
	'Renderw': {
		'target': 'both'
	},
	'Renderh': {
		'target': 'both'
	},
	# Resolutions
	'Uiw': {
		'target': 'ui',
		'par': 'w'
	},
	'Uih': {
		'target': 'ui',
		'par': 'h'
	},
	'Debuguiw': {
		'target': 'none'
	},
	'Debuguih': {
		'target': 'none'
	},
	'Clipthumbw': {
		'target': 'both'
	},
	'Clipthumbh': {
		'target': 'both'
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
	# Paths
	'Compositionspath': {
		'target': 'both'
	},
	'Effectspath': {
		'target': 'both'
	},
	'Generatorspath': {
		'target': 'both'
	},
	'Moviespath': {
		'target': 'both'
	},
	'Libpath': {
		'target': 'both'
	},
}

pulseMap = {
	'Reloadengine': {
		'target': 'engine',
		'par': 'reload'
	},
}

DEFAULT_COMPOSITIONS_DIR = 'Compositions'
COMPOSITION_EXTENSION = 'tdac'


def isValidSaveFile(saveFile: str):
	return saveFile.endswith(COMPOSITION_EXTENSION) and path.isfile(saveFile)


# TODO: rename this class. "TD..." prefix should be reserved for system things
# @see https://forum.derivative.ca/t/simple-error-logging/8894/5?u=llwt
class TdArena(LoadableExt):
	@property
	def par(self):
		return self.ownerComponent.par

	# pylint: disable=too-many-arguments
	def __init__(
		self, ownerComponent, logger, uiState, userSettings, renderLocal,
		renderEngine, ui
	):
		super().__init__(ownerComponent, logger)
		self.uiState = uiState
		self.userSettings = userSettings

		self.localRender = renderLocal
		self.engineRender = renderEngine
		self.ui = ui

		self.Sync()
		self.logInfo('TdArena initialized')

		if self.ownerComponent.op('null_layerState').numRows > 1:
			self.setLoaded()

	def Sync(self):
		self.logDebug('syncing render parameters')
		self.SetLibPath()

		# ensure Useengined is synced since it's not in the map
		mappedPars = {'Useengine': {}, **VALUE_MAP}

		for parName in mappedPars:
			par = getattr(self.par, parName, None)
			if par is not None:
				# TODO: Could passing same value as prev cause issues?
				self.SyncValueChange(par, par.val)
			else:
				self.logWarning(
					'expected TdArena to have mapped parameter {}'.format(parName)
				)

	def ReinitComposition(self):
		op.uiState.SendMessage('/composition/reinit')
		# TODO: Remove once OnCompositionUnloaded logic is smarter
		# e.g. not counting layers)
		self.setUnloaded()

	def NewComposition(self):
		self.setLoading()
		self.userSettings.par.Composition = ''
		op.uiState.SendMessage('/composition/new')

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

	# TODO: what happens when we fail to load a composition?
	# TODO: How do we get the failure message/state back?
	# 		since we're only keying off of layer state length
	# 		right now which won't change on failure
	def OpenComposition(self, promptIfConfigured=True):
		saveFile = self.getSaveFile(promptIfConfigured, load=True)
		if not saveFile:
			self.logInfo('no save file selected, aborting open')
			return

		if not self.Loaded:
			self.setLoading()

		self.logInfo(f'opening composition: {saveFile}')
		self.uiState.SendMessage('/composition/load', saveFile)

	def SaveComposition(self, saveAs=False):
		saveFile = self.getSaveFile(promptIfConfigured=saveAs, load=True)
		if not saveFile:
			self.logInfo('no save file selected, aborting save')
			return

		self.logInfo(f'saving composition to {saveFile}')

		op.uiState.SendMessage('/composition/save', saveFile)

	def OnCompositionLoaded(self, wasSuccessful=True):
		self.setLoaded(wasSuccessful)

	def OnCompositionUnloaded(self):
		self.setUnloaded()

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

	def SetLibPath(self):
		# NOTE: os.path.join results in bothforward and backward slashes on Windows
		self.par.Libpath = '{}/{}'.format(project.folder, 'Lib')

	def SyncValueChange(self, par, _):
		newVal = par.eval()

		if par.name == 'Useengine':
			self.toggleEngine(newVal)
			return

		for targetPar in self.getUpdateTargets(par.name, VALUE_MAP):
			targetPar.val = newVal

	def SyncPulse(self, par):
		if par.name == 'Sync':
			self.Sync()
			return

		for targetPar in self.getUpdateTargets(par.name, pulseMap):
			targetPar.pulse()

	def getUpdateTargets(self, parName, parameterMap):
		assert parName in parameterMap, 'expected tda par "{}" to be mapped'.format(
			parName
		)
		mapConfig = parameterMap[parName]
		if 'par' not in mapConfig:
			mapConfig['par'] = parName

		targets = []
		if mapConfig['target'] == 'both':
			targets.append(self.localRender)
			targets.append(self.engineRender)
		elif mapConfig['target'] == 'engine':
			targets.append(self.engineRender)
		elif mapConfig['target'] == 'local':
			targets.append(self.localRender)
		elif mapConfig['target'] == 'ui':
			targets.append(self.ui)
		elif mapConfig['target'] == 'active':
			targets.append(
				self.engineRender if self.par.Useengine else self.localRender
			)
		elif mapConfig['target'] == 'none':
			pass
		else:
			raise AssertionError('unexpected mapType of {}'.format(mapConfig['target']))

		targets = [self.getTargetPar(target, mapConfig) for target in targets]
		return filter(lambda x: x is not None, targets)

	def getTargetPar(self, targetOp, mapConfig):
		target = getattr(targetOp.par, mapConfig['par'], None)
		if target is None:
			self.logWarning(
				'mapping expected {} to have paremeter {}, parameter will not be synced'.
				format(targetOp.name, mapConfig['par'])
			)

		return target

	def toggleEngine(self, useEngine):
		if useEngine:
			self.localRender.allowCooking = False
			self.engineRender.par.initialize.pulse()
		else:
			self.engineRender.par.unload.pulse()
			self.localRender.allowCooking = True
