from tda import BaseExt


class Thumbnails(BaseExt):
	def __init__(self, ownerComponent, logger):
		super().__init__(ownerComponent, logger)
		self.thumbnailClips = ownerComponent.op('null_thumbnailClips')

		self.thumbnailClipIds = ownerComponent.op('table_thumbnailClipIds')
		self.thumbnailClipIds.clear()

	def Sync(self):
		self.thumbnailClipIds.setSize(
			self.thumbnailClips.numRows * self.thumbnailClips.numCols, 1
		)

		nextRow = 0
		for row in self.thumbnailClips.rows():
			for cell in row:
				self.thumbnailClipIds[nextRow, 0] = cell
				nextRow += 1

		self.logDebug('synced')
