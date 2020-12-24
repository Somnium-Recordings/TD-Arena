import math
import re


def intIfSet(stringNumber):
	# NOTE: the == 0 check is to support touch table cells with a value of 0
	return int(stringNumber) if stringNumber or stringNumber == 0 else None


def layoutComps(compList, columns=4):
	# TODO: use TDF.arrangeNode instead
	# TODO: should we skip if ui.performMode == False?
	for i, comp in enumerate(compList):
		comp.nodeX = 0 + (i % columns) * 200
		comp.nodeY = (1 + math.floor(i / columns)) * -200


def layoutChildren(op, columns=4):
	children = op.findChildren(depth=1)
	layoutComps(children, columns)


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


def mapAddressToDeckLocation(address):
	m = re.match(r'/selecteddeck/layers/(\d+)/clips/(\d+)/?.*', address)
	assert m, 'expected to match layer and clip number in {}'.format(address)

	return (int(m.group(1)), int(m.group(2)))


def getDeckID(address):
	m = re.match(r'/composition/decks/(\d+)?.*', address)
	assert m, 'expected to match deck id in {}'.format(address)

	return int(m.group(1))


def getLayerID(address):
	m = re.match(r'/composition/layers/(\d+)?.*', address)
	assert m, 'expected to match layer id in {}'.format(address)

	return int(m.group(1))


def getClipID(address):
	m = re.match(r'/composition/clips/(\d+)?.*', address)
	assert m, 'expected to match clip id in {}'.format(address)

	return int(m.group(1))


def addressToValueLocation(address, compositionPath):
	"""
	from: /composition/layers/1/...
	to  : /composition/layers/layer1/...
	"""
	p = re.compile(r'(layer|clip|deck)s/([\d]+)')

	fullPath = p.sub(r'\1s/\1\2', address)

	return tuple(fullPath.replace('/composition', compositionPath).rsplit('/', 1))


def parameterPathToAddress(path: str, parameter: str):
	"""
	from: /tdArena/composition/layers/layer1/...
	from: /tdArena/render/composition/layers/layer1/...
	to  : /composition/layers/1/...
	"""
	p = re.compile(r'.*/composition/(layer|clip|deck)s/(layer|clip|deck)(\d+)')

	address = p.sub(r'/composition/\1s/\3', path)

	return '{}/{}'.format(address, parameter)


def addressToExport(address):
	(path, prop) = addressToValueLocation(address, '')
	return '{}:{}'.format(path.lstrip('/'), prop)


def addSectionParameters(op, order: int, opacity: float = None):
	page = op.appendCustomPage('Section')
	pageOrder = [page.name for page in op.customPages]
	pageOrder.insert(0, pageOrder.pop())  # ensure "Section" is first page
	op.sortCustomPages(*pageOrder)

	# TODO: can we use this for the "Video" section's opacity parameter?
	if opacity is not None:
		# TODO: implement/hard-code as "Section Opactiy" w/ collapse logic
		sectionOpacity, = page.appendFloat('Sectionopacity', label='Opacity')
		sectionOpacity.val = opacity

	expanded, = page.appendToggle('Sectionexpanded', label='Section Expanded')
	expanded.val = True

	sectionOrder, = page.appendFloat('Sectionorder', label='Section Order')
	sectionOrder.val = order
