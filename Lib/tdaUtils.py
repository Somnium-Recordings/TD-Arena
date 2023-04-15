import math
import re
from collections import namedtuple
from fnmatch import fnmatchcase
from pathlib import PureWindowsPath
from typing import NamedTuple, Optional

SELECTED_DECK_LOCATION_RE = re.compile(
	r'/selecteddeck/layers/(\d+)/clips/(\d+)/?.*'
)
EFFECT_LOCATION_RE = re.compile(r'(/composition/.*/effects)/(\d+)/?.*')
EFFECT_CONTAINER_RE = re.compile(r'(/composition/.*/effects)/?.*')
DECK_ID_RE = re.compile(r'/composition/decks/(\d+)')
LAYER_ID_RE = re.compile(r'/(?:composition|selecteddeck)/layers/(\d+)')
CLIP_ID_RE = re.compile(r'/composition/clips/(\d+)')
EXPAND_FROM_ID_RE = re.compile( # /layer/1 -> /layer/layer1
	r'(layer|clip|deck|effect)s/([\d]+)'
)
COLLAPSE_TO_ID_RE = re.compile( # /layer/layer1 -> /layer/1
	r'/(layer|clip|deck|effect)s/(layer|clip|deck|effect)(\d+)'
)

# TODO: covert to typed version
EffectLocation = namedtuple('EffectLocation', ['containerAddress', 'effectID'])


class DeckLocation(NamedTuple):
	layerNmber: int
	columnNumber: int


def intIfSet(stringNumber):  # noqa: ANN001
	# NOTE: the == 0 check is to support touch table cells with a value of 0
	return int(stringNumber) if stringNumber or stringNumber == 0 else None


def layoutComps(compList, columns=4, xBase=0):  # noqa: ANN001
	# TODO: use TDF.arrangeNode instead
	# TODO: should we skip if ui.performMode == False?
	for i, comp in enumerate(compList):
		comp.nodeX = xBase + (i % columns) * 200
		comp.nodeY = (1 + math.floor(i / columns)) * -200


def layoutChildren(op, columns=4):  # noqa: ANN001
	children = op.findChildren(depth=1)
	layoutComps(children, columns)


def getCellValues(datRow) -> list[str]:  # noqa: ANN001
	return [cell.val for cell in datRow]


def clearChildren(op, exclude=None):  # noqa: ANN001
	if not exclude:
		exclude = []

	for child in op.findChildren(depth=1):
		if child.path not in exclude:
			child.destroy()


def syncToDat(data, targetDat):  # noqa: ANN001
	if data is None:
		targetDat.clear()
		return

	rowCount = len(data)
	columnCount = len(data[0]) if rowCount > 0 else 0
	targetDat.setSize(rowCount, columnCount)

	for rowIndex, row in enumerate(data):
		for columnIndex, cell in enumerate(row):
			targetDat[rowIndex, columnIndex] = cell or ''


def mapAddressToDeckLocation(address: str) -> DeckLocation:
	m = re.match(SELECTED_DECK_LOCATION_RE, address)
	assert m, f'expected to match layer and clip number in {address}'

	return DeckLocation(int(m.group(1)), int(m.group(2)))


def mapAddressToEffectLocation(address: str) -> EffectLocation:
	m = re.match(EFFECT_LOCATION_RE, address)
	assert m, f'expected to match effect container and effect ID in {address}'

	return EffectLocation(containerAddress=m.group(1), effectID=int(m.group(2)))


def mapAddressToEffectContainer(address: str) -> str:
	m = re.match(EFFECT_CONTAINER_RE, address)
	assert m, f'expected to match effect container in {address}'

	return m.group(1)


def getDeckID(address):  # noqa: ANN001
	m = re.match(DECK_ID_RE, address)
	assert m, f'expected to match deck id in {address}'

	return int(m.group(1))


def getLayerID(address):  # noqa: ANN001
	m = re.match(LAYER_ID_RE, address)
	assert m, f'expected to match layer id in {address}'

	return int(m.group(1))


def getClipID(address):  # noqa: ANN001
	m = re.match(CLIP_ID_RE, address)
	assert m, f'expected to match clip id in {address}'

	return int(m.group(1))


def addressToValueLocation(address, compositionPath):  # noqa: ANN001
	"""
	from: /composition/layers/1/...
	to  : /composition/layers/layer1/...
	"""

	fullPath = EXPAND_FROM_ID_RE.sub(r'\1s/\1\2', address)

	return tuple(fullPath.replace('/composition', compositionPath).rsplit('/', 1))


def addressToToxPath(address, compositionPath):  # noqa: ANN001
	(container, el) = addressToValueLocation(address, compositionPath)
	path = f'{container}/{el}'

	return path if path.endswith('/tox') else f'{path}/tox'


def parameterPathToAddress(path: str, parameter: str):
	"""
	from: /tdArena/composition/layers/layer1/...
	from: /tdArena/render/composition/layers/layer1/...
	to  : /composition/layers/1/...:parameter
	"""
	compositionStart = path.find('/composition')
	address = COLLAPSE_TO_ID_RE.sub(r'/\1s/\3', path[compositionStart:])

	return f'{address}:{parameter}'


def addressToExport(address):  # noqa: ANN001
	(path, prop) = addressToValueLocation(address, '')
	return f'{path.lstrip("/")}:{prop}'


def exportToAddress(exportName):  # noqa: ANN001
	(path, prop) = exportName.split(':')

	address = COLLAPSE_TO_ID_RE.sub(r'/\1s/\3', f'/composition/{path}')

	return f'{address}/{prop}'


def addSectionParameters(
	op,  # noqa: ANN001
	order: int,
	name: str,
	opacity: Optional[float] = None
):
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


def resetCustomParameters(
	operator,  # noqa: ANN001
	checkDefaultExpr=False  # noqa: ANN001, FBT002
):
	for p in operator.customPars:
		# There's some weird cases where the defaultExpr is string 'None'
		# Ignore those when using the expr. Specifically, I noticed this
		# on old Toggle custom parameters
		if checkDefaultExpr and p.defaultExpr and p.defaultExpr != 'None':
			p.expr = p.defaultExpr
			p.mode = ParMode.EXPRESSION
		else:
			p.val = p.default
			p.mode = ParMode.CONSTANT


# TODO(#48): apply to clip names
def filePathToName(path: str) -> str:
	stem = PureWindowsPath(path).stem.replace('-', ' ').replace('_', ' ')
	return re.sub(r'(\w)([A-Z])', r'\1 \2', stem).title()


def filePathToStemSlug(path: str) -> str:
	return PureWindowsPath(path).stem.replace('-', '_').replace(' ', '_')


def matchesGlob(globStr: str, path: str) -> bool:
	return next(
		(True for glob in globStr.split(',') if fnmatchcase(path, glob)),
		False  # noqa: FBT003
	)
