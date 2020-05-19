deckCells = op("table_deckCells")
activeDeck = op("select_activeDeck")

deckCells.setSize(activeDeck.numRows * activeDeck.numCols, 1)

nextRow = 0
for row in activeDeck.rows():
    for cell in row:
        deckCells[nextRow, 0] = cell
        nextRow += 1
