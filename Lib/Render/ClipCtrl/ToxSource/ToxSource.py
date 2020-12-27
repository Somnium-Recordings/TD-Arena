from tda import BaseExt
from tdaUtils import addSectionParameters, filePathToName

LOAD_FRAME_DELAY = 2
MAX_WAIT_CYCLES = 20


# TODO: use ABC and create a base "Source" class?
# TODO: Move ToxSource and MovieSource out of cloned base
class ToxSource(BaseExt):
	@property
	def tox(self):
		return self.ownerComponent.op('./tox')

	def __init__(self, ownerComponent, logger):
		super().__init__(ownerComponent, logger)
		# TODO: support running a tox in an engine
		self.thumb = ownerComponent.op('./null_thumb')
		self.state = ownerComponent.op('./table_state')

	def Load(self):
		self.setLoading()
		self.logInfo('loading tox')
		self.tox.par.reinitnet.pulse()
		self.waitForPreload()

	def waitForPreload(self, waitCount=0):
		# TODO(#44): this isn't actually necessary, reinitnet seems to be synchronus
		if waitCount > MAX_WAIT_CYCLES:
			self.setLoaded(wasSuccessful=False)
			self.logError(
				'preloading tox took more than {} cycles, aborting. Does the tox contain null_final?'
				.format(MAX_WAIT_CYCLES)
			)
			return

		if not self.isSourceLoaded():
			run('args[0].waitForPreload(args[1])', self, waitCount + 1, delayFrames=1)
			return

		self.logDebug('tox loaded, setting thumbnail')
		self.setThumbail()

		addSectionParameters(
			self.tox,
			order=-2,
			name=filePathToName(self.ownerComponent.par.Sourcepath.eval())
		)

	def isSourceLoaded(self):
		return bool(self.tox.op('./null_final'))

	def setThumbail(self):
		# switch output to loaded video so we can capture as thumb if needed
		self.setLoaded()

		# wait frames so thumbnail null has image in it it to "lock"
		run('args[0].lockThumbnail()', self, delayFrames=3)

	def lockThumbnail(self):
		self.thumb.lock = True
		self.logDebug('thumbnail locked')

	def setLoading(self):
		self.state['Loaded', 1] = 0
		self.setStatusText('Loading...')

	def setLoaded(self, wasSuccessful=True):
		if not wasSuccessful:
			self.setStatusText('Error')

		self.state['Loaded', 1] = int(wasSuccessful)

	def setStatusText(self, text):
		self.state['Status Text', 1] = text
