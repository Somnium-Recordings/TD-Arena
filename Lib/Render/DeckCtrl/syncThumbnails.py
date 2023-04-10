from typing import cast

deckCells = cast(DAT, op('table_deckCells'))
activeDeck = cast(DAT, op('select_activeDeck'))

deckCells.setSize(activeDeck.numRows * activeDeck.numCols, 1)

nextRow = 0
for row in activeDeck.rows():
	for cell in row:
		deckCells[nextRow, 0] = cell
		nextRow += 1
