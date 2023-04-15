import shutil
import traceback
from collections.abc import Iterable
from glob import glob
from itertools import filterfalse, tee
from pathlib import Path, PureWindowsPath
from typing import NamedTuple, Optional, Union

from tda import TDFileInfo
from tdaUtils import addressToToxPath, resetCustomParameters

COMPOSITION_LISTER_ROOT = '/composition'
EXTERNAL_TOX_COLOR = (0.05000000074505806, 0.3499999940395355, 0.5)
EXCLUDE_PATHS = [COMPOSITION_LISTER_ROOT, '/tdArena']
SETTINGS_PAGE_NAME = 'Save Settings'
SETTINGS_BEFORE_SAVE_SCRIPT = 'Savealltoxesonbeforesave'
SETTINGS_AFTER_SAVE_SCRIPT = 'Savealltoxesonaftersave'


class ToxInfo(NamedTuple):
	path: str
	networkPath: str
	filePath: TDFileInfo
	dirty: bool


def partition(pred, iterable):  # noqa: ANN001
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


def hasCustomParameter(comp, name):  # noqa: ANN001
	return any(par.name == name for par in comp.customPars)


def ensureExternalToxSetup(comp):  # noqa: ANN001
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


def executeParameterCallback(comp, paramName):  # noqa: ANN001
	callbackParameter = getattr(comp.par, paramName, None)
	if callbackParameter is None:
		debug(f'expected callback parameter {paramName} to exist on {comp.path}')
		return

	callbackScript = callbackParameter.eval()
	if callbackScript != '':
		run(callbackScript, fromOP=comp)


def hasConflictingFilePath(
	toxes: Iterable[ToxInfo]
) -> Union[TDFileInfo, bool]:
	paths = set()

	for tox in toxes:
		if tox.filePath in paths:
			return tox.filePath
		paths.add(tox.filePath)

	return False


def displayConflictingPathError(conflictingPath: str):
	ui.messageBox(
		'Conflicting File Path Error',
		''.join(
			[
				'Multiple toxes are attempting to save to the same file path:\n\n',
				f'{conflictingPath}\n\n', 'Only one tox can save to a path at a time.'
			]
		),
	)


def findLastBackup(savePath: TDFileInfo):
	fileStem = PureWindowsPath(savePath).stem
	saveStem = f'{savePath.dir}\\{fileStem}.'

	lastBackupVersion = 0
	for backupFile in glob(f'{saveStem}*{savePath.ext}'):
		try:
			lastBackupVersion = max(
				lastBackupVersion,
				int(backupFile.replace(saveStem, '').replace(savePath.ext, ''))
			)
		except ValueError:
			print(  # noqa: T201
				f'Failed to parse version from unexpected matched backup file: {backupFile}\n'
				+ traceback.format_exc()
			)
			continue

	lastBackup = f'{saveStem}{lastBackupVersion}{savePath.ext}' if lastBackupVersion > 0 else None
	nextBackup = f'{saveStem}{lastBackupVersion + 1}{savePath.ext}'

	return lastBackup, nextBackup


def moveToBackupDir(fileToMove: TDFileInfo, backupDir: str) -> None:
	backupDir = Path(backupDir)

	if not backupDir.exists():
		backupDir.mkdir(parents=True)
	elif not backupDir.is_dir():
		raise NotADirectoryError(
			f'the backup directory, {backupDir}, must be a directory'
		)

	shutil.move(fileToMove, backupDir)


def backupAndSave(
	op,  # noqa: ANN001
	savePath: TDFileInfo,
	backupDir: Optional[str] = None
) -> None:
	if not backupDir:
		backupDir = tdu.expandPath(f'{savePath.dir}/Backup')

	lastBackup, nextBackup = findLastBackup(savePath)
	shutil.move(savePath, nextBackup)
	if lastBackup:
		moveToBackupDir(lastBackup, backupDir)

	op.save(savePath)


def disconnectAndSave(tox: ToxInfo):
	"""
	This makes a copy of the tox in the parent and resets all custom parameters
	to default before saving. This ensures there are no startup errors
	or errant bound parameters when loading it back in later.
	After saving, the copy is deleted from the parent
	"""
	try:
		parentOpPath, _, _ = tox.networkPath.rpartition('/')
		parentOp = op(parentOpPath)
		sourceOp = op(tox.networkPath)

		copy = parentOp.copy(sourceOp)
		copy.par.externaltox = ''
		resetCustomParameters(copy)

		backupAndSave(copy, tox.filePath)
	finally:
		# ensure we always delete the copy, even if we have an error during processing
		if copy:
			copy.destroy()


def toSystemToxBackupDir(tox: ToxInfo) -> str:
	"""
	Constructs a path in the project backup folder that
	matches the local directory structure for system toxes.

	From: Lib/UI/ui.tox
	To: C:/path-to-project/Backup/Lib/Ui
	"""
	toxDir = tdu.expandPath(tox.filePath.dir)
	relativePath = toxDir.replace(project.folder, '')

	return tdu.expandPath(f'{project.folder}/Backup/{relativePath}')


class ToxManager:

	@property
	def CompositionRoot(self) -> str:
		return self.ownerComp.par.Compositionroot.eval()

	def __init__(self, ownerComp, tda):  # noqa: ANN001
		self.ownerComp = ownerComp
		self.tda = tda
		self.window = ownerComp.op('window1')
		self.opFind = ownerComp.op('opfind_externalToxes')
		self.selectedToxesDat = ownerComp.op('null_selectedToxes')
		self.allToxesDat = ownerComp.op('null_allToxes')
		self.toxLister = ownerComp.op('toxLister')

	def Display(self, onlyIfDirty=False):  # noqa: ANN001, FBT002
		if onlyIfDirty and not self.hasDirtyToxes():
			return

		self.RefreshToxList()
		self.window.par.winopen.pulse()

	def SaveSystemToxes(self, selected=True):  # noqa: ANN001, FBT002
		if self.tda.Loaded:
			if confirmShouldUnload():
				self.tda.Unload()
				# best-effort attempt to refresh the ui after things have been unloaded
				run('op.toxManager.RefreshToxList()', delayFrames=30)
			# NOTE: we return here because we can't ensure that everything is immediately
			#       reset to initial state before moving on, so we rely on the user to
			#       click save after things have settled
			return

		try:
			for tox in self.getSystemToxes(selected):
				sysOp = op(tox.networkPath)
				ensureExternalToxSetup(sysOp)
				executeParameterCallback(sysOp, SETTINGS_BEFORE_SAVE_SCRIPT)
				backupAndSave(sysOp, tox.filePath, toSystemToxBackupDir(tox))
				executeParameterCallback(sysOp, SETTINGS_AFTER_SAVE_SCRIPT)

			self.Close()
		except Exception:  # noqa: BLE001
			ui.messageBox(
				'!!!Warning!!!',
				'Encountered an unexpected error while attempting to save system toxes: \n\n'
				+ traceback.format_exc(),
			)

	def SaveCompositionToxes(self):
		selectedCompositionToxes = list(self.getCompositionToxes(selected=True))
		if conflictingPath := hasConflictingFilePath(selectedCompositionToxes):
			displayConflictingPathError(conflictingPath)
			return

		toxPathsToReInit = []
		for tox in selectedCompositionToxes:
			disconnectAndSave(tox)
			toxPathsToReInit.append(tox.filePath)

		# Reload all instances of saved toxes
		for tox in self.getCompositionToxes(selected=False):
			if tox.filePath in toxPathsToReInit:
				op(tox.networkPath).par.reinitnet.pulse()

		self.Close()

	def Close(self):
		self.window.par.winclose.pulse()

	def OpenNetworkAtPath(self, networkPath: str) -> None:
		p = ui.panes.createFloating(type=PaneType.NETWORKEDITOR, name='Edit Tox')
		p.owner = op(networkPath)

	def EditCompositionAddress(self, address):  # noqa: ANN001
		toxPath = addressToToxPath(address, self.CompositionRoot)
		self.OpenNetworkAtPath(toxPath)

	def IsCompositionNetworkPath(self, networkPath: str):
		return networkPath.startswith(self.CompositionRoot + '/')

	def RefreshToxList(self):
		self.opFind.par.cookpulse.pulse()
		self.toxLister.par.Reloadinput.pulse()

	def getToxes(
		self,
		selected=True  # noqa: ANN001, FBT002
	) -> tuple[Iterable[ToxInfo], Iterable[ToxInfo]]: # yapf: disable
		toxDat = self.selectedToxesDat if selected else self.allToxesDat

		paths = [
			ToxInfo( # yapf: disable
				toxDat[rowNumber, 'path'].val,
				toxDat[rowNumber, 'networkPath'].val,
				tdu.FileInfo(toxDat[rowNumber, 'filePath'].val),
				toxDat[rowNumber, 'dirty'].val == '1'
			)
			for rowNumber in range(1, toxDat.numRows)
			if toxDat[rowNumber, 'path'].val not in EXCLUDE_PATHS
			and toxDat[rowNumber, 'filePath'].val != ''
		]

		return partition(isCompositionTox, paths)

	def getSystemToxes(self, selected=True):  # noqa: ANN001, FBT002
		systemToxes, _ = self.getToxes(selected)
		return systemToxes

	def getCompositionToxes(self, selected=True):  # noqa: ANN001, FBT002
		_, compositionToxes = self.getToxes(selected)
		return compositionToxes

	def HasSelectedCompositionToxes(self):
		return any(self.getCompositionToxes(selected=True))

	def HasSelectedSystemToxes(self):
		return any(self.getSystemToxes(selected=True))

	# TODO: remove if no longer is in use
	def hasDirtyComposition(self, selected=False):  # noqa: ANN001, FBT002
		return hasDirty(self.getCompositionToxes(selected))

	def hasDirtySystem(self):
		return hasDirty(self.getSystemToxes(selected=False))

	def hasDirtyToxes(self):
		systemToxes, compositionToxes = self.getToxes(selected=False)
		return hasDirty(systemToxes) or hasDirty(compositionToxes)

	# TODO(#84)
	# def CreateNewExternalizedComponent(self):
	#  - set color
	#  - set external parameter
	#  - save tox
	#  - with extension?
	# return
