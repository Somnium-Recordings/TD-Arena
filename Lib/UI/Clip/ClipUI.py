from tda import BaseExt, DroppedItem


class ClipUI(BaseExt):
	@property
	def ClipDeckAddress(self):
		return self.ownerComponent.par.Clipdeckaddress.eval()

	def __init__(
		self, ownerComponent, logger, uiState, movieBrowser, generatorBrowser,
		effectBrowser
	):  # pylint: disable=too-many-arguments
		super().__init__(ownerComponent, logger)
		self.uiState = uiState
		self.movieBrowser = movieBrowser
		self.generatorBrowser = generatorBrowser
		self.effectBrowser = effectBrowser

	def OnDrop(self, droppedItem: DroppedItem):
		if droppedItem.dropName == 'clipLabel':
			droppedClip: ClipUI = op(droppedItem.itemPath).parent.clipUI
			self.uiState.SendMessage(
				f'{droppedClip.ClipDeckAddress}/move', self.ClipDeckAddress
			)
		elif droppedItem.dropName.startswith('movie'):
			(fileName, filePath) = self.movieBrowser.GetPath(droppedItem.dropName)
			self.uiState.SendMessage(
				f'{self.ClipDeckAddress}/source/load', 'movie', fileName, filePath
			)
		elif droppedItem.dropName.startswith('generator'):
			(fileName, filePath) = self.generatorBrowser.GetPath(droppedItem.dropName)
			# TODO: should we change sourceType to "generator" instead of tox?
			self.uiState.SendMessage(
				f'{self.ClipDeckAddress}/source/load', 'tox', fileName, filePath
			)
		elif droppedItem.dropName.startswith('effect'):
			(_, filePath) = self.effectBrowser.GetPath(droppedItem.dropName)
			self.uiState.SendMessage(
				f'{self.ClipDeckAddress}/video/effects/add', filePath
			)
		else:
			raise NotImplementedError(f'unsupported drop name: {droppedItem.dropName}')

	def OnLeftClickThumb(self):
		self.uiState.SendMessage(f'{self.ClipDeckAddress}/connect')

	def OnRightClickThumb(self):
		self.uiState.SendMessage(f'{self.ClipDeckAddress}/clear')
