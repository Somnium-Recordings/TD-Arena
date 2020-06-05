from tda import BaseExt


class Thumbnails(BaseExt):
	def __init__(self, ownerComponent, logger):
		super().__init__(ownerComponent, logger)
		self.deckCells = ownerComponent.op('table_deckCells')
		self.deckClips = ownerComponent.op('null_deckClips')

	def Sync(self):
		self.deckCells.setSize(self.deckClips.numRows * self.deckClips.numCols, 1)

		nextRow = 0
		for row in self.deckClips.rows():
			for cell in row:
				self.deckCells[nextRow, 0] = cell
				nextRow += 1

		self.logDebug('synced')
