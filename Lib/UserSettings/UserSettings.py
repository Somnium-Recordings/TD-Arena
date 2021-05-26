import json
from os import path

from tda import LoadableExt

SETTINGS_FILE = path.join('.td-arena', 'settings.json')

# TODO: test if we can use a bind now rather than manually syncing
SETTINGS_MAP = {
	'Composition': {
		# TODO: target: none
		'target': 'both'
	}
}


class UserSettings(LoadableExt):
	@property
	def settingsFilePath(self):
		return tdu.expandPath(SETTINGS_FILE)

	# pylint: disable=too-many-arguments
	def __init__(self, ownerComponent, logger, renderLocal, renderEngine, ui):
		super().__init__(ownerComponent, logger)
		self.renderLocal = renderLocal
		self.renderEngine = renderEngine
		self.ui = ui

		settings = self.loadSettingsFile()
		self.Sync(settings)

		self.setLoaded()
		self.logInfo('Settings initialized')

	def loadSettingsFile(self):
		self.logDebug('loading settings file')
		try:
			with open(self.settingsFilePath) as saveFile:
				return json.load(saveFile)
		except (json.JSONDecodeError, FileNotFoundError):
			self.logDebug(f'no settings file found at {self.settingsFilePath}')
			return {}

	def Sync(self, applyUserSettings=None):
		self.logDebug(
			f'{"syncing" if applyUserSettings is None else "applying user"} settings'
		)
		userSettings = {}

		# Note: If we get to the point where we have a ton of settings, we can
		#       break this function up into an "update" and "load" so we don't
		#       have to process everything on every change, but for now it's not
		#       a big deal.
		for parName in SETTINGS_MAP:
			par = self.ownerComponent.par[parName]

			if applyUserSettings is not None:
				if parName in applyUserSettings:
					par.val = applyUserSettings[parName]
				else:
					# reset to default to avoid any non-default config
					# carrying over from different systems where td-arena is
					# developed on
					par.val = par.default

			if not par.isDefault:
				userSettings[parName] = par.eval()

			# TODO: test if we can use a bind now rather than manually
			#       syncing once engine is working again
			print(f'TODO: sync {parName} to comp')

		if applyUserSettings is None:
			with open(self.settingsFilePath, 'w') as saveFile:
				json.dump(userSettings, saveFile, indent='\t')

	def getTargetPar(self, targetOp, mapConfig):
		target = getattr(targetOp.par, mapConfig['par'], None)
		if target is None:
			self.logWarning(
				'mapping expected {} to have paremeter {}, parameter will not be synced'.
				format(targetOp.name, mapConfig['par'])
			)

		return target

	def getUpdateTargets(self, parName, parameterMap):
		assert parName in parameterMap, 'expected tda par "{}" to be mapped'.format(
			parName
		)
		mapConfig = parameterMap[parName]
		if 'par' not in mapConfig:
			mapConfig['par'] = parName

		targets = []
		if mapConfig['target'] == 'both':
			targets.append(self.renderLocal)
			targets.append(self.renderEngine)
		elif mapConfig['target'] == 'engine':
			targets.append(self.renderEngine)
		elif mapConfig['target'] == 'local':
			targets.append(self.renderLocal)
		elif mapConfig['target'] == 'ui':
			targets.append(self.ui)
		elif mapConfig['target'] == 'active':
			debug('TODO')
			# targets.append(
			# 	self.engineRender if self.par.Useengine else self.localRender
			# )
		elif mapConfig['target'] == 'none':
			pass
		else:
			raise AssertionError('unexpected mapType of {}'.format(mapConfig['target']))

		targets = [self.getTargetPar(target, mapConfig) for target in targets]
		return filter(lambda x: x is not None, targets)
