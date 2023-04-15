from tda import BaseExt

LOAD_FRAME_DELAY = 2
MAX_WAIT_CYCLES = 20


class MovieSource(BaseExt):

	def __init__(self, ownerComponent, logger):  # noqa: ANN001
		super().__init__(ownerComponent, logger)
		self.movie = ownerComponent.op('./moviefilein1')
		self.thumb = ownerComponent.op('./null_thumb')
		self.state = ownerComponent.op('./table_state')

	def Load(self):
		self.setLoading()
		self.logInfo('loading movie')
		self.movie.preload()
		self.waitForPreload()

	def waitForPreload(self, waitCount=0):  # noqa: ANN001
		if waitCount > MAX_WAIT_CYCLES:
			self.setLoaded(wasSuccessful=False)
			self.logError(
				f'preloading video took more than {MAX_WAIT_CYCLES} cycles, aborting'
			)
			return

		if not self.isSourceLoaded():
			run('args[0].waitForPreload(args[1])', self, waitCount + 1, delayFrames=2)
			return

		self.logDebug('movie loaded, setting thumbnail')
		self.setThumbail()

	def isSourceLoaded(self):
		return self.movie.isFullyPreRead

	def setThumbail(self):
		# seek to middle of clip for thumbnail
		self.movie.par.cuepoint = 0.5
		self.movie.par.cue = 1

		# switch output to loaded video so we can capture as thumb
		self.setLoaded()

		# wait frames so thumbnail null has image in it it to "lock"
		run('args[0].lockThumbnail()', self, delayFrames=3)

	def lockThumbnail(self):
		self.thumb.lock = True
		self.movie.par.cuepoint = 0
		self.movie.par.cue = 0
		self.logDebug('thumbnail locked')

	def setLoading(self):
		self.state['Loaded', 1] = 0
		self.setStatusText('Loading...')

	def setLoaded(self, wasSuccessful=True):  # noqa: ANN001
		if not wasSuccessful:
			self.setStatusText('Error')

		self.state['Loaded', 1] = int(wasSuccessful)

	def setStatusText(self, text):  # noqa: ANN001
		self.state['Status Text', 1] = text
