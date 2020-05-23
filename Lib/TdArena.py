valueMap = {
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
	# State
	# TODO: move to osc/state out
	'Activedeck': {
		'target': 'both'
	},
	# Resolutions
	'Renderlocal': {
		'target': 'none'
	},
	'Uiw': {
		'target': 'ui',
		'par': 'w'
	},
	'Uih': {
		'target': 'ui',
		'par': 'h'
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
	'Localstateoutport': {
		'target': 'local',
		'par': 'Stateoutport'
	},
	'Localerrorsoutport': {
		'target': 'local',
		'par': 'Errorsoutport'
	},
	'Engineoscinport': {
		'target': 'engine',
		'par': 'Oscinport'
	},
	'Enginestateoutport': {
		'target': 'engine',
		'par': 'Stateoutport'
	},
	'Engineerrorsoutport': {
		'target': 'engine',
		'par': 'Errorsoutport'
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
	'Clearrendererrors': {
		'target': 'active',
		'par': 'Clearerrors'
	},
	'Reloadengine': {
		'target': 'engine',
		'par': 'reload'
	},
}


class TdArena:
	@property
	def par(self):
		return self.ownerComponent.par

	def __init__(self, ownerComponent, logger):
		self.ownerComponent = ownerComponent
		self.logger = logger
		self.localRender = ownerComponent.op('./render')
		self.engineRender = ownerComponent.op('./engine_render')
		self.ui = ownerComponent.op('./ui')

		self.Sync()
		self.logInfo('TdArena initialized')

	def Sync(self):
		self.SetLibPath()

		for parName in valueMap:
			par = getattr(self.par, parName, None)
			if par is not None:
				# TODO: Could passing same value as prev cause issues?
				self.SyncValueChange(par, par.val)
			else:
				self.logWarning(
					'expected TdArena to have mapped parameter {}'.format(parName)
				)

	def SetLibPath(self):
		# NOTE: os.path.join results in bothforward and backward slashes on Windows
		self.par.Libpath = '{}/{}'.format(project.folder, 'Lib')

	def SyncValueChange(self, par, _):
		newVal = par.eval()

		if par.name == 'Useengine':
			self.toggleEngine(newVal)
			return

		for targetPar in self.getUpdateTargets(par.name, valueMap):
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
		self.localRender.allowCooking = not useEngine
		self.engineRender.par.power = useEngine

	def logInfo(self, *args):
		self.logger.Info(self.ownerComponent, *args)

	def logWarning(self, *args):
		self.logger.Warning(self.ownerComponent, *args)
