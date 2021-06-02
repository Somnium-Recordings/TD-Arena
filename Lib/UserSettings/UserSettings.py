import json
from os import path

from tda import LoadableExt

SETTINGS_FILE = path.join('.td-arena', 'settings.json')


class UserSettings(LoadableExt):
	@property
	def settingsFilePath(self):
		return tdu.expandPath(SETTINGS_FILE)

	# pylint: disable=too-many-arguments
	def __init__(self, ownerComponent, logger):
		super().__init__(ownerComponent, logger)

		self.loadSettingsFile()

		self.setLoaded()
		self.logInfo('Settings initialized')

	def loadSettingsFile(self):
		self.logDebug('loading settings file')
		try:
			with open(self.settingsFilePath) as saveFile:
				settings = json.load(saveFile)
		except (json.JSONDecodeError, FileNotFoundError):
			self.logDebug(f'no settings file found at {self.settingsFilePath}')
			settings = {}

		self.Sync(settings)

	def Sync(self, applyUserSettings=None):
		self.logDebug(
			f'{"syncing" if applyUserSettings is None else "applying user"} settings'
		)
		userSettings = {}

		# Note: If we get to the point where we have a ton of settings, we can
		#       break this function up into an "update" and "load" so we don't
		#       have to process everything on every change, but for now it's not
		#       a big deal.
		for par in self.ownerComponent.customPars:
			if par.style == 'Header':
				continue

			if applyUserSettings is not None:
				if par.name in applyUserSettings:
					par.val = applyUserSettings[par.name]
				else:
					# reset to default to avoid any non-default config
					# carrying over from different systems where td-arena is
					# developed on
					par.val = par.default

			if not par.isDefault:
				userSettings[par.name] = par.eval()

		if applyUserSettings is None:
			with open(self.settingsFilePath, 'w') as saveFile:
				json.dump(userSettings, saveFile, indent='\t')
