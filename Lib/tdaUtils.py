import math
import re
from collections import namedtuple
from pathlib import Path


def intIfSet(stringNumber):
	# NOTE: the == 0 check is to support touch table cells with a value of 0
	return int(stringNumber) if stringNumber or stringNumber == 0 else None


def layoutComps(compList, columns=4, xBase=0):
	# TODO: use TDF.arrangeNode instead
	# TODO: should we skip if ui.performMode == False?
	for i, comp in enumerate(compList):
		comp.nodeX = xBase + (i % columns) * 200
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


SELECTED_DECK_LOCATION_RE = re.compile(
	r'/selecteddeck/layers/(\d+)/clips/(\d+)/?.*'
)
# TODO(#47): turn deckLocation into named tuple since it's used in a bunch of places


def mapAddressToDeckLocation(address: str):
	m = re.match(SELECTED_DECK_LOCATION_RE, address)
	assert m, 'expected to match layer and clip number in {}'.format(address)

	return (int(m.group(1)), int(m.group(2)))


EFFECT_LOCATION_RE = re.compile(r'(/composition/.*/effects)/(\d+)/?.*')
EffectLocation = namedtuple('EffectLocation', ['containerAddress', 'effectID'])


def mapAddressToEffectLocation(address: str) -> EffectLocation:
	m = re.match(EFFECT_LOCATION_RE, address)
	assert m, f'expected to match effect container and effect ID in {address}'

	return EffectLocation(containerAddress=m.group(1), effectID=int(m.group(2)))


DECK_ID_RE = re.compile(r'/composition/decks/(\d+)')


def getDeckID(address):
	m = re.match(DECK_ID_RE, address)
	assert m, 'expected to match deck id in {}'.format(address)

	return int(m.group(1))


LAYER_ID_RE = re.compile(r'/composition/layers/(\d+)')


def getLayerID(address):
	m = re.match(LAYER_ID_RE, address)
	assert m, 'expected to match layer id in {}'.format(address)

	return int(m.group(1))


CLIP_ID_RE = re.compile(r'/composition/clips/(\d+)')


def getClipID(address):
	m = re.match(CLIP_ID_RE, address)
	assert m, 'expected to match clip id in {}'.format(address)

	return int(m.group(1))


# /layer/1 -> /layer/layer1
EXPAND_FROM_ID_RE = re.compile(r'(layer|clip|deck|effect)s/([\d]+)')


def addressToValueLocation(address, compositionPath):
	"""
	from: /composition/layers/1/...
	to  : /composition/layers/layer1/...
	"""

	fullPath = EXPAND_FROM_ID_RE.sub(r'\1s/\1\2', address)

	return tuple(fullPath.replace('/composition', compositionPath).rsplit('/', 1))


# /layer/layer1 -> /layer/1
COLLAPSE_TO_ID_RE = re.compile(
	r'/(layer|clip|deck|effect)s/(layer|clip|deck|effect)(\d+)'
)


def parameterPathToAddress(path: str, parameter: str):
	"""
	from: /tdArena/composition/layers/layer1/...
	from: /tdArena/render/composition/layers/layer1/...
	to  : /composition/layers/1/...
	"""
	compositionStart = path.find('/composition')
	address = COLLAPSE_TO_ID_RE.sub(r'/\1s/\3', path[compositionStart:])

	return '{}/{}'.format(address, parameter)


def addressToExport(address):
	(path, prop) = addressToValueLocation(address, '')
	return '{}:{}'.format(path.lstrip('/'), prop)


def addSectionParameters(op, order: int, name: str, opacity: float = None):
	page = op.appendCustomPage('Section')

	# TODO(#41): can we use this for the "Video" section's opacity parameter?
	if opacity is not None:
		# TODO(#43): implement/hard-code as "Section Opactiy" w/ collapse logic
		sectionOpacity, = page.appendFloat('Sectionopacity', label='Opacity')
		sectionOpacity.val = opacity

	sectionName, = page.appendStr('Sectionname', label='Section Name')
	sectionName.val = name

	expanded, = page.appendToggle('Sectionexpanded', label='Section Expanded')
	expanded.val = True

	sectionOrder, = page.appendFloat('Sectionorder', label='Section Order')
	sectionOrder.val = order

	pageOrder = [page.name for page in op.customPages]
	pageOrder.insert(0, pageOrder.pop())  # ensure "Section" is first page
	op.sortCustomPages(*pageOrder)


# TODO(#48): apply to clip names
def filePathToName(path: str) -> str:
	return re.sub(
		r'(\w)([A-Z])', r'\1 \2',
		Path(path).stem.replace('-', ' ').replace('_', ' ')
	).title()
