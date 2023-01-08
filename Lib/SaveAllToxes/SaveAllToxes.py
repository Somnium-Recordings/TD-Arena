import time
import traceback

DIRTY_COL = 2


def formatTimestamp(timestamp):
	winSecs = int(timestamp / 10000000)  ## divide by 10 000 000 to get seconds
	epoch = max(winSecs - 11644473600, 0)
	timeStr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch))
	return timeStr


SETTINGS_PAGE_NAME = 'Save Settings'
SETTINGS_BEFORE_SAVE_SCRIPT = 'Savealltoxesonbeforesave'
SETTINGS_AFTER_SAVE_SCRIPT = 'Savealltoxesonaftersave'


def hasCustomParameter(comp, name):
	return any(par.name == name for par in comp.customPars)


def ensureSaveSettingsCreated(comp):
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


def isCloneOfSelf(c):
	return op(c.par.clone).id == c.id


def isClone(o):
	return o is not None and o.par.clone


def isCloneAndNotOfSelf(c, parentsToCheck=2):
	opsToCheck = [c.parent(i) for i in range(parentsToCheck + 1)]

	return next(
		filter(None, [isClone(o) and not isCloneOfSelf(o) for o in opsToCheck]),
		False
	)


def isSaveable(c):
	if not c.par.externaltox:
		return False

	# Only save clones if they are a clone of themselves
	if isCloneAndNotOfSelf(c):
		return False

	# Don't save dynamically created components inside of the composition
	# TODO: move this to configurable parameter
	if c.path.startswith('/tdArena/render/composition/'):
		return False

	return True


def saveExternalToxes(rows):
	try:
		dirtyComps = [op(row[0].val) for row in rows]

		for comp in dirtyComps:
			executeParameterCallback(comp, SETTINGS_BEFORE_SAVE_SCRIPT)

		for comp in dirtyComps:
			comp.save(tdu.expandPath(comp.par.externaltox))

		for comp in dirtyComps:
			executeParameterCallback(comp, SETTINGS_AFTER_SAVE_SCRIPT)

		op('window1').par.winclose.pulse()
	except Exception as _:  # pylint: disable=broad-except

		ui.messageBox(
			'!!!Warning!!!',
			'Encountered an unexpected error while attempting to save external toxes: \n\n'
			+ traceback.format_exc(),
		)


class SaveAllToxes:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp
		self.compList = self.ownerComp.op('table_externalizedComps')

	@property
	def projectRoot(self):
		return self.ownerComp.par.Projectroot

	def SaveDirty(self):
		dirtyRows = [
			r for r in self.compList.rows()[1:] if r[DIRTY_COL].val == 'True'
		]
		saveExternalToxes(dirtyRows)

	def SaveAll(self):
		"""
		The "Dirty" flag isn't set if you modify component params. So sometimes we
		need to just save everything.
		"""
		saveExternalToxes(self.compList.rows()[1:])

	def Display(self, onlyIfDirty=False):
		hasDirty = self.updateCompList()

		if not onlyIfDirty or hasDirty:
			op('window1').par.winopen.pulse()

	def ToggleDirtyStatus(self, opPath):
		dirtyCell = self.compList[opPath, DIRTY_COL]
		if dirtyCell.val == 'True':
			dirtyCell.val = 'False'
		else:
			dirtyCell.val = 'True'

	def updateCompList(self) -> bool:
		self.compList.clear(keepFirstRow=True)
		children = [
			c for c in op(self.projectRoot).findChildren(type=COMP) if isSaveable(c)
		]

		hasDirty = False
		for child in children:
			ensureSaveSettingsCreated(child)
			self.compList.appendRow(
				[child.path,
					formatTimestamp(child.externalTimeStamp), child.dirty]
			)
			if child.dirty:
				hasDirty = True

		return hasDirty
