import traceback
from itertools import filterfalse, tee
from typing import Iterable, NamedTuple, Tuple

COMPOSITION_LISTER_ROOT = '/composition'
EXTERNAL_TOX_COLOR = (0.05000000074505806, 0.3499999940395355, 0.5)
EXCLUDE_PATHS = [COMPOSITION_LISTER_ROOT, '/tdArena']
SETTINGS_PAGE_NAME = 'Save Settings'
SETTINGS_BEFORE_SAVE_SCRIPT = 'Savealltoxesonbeforesave'
SETTINGS_AFTER_SAVE_SCRIPT = 'Savealltoxesonaftersave'


class ToxInfo(NamedTuple):
	path: str
	networkPath: str
	dirty: bool


def partition(pred, iterable):
	'Use a predicate to partition entries into false entries and true entries'
	# partition(is_odd, range(10)) --> 0 2 4 6 8   and  1 3 5 7 9
	t1, t2 = tee(iterable)
	return filterfalse(pred, t1), filter(pred, t2)


def isCompositionListerPath(path: str) -> bool:
	return path.startswith(COMPOSITION_LISTER_ROOT)


def isCompositionTox(tox: ToxInfo) -> bool:
	return isCompositionListerPath(tox.path)


def hasDirty(toxes: Iterable[ToxInfo]):
	return any(o.dirty for o in toxes)


def confirmSystemSaveWithDirtyComposition():
	return ui.messageBox(
		'Warning',
		''.join(
			[
				'There are unsaved Composition toxes.\n',
				'Saving system toxes will result in a loss of unsaved changes.\n\n'
				'Continue anyway?'
			]
		),
		buttons=['Yes', 'No']
	) == 0


def confirmShouldUnload():
	return ui.messageBox(
		'Warning',
		''.join(
			[
				'The system must be unloaded before it can be saved.\n',
				'Any unsaved composition toxes, user layouts, etc. will be lost.\n\n'
				'Do you want to unload the system?'
			]
		),
		buttons=['Yes', 'No']
	) == 0


def hasCustomParameter(comp, name):
	return any(par.name == name for par in comp.customPars)


def ensureExternalToxSetup(comp):
	comp.color = EXTERNAL_TOX_COLOR

	saveSettingsPage = next(
		(p for p in comp.customPages if p.name == SETTINGS_PAGE_NAME), None
	)
	if saveSettingsPage is None:
		saveSettingsPage = comp.appendCustomPage(SETTINGS_PAGE_NAME)

	if not hasCustomParameter(comp, SETTINGS_BEFORE_SAVE_SCRIPT):
		saveSettingsPage.appendStr(
			SETTINGS_BEFORE_SAVE_SCRIPT, label='On Before Save Script'
		)

	if not hasCustomParameter(comp, SETTINGS_AFTER_SAVE_SCRIPT):
		saveSettingsPage.appendStr(
			SETTINGS_AFTER_SAVE_SCRIPT, label='On After Save Script'
		)


def executeParameterCallback(comp, paramName):
	callbackParameter = getattr(comp.par, paramName, None)
	if callbackParameter is None:
		debug(f'expected callback parameter {paramName} to exist on {comp.path}')
		return

	callbackScript = callbackParameter.eval()
	if callbackScript != '':
		run(callbackScript, fromOP=comp)


class ToxManager:

	@property
	def CompositionRoot(self) -> str:
		return self.ownerComp.par.Compositionroot.eval()

	def __init__(self, ownerComp, tda):
		self.ownerComp = ownerComp
		self.tda = tda
		self.window = ownerComp.op('window1')
		self.opFind = ownerComp.op('opfind_externalToxes')
		self.selectedToxesDat = ownerComp.op('null_selectedToxes')
		self.allToxesDat = ownerComp.op('null_allToxes')

	def Display(self, onlyIfDirty=False):
		if onlyIfDirty and not self.hasDirtyToxes():
			return

		self.opFind.par.cookpulse.pulse()
		self.window.par.winopen.pulse()

	def SaveSelectedToxes(self):
		# If in local mode and there are composition component changes
		# show composition components
		# If composition changes
		# save composition (with prompt)
		# if project changes
		# show project changes
		# on save, call Unload first
		# else
		# do nothing since there is nothing to save
		self.SaveSystemToxes(selected=True)

	def SaveSystemToxes(self, selected=True):
		if self.hasDirtyComposition(
		) and not confirmSystemSaveWithDirtyComposition():
			return

		if self.tda.Loaded:
			if confirmShouldUnload():
				self.tda.Unload()
			# NOTE: we return here because we can't ensure that everything is immediately
			#       reset to initial state before moving on, so we rely on the user to
			#       click save after things have settled
			return

		try:
			# TODO: increment files into backup folder
			for tox in self.getSystemToxes(selected):
				sysOp = op(tox.networkPath)
				ensureExternalToxSetup(sysOp)
				executeParameterCallback(sysOp, SETTINGS_BEFORE_SAVE_SCRIPT)
				sysOp.save(tdu.expandPath(sysOp.par.externaltox))
				executeParameterCallback(sysOp, SETTINGS_AFTER_SAVE_SCRIPT)

			self.Close()
		except Exception as _:  # pylint: disable=broad-except
			ui.messageBox(
				'!!!Warning!!!',
				'Encountered an unexpected error while attempting to save system toxes: \n\n'
				+ traceback.format_exc(),
			)

	def SaveCompositionToxes(self):
		pass

	def Close(self):
		self.window.par.winclose.pulse()

	def OpenNetworkAtPath(self, networkPath: str) -> None:
		p = ui.panes.createFloating(type=PaneType.NETWORKEDITOR, name='Edit Tox')
		p.owner = op(networkPath)

	def ToCompositionListerPath(self, networkPath) -> str:
		# /composition/effects/<name>/layer1-effect0
		# /effects/<effect-name>/layerN-[1..99]|clipN-[1..99]
		return networkPath.replace(self.CompositionRoot, COMPOSITION_LISTER_ROOT)

	def IsCompositionNetworkPath(self, networkPath: str):
		return networkPath.startswith(self.CompositionRoot + '/')

	def getToxes(
		self,
		selected=True
	) -> Tuple[Iterable[ToxInfo], Iterable[ToxInfo]]: # yapf: disable
		toxDat = self.selectedToxesDat if selected else self.allToxesDat

		paths = [
			ToxInfo( # yapf: disable
				toxDat[rowNumber, 'path'].val,
				toxDat[rowNumber, 'networkPath'].val,
				toxDat[rowNumber, 'dirty'].val == '1'
			)
			for rowNumber in range(1, toxDat.numRows)
			if toxDat[rowNumber, 'path'].val not in EXCLUDE_PATHS
		]

		return partition(isCompositionTox, paths)

	def getSystemToxes(self, selected=True):
		systemToxes, _ = self.getToxes(selected)
		return systemToxes

	def getCompositionToxes(self, selected=True):
		_, compositionToxes = self.getToxes(selected)
		return compositionToxes

	def hasDirtyComposition(self):
		return hasDirty(self.getCompositionToxes(selected=False))

	def hasDirtySystem(self):
		return hasDirty(self.getSystemToxes(selected=False))

	def hasDirtyToxes(self):
		systemToxes, compositionToxes = self.getToxes(selected=False)
		return hasDirty(systemToxes) or hasDirty(compositionToxes)

	# TODO
	# def CreateNewExternalizedComponent(self):
	#  - set color
	#  - set external parameter
	#  - save tox
	#  - with extension?
	# return
