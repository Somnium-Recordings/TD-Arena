from tdaUtils import layoutComps


def initMovieClip(name, path, clip, source):
	clip.par.Clipname = name
	source.par.Moviepath = path


def initToxClip(name, path, clip, source):
	clip.par.Clipname = name
	source.par.Toxpath = path


class ClipCtrl:  # pylint: disable=too-many-instance-attributes
	@property
	def StateDATs(self):
		"""
        paths to DATs that RenderState should watch for changes
		TODO: just hard code this over in the state component...
        """
		return self.ClipState.path

	def __init__(self, ownerComponent, logger):
		self.ownerComponent = ownerComponent
		self.logger = logger

		self.clipList = ownerComponent.op('./table_clipIDs')
		self.clipTemplate = ownerComponent.op('./clipTemplate')
		self.ClipState = ownerComponent.op('null_clipState')
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

		# NOTE: These lines should be mirrored in Reinit
		self.nextClipID = None
		self.clipComps = None
		self.composition = None
		self.clipContainer = None
		self.logInfo('initialized')

	def Reinit(self):
		self.nextClipID = None
		self.clipComps = None
		self.composition = None
		self.clipContainer = None
		self.clipList.clear()
		self.logInfo('reinitialized')

	def Load(self):
		self.logInfo('loading composition')

		self.composition = self.ownerComponent.op('../composition')
		assert self.composition, 'could not find composition component'

		self.clipContainer = self.composition.op('clips')
		if not self.clipContainer:
			self.logInfo('clips op not found in composition, initalizing')
			self.clipContainer = self.composition.create(baseCOMP, 'clips')

		self.nextClipID = 0
		self.clipComps = {}
		self.clipList.clear()
		for clip in self.clipContainer.findChildren(
			name='clip*', depth=1, type=COMP
		):
			clipID = clip.digits
			self.clipComps[clipID] = clip
			if clipID >= self.nextClipID:
				self.nextClipID = clipID + 1

			self.clipList.appendRow([clipID])

		self.logInfo('loaded {} clips in composition'.format(self.clipList.numRows))

	def CreateClip(self, sourceType, name, path):
		clip = self.createNextClip()
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
		# TODO: figure out a better way to handle this.
		# Right now if we don't do this the source looses its Moviepath property on reload
		newSource.par.externaltox = None

		initSourceFn(name, path, clip, newSource)

		return newSource

	def createNextClip(self):
		assert self.clipContainer, 'could not create clip, composition not loaded'

		clipID = self.nextClipID
		clip = self.clipContainer.copy(
			self.clipTemplate, name='clip{}'.format(clipID)
		)
		self.clipComps[clipID] = clip
		self.nextClipID += 1

		self.clipList.appendRow([clipID])

		self.updateClipNetworkPositions()

		return clip

	def updateClipNetworkPositions(self):
		layoutComps(self.clipComps.values())

	def logInfo(self, *args):
		self.logger.Info(self.ownerComponent, *args)
