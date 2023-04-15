from typing import Optional

from tda import LoadableExt
from tdaUtils import addSectionParameters, clearChildren, getCellValues, layoutComps


# TODO: be smarter about this, direct map?
def initMovieClip(name, path, clip, source):  # noqa: ANN001
	clip.par.Clipname = name
	source.par.Sourcepath = path


def initToxClip(name, path, clip, source):  # noqa: ANN001
	clip.par.Clipname = name
	source.par.Sourcepath = path


DEFAULT_STATE = []


class ClipCtrl(LoadableExt):

	def __init__(self, ownerComponent, logger, effectCtrl):  # noqa: ANN001
		super().__init__(ownerComponent, logger)

		self.effectCtrl = effectCtrl
		self.clipList = ownerComponent.op('./table_clipIDs')
		self.clipTemplate = ownerComponent.op('./clipTemplate')
		self.clipState = ownerComponent.op('null_clipState')
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

	def Init(self, _renderState):  # noqa: ANN001
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

		self.logInfo('initialized')

	def Load(self, saveState=None):  # noqa: ANN001
		self.setLoading()
		self.logInfo('loading composition')

		state = saveState or DEFAULT_STATE
		for clip in state[1:]:
			(clipID, clipName, _, sourceType, path) = clip
			clipID = int(clipID)

			self.CreateClip(sourceType, clipName, path, clipID)

		self.logInfo(f'loaded {self.clipList.numRows} clips in composition')
		self.setLoaded()

	def GetSaveState(self):
		return [
			getCellValues(clip) for clip in self.clipState.rows()
		] if self.Loaded else None

	def GetClipProp(self, clipID: int, propName):  # noqa: ANN001
		if not self.Loaded:
			return None

		prop = self.clipState[str(clipID), propName]
		return prop.val if prop is not None else None

	def CreateClip(
		self,
		sourceType,  # noqa: ANN001
		name,  # noqa: ANN001
		path,  # noqa: ANN001
		clipID: Optional[int] = None
	):  # noqa: ANN001, RUF100
		clip = self.createNextClip(clipID)
		self.loadSource(sourceType, name, path, clip)

		return clip

	def ReplaceSource(self, sourceType, name, path, clipID: int):  # noqa: ANN001
		clip = self.clipComps[clipID]
		assert clip, f'could not replace {sourceType} clip of unknown clip id {clipID}'
		self.loadSource(sourceType, name, path, clip)

		return clip

	def ActivateClip(self, clipID: int, fromSelect=False):  # noqa: ANN001
		clip = self.clipComps[clipID]
		assert clip, f'could not activate unknown clip id {clipID}'
		source = clip.op('./video/source')

		if not fromSelect:
			clip.par.Active = 1

		if not fromSelect or clip.par.Active.eval() == 0:
			source.par.Onactivate.pulse()

	def DeactivateClip(self, clipID: int):
		clip = self.clipComps[clipID]
		assert clip, f'could not deactivate unknown clip id {clipID}'

		clip.par.Active = 0

	def DeleteClip(self, clipID: int):
		assert self.clipComps, 'could not delete clip, composition not loaded'

		cell = self.clipList.findCell(clipID)
		if cell is not None:
			self.clipList.deleteRow(cell.row)

		clip = self.clipComps.pop(clipID, None)
		if clip is not None:
			clip.destroy()
			self.effectCtrl.ClearEffectContainer(
				f'/composition/clips/{clipID}/video/effects'
			)
			self.updateClipNetworkPositions()

	def loadSource(self, sourceType, name, path, clip):  # noqa: ANN001
		sourceMap = self.sourceMap.get(sourceType, None)
		assert sourceMap, f'unmapped source type "{sourceType}" requested'
		sourceTemplate = sourceMap['template']
		initSourceFn = sourceMap['init']

		video = clip.op('video')

		existingSource = video.op('source')
		if existingSource:
			# TODO: is there a more performant way to do this?
			# How does this perform if clip is active?
			existingSource.destroy()

		newSource = video.copy(sourceTemplate, name='source')
		initSourceFn(name, path, clip, newSource)

		return newSource

	def createNextClip(self, clipID: Optional[int] = None):
		assert self.clipContainer, 'could not create clip, composition not loaded'

		if clipID is None:
			clipID = self.nextClipID
			self.nextClipID += 1
		elif clipID >= self.nextClipID:
			self.nextClipID = clipID + 1

		clip = self.clipContainer.copy(self.clipTemplate, name=f'clip{clipID}')
		videoContainer = clip.op('video')
		addSectionParameters(videoContainer, order=-1, name='Video')

		self.clipComps[clipID] = clip

		self.clipList.appendRow([clipID])

		self.updateClipNetworkPositions()

		return clip

	def updateClipNetworkPositions(self):
		layoutComps(self.clipComps.values())
