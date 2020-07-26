import math


def intIfSet(stringNumber):
	return int(stringNumber) if stringNumber else None


def layoutComps(compList, columns=4):
	# TODO: use TDF.arrangeNode instead
	# TODO: should we skip if ui.performMode == False?
	for i, comp in enumerate(compList):
		comp.nodeX = 0 + (i % columns) * 200
		comp.nodeY = (1 + math.floor(i / columns)) * -200


def getCellValues(datRow):
	return [cell.val for cell in datRow]
