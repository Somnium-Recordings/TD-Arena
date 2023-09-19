from typing import cast

from tda import BaseExt
from tdaUtils import addSectionParameters, filePathToName

LOAD_FRAME_DELAY = 2
MAX_WAIT_CYCLES = 20

COMPOSITION_WIDTH_EXPR = 'parent.composition.par.Width'
COMPOSITION_HEIGHT_EXPR = 'parent.composition.par.Height'


# TODO: use ABC and create a base "Source" class?
# TODO: Move ToxSource and MovieSource out of cloned base
class ToxSource(BaseExt):

	@property
	def tox(self):
		return self.ownerComponent.op('./tox')

	def __init__(self, ownerComponent, logger):  # noqa: ANN001
		super().__init__(ownerComponent, logger)
		# TODO: support running a tox in an engine
		self.thumb = ownerComponent.op('./null_thumb')
		self.state = ownerComponent.op('./table_state')
		self.fitFinalTop = cast(TOP, ownerComponent.op('./fit1'))
		self.fitThumbnailTop = cast(TOP, ownerComponent.op('./fit2'))

	def Load(self):
		self.setLoading()
		self.bindCompositionParameters()
		self.logInfo('loading tox')
		self.tox.par.reinitnet.pulse()
		self.waitForPreload()

	def bindCompositionParameters(self):
		self.fitFinalTop.par.resolutionw.expr = COMPOSITION_WIDTH_EXPR
		self.fitFinalTop.par.resolutionh.expr = COMPOSITION_HEIGHT_EXPR
		self.fitThumbnailTop.par.resolutionw.expr = COMPOSITION_WIDTH_EXPR
		self.fitThumbnailTop.par.resolutionh.expr = COMPOSITION_HEIGHT_EXPR

	def waitForPreload(self, waitCount=0):  # noqa: ANN001
		# TODO(#44): this isn't actually necessary, reinitnet seems to be synchronous
		if waitCount > MAX_WAIT_CYCLES:
			self.setLoaded(wasSuccessful=False)
			self.logError(
				f'preloading tox took more than {MAX_WAIT_CYCLES} cycles, aborting. Does the tox contain null_final?'
			)
			return

		if self.tox.isCOMP:
			self.tox.par.w.expr = COMPOSITION_WIDTH_EXPR
			self.tox.par.h.expr = COMPOSITION_HEIGHT_EXPR

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

	def setLoaded(self, wasSuccessful=True):  # noqa: ANN001, FBT002
		if not wasSuccessful:
			self.setStatusText('Error')

		self.state['Loaded', 1] = int(wasSuccessful)

	def setStatusText(self, text):  # noqa: ANN001
		self.state['Status Text', 1] = text
