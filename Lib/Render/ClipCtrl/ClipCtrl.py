from tda import LoadableExt
from tdaUtils import clearChildren, getCellValues, layoutComps


# TODO: be smarter about this, direct map?
def initMovieClip(name, path, clip, source):
	clip.par.Clipname = name
	source.par.Sourcepath = path


def initToxClip(name, path, clip, source):
	clip.par.Clipname = name
	source.par.Sourcepath = path


DEFAULT_STATE = []
STATE_KEY = 'clips'


class ClipCtrl(LoadableExt):
	def __init__(self, ownerComponent, logger, state):
		super().__init__(ownerComponent, logger)
		self.state = state

		self.clipList = ownerComponent.op('./table_clipIDs')
		self.clipTemplate = ownerComponent.op('./clipTemplate')
		self.clipOpState = ownerComponent.op('null_clipState')
		self.composition = ownerComponent.op('../composition')
		assert self.composition, 'could not find composition component'

		self.sourceMap = {
			'movie': {
				'template': ownerComponent.op('./movieSourceTemplate'),
				'init': initMovieClip,
			},
			'tox': {
				'template': ownerComponent.op('./toxSourceTemplate'),
				'init': initToxClip,
			}
		}

	def Init(self):
		self.setUnloaded()

		self.clipContainer = self.composition.op('clips')
		if self.clipContainer:
			self.logDebug('clearing clips in composition')
			clearChildren(self.clipContainer)
		else:
			self.logInfo('clips op not found in composition, initalizing')
			self.clipContainer = self.composition.create(baseCOMP, 'clips')

		self.nextClipID = 0
		self.clipComps = {}
		self.clipList.clear()
		self.SendState()

		self.logInfo('initialized')

	def Load(self):
		self.setLoading()
		self.logInfo('loading composition')

		for clip in self.state.Get(STATE_KEY, DEFAULT_STATE)[1:]:
			(clipID, clipName, active, sourceType, path) = clip
			clipID = int(clipID)

			self.CreateClip(sourceType, clipName, path, clipID)
			# TODO: should we even be doing this?
			# It currently causes thumbnail generation to choke
			if bool(int(active)):
				self.ActivateClip(clipID)

		self.logInfo('loaded {} clips in composition'.format(self.clipList.numRows))
		self.setLoaded()
		self.SendState()

	def SendState(self):
		self.logDebug('sending state')

		state = [
			getCellValues(clip) for clip in self.clipOpState.rows()
		] if self.Loaded else None

		self.state.Update(STATE_KEY, state)

	def GetClipProp(self, clipID, propName):
		if not self.Loaded:
			return None

		prop = self.clipOpState[str(clipID), propName]
		return prop.val if prop is not None else None

	def CreateClip(self, sourceType, name, path, clipID=None):
		clip = self.createNextClip(clipID)
		self.loadSource(sourceType, name, path, clip)

		return clip

	def ReplaceSource(self, sourceType, name, path, clipID):
		clip = self.clipComps[clipID]
		assert clip, 'could not replace {} clip of unknown clip id {}'.format(
			sourceType, clipID
		)

		self.loadSource(sourceType, name, path, clip)

		return clip

	def ActivateClip(self, clipID):
		clip = self.clipComps[clipID]
		assert clip, 'could not activate unknown clip id {}'.format(clipID)
		source = clip.op('source')

		clip.par.Active = 1

		source.par.Onactivate.pulse()

	def DeactivateClip(self, clipID):
		clip = self.clipComps[clipID]
		assert clip, 'could not deactivate unknown clip id {}'.format(clipID)

		clip.par.Active = 0

	def DeleteClip(self, clipID):
		assert self.clipComps, 'could not delete clip, composition not loaded'

		cell = self.clipList.findCell(clipID)
		if cell is not None:
			self.clipList.deleteRow(cell.row)

		clip = self.clipComps.pop(clipID, None)
		if clip is not None:
			clip.destroy()
			self.updateClipNetworkPositions()

	def loadSource(self, sourceType, name, path, clip):
		sourceMap = self.sourceMap.get(sourceType, None)
		assert sourceMap, 'unmapped source type "{}" requested'.format(sourceType)
		sourceTemplate = sourceMap['template']
		initSourceFn = sourceMap['init']

		existingSource = clip.op('source')
		if existingSource:
			# TODO: is there a more performant way to do this?
			# How does this perform if clip is active?
			existingSource.destroy()

		newSource = clip.copy(sourceTemplate, name='source')
		initSourceFn(name, path, clip, newSource)

		return newSource

	def createNextClip(self, clipID=None):
		assert self.clipContainer, 'could not create clip, composition not loaded'

		if clipID is None:
			clipID = self.nextClipID
			self.nextClipID += 1
		elif clipID >= self.nextClipID:
			self.nextClipID = clipID + 1

		clip = self.clipContainer.copy(
			self.clipTemplate, name='clip{}'.format(clipID)
		)
		self.clipComps[clipID] = clip

		self.clipList.appendRow([clipID])

		self.updateClipNetworkPositions()

		return clip

	def updateClipNetworkPositions(self):
		layoutComps(self.clipComps.values())
