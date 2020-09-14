import math
import re


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


def clearChildren(op):
	for child in op.findChildren(depth=1):
		child.destroy()


def syncToDat(data, targetDat):
	if data is None:
		targetDat.clear()
		return

	rowCount = len(data)
	columnCount = len(data[0]) if rowCount > 0 else 0
	targetDat.setSize(rowCount, columnCount)

	for rowIndex, row in enumerate(data):
		for columnIndex, cell in enumerate(row):
			targetDat[rowIndex, columnIndex] = cell or ''


def mapAddressToClipLocation(address):
	m = re.match(r'/composition/layers/(\d+)/clips/(\d+)/?.*', address)
	assert m, 'expected to match layer and clip number in {}'.format(address)

	return (int(m.group(1)), int(m.group(2)))


def getLayerId(address):
	m = re.match(r'/composition/layers/(\d+)?.*', address)
	assert m, 'expected to match layer id in {}'.format(address)

	return int(m.group(1))


def addressToValueLocation(address, compositionPath):
	p = re.compile(r'(layer|clip)s/([\d]+)')

	fullPath = p.sub(r'\1s/\1\2', address)

	return tuple(fullPath.replace('/composition', compositionPath).rsplit('/', 1))
