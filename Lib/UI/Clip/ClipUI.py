from tda import BaseExt


class ClipUI(BaseExt):
	@property
	def ClipAddress(self):
		return '/selecteddeck/layers/{}/clips/{}'.format(
			self.ownerComponent.parent.layerUI.digits, self.ownerComponent.digits
		)

	def __init__(self, ownerComponent, logger, browserUI, uiState, compCtrl):  # pylint: disable=too-many-arguments

		super().__init__(ownerComponent, logger)
		self.browserUI = browserUI
		self.uiState = uiState
		self.compCtrl = compCtrl

	#
	#  arguments for dropping nodes           (and files)
	#
	#       args[0] dropped node name            (or filename)
	#       args[1] x position
	#       args[2] y position
	#       args[3] dragged index
	#       args[4] total dragged
	#       args[5] operator                     (or file extension)
	#       args[6] dragged node parent network  (or parent directory)
	#       args[7] dropped network
	#
	def OnDrop(self, *args):
		droppedNode = args[0]
		sourceType = self.getSourceType(droppedNode)
		if sourceType is None:
			self.logDebug('ignoring drop event for unhandled sourceType')
			return

		(fileName, filePath) = self.browserUI.GetPath(droppedNode)

		if sourceType == 'effect':
			self.uiState.SendMessage(f'{self.ClipAddress}/video/effects/add', filePath)
		else:
			self.uiState.SendMessage(
				f'{self.ClipAddress}/source/load', sourceType, fileName, filePath
			)

	def getSourceType(self, nodeName):
		if nodeName.startswith('movie'):
			return 'movie'

		if nodeName.startswith('generator'):
			return 'tox'

		if nodeName.startswith('effect'):
			return 'effect'

		self.logDebug('Could not match node to clip type: {}'.format(nodeName))

		return None

	def OnLeftClickThumb(self):
		self.uiState.SendMessage(f'{self.ClipAddress}/connect')

	def OnRightClickThumb(self):
		self.uiState.SendMessage(f'{self.ClipAddress}/clear')
