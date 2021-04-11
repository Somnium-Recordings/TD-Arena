from tda import BaseExt
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


# TODO: rename this class. "TD..." prefix should be reserved for system things
# @see https://forum.derivative.ca/t/simple-error-logging/8894/5?u=llwt
class TdArena(BaseExt):
	@property
	def par(self):
		return self.ownerComponent.par

	def __init__(self, ownerComponent, logger):
		super().__init__(ownerComponent, logger)
		self.localRender = ownerComponent.op('./render')
		self.engineRender = ownerComponent.op('./engine_render')
		self.ui = ownerComponent.op('./ui')

		self.Sync()
		self.logInfo('TdArena initialized')

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

		# self.localRender.allowCooking = not useEngine
		# self.engineRender.par.power = useEngine
