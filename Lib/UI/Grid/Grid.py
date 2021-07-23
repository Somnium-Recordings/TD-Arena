import json
from functools import reduce
from os import path

from tda import DroppedItem, LoadableExt
from tdaUtils import getCellValues, layoutComps

DIRECTIONS = ('l', 'r', 'b', 't')
OPPOSITE_DIRECTIONS = {'l': 'r', 'r': 'l', 't': 'b', 'b': 't'}


def nextID(ops):
	return reduce(lambda acc, op: max(acc, op.digits), ops, -1) + 1


def setDivider(op, direction, divider=None, dividerName=None):
	if dividerName is None:
		dividerName = divider.name if divider else ''
	op.par[f'Divider{direction}'].val = dividerName


def getDivider(op, direction):
	return op.par[f'Divider{direction}'].eval()


def nameIfSet(op):
	return op.name if op else str(op)


def findAdjacentToDivider(
	searchCollection, targetDivider, direction, exclude=None
):
	return [
		x for x in searchCollection
		if getDivider(x, direction) == targetDivider and x not in (exclude or [])
	]


def setDividerReferences(element, layoutSpec):
	if layoutSpec['l'] is not None:
		setDivider(element, 'l', dividerName=f'vDivider{layoutSpec["l"]}')
	if layoutSpec['r'] is not None:
		setDivider(element, 'r', dividerName=f'vDivider{layoutSpec["r"]}')
	if layoutSpec['b'] is not None:
		setDivider(element, 'b', dividerName=f'hDivider{layoutSpec["b"]}')
	if layoutSpec['t'] is not None:
		setDivider(element, 't', dividerName=f'hDivider{layoutSpec["t"]}')


# yapf: disable
# pylint: disable=bad-whitespace
DEFAULT_LAYOUT = {
	'cells': [
		{'id': 0, 'l': None, 'r': 2,    'b': None, 't': 0   },
		{'id': 1, 'l': None, 'r': 0,    'b': 0,    't': None},
		{'id': 2, 'l': 0,    'r': 1,    'b': 0,    't': None},
		{'id': 3, 'l': 1,    'r': None, 'b': 0,    't': None},
		{'id': 4, 'l': 2,    'r': None, 'b': None, 't': 0   },
	],
	'vDividers': [
		{'id': 0, 'l': None, 'r': 1,    'b': 0,    't': None, 'pos': 0.35},
		{'id': 1, 'l': 0,    'r': None, 'b': 0,    't': None, 'pos': 0.7161},
		{'id': 2, 'l': None, 'r': None, 'b': None, 't': 0,    'pos': 0.7161},
	],
	'hDividers': [
		{'id': 0, 'l': None, 'r': None, 'b': None, 't': None, 'pos': 0.3902},
	],
	'panelMap': [
		['path',                                           'cellID', 'order'],
		['/tdArena/ui/assetBrowserUI/browserUI_movie',     3,        1],
		['/tdArena/ui/assetBrowserUI/browserUI_generator', 3,        2],
		['/tdArena/ui/assetBrowserUI/browserUI_effect',    3,        3],
		['/tdArena/ui/parametersUI/selectedLayer',         1,        1],
		['/tdArena/ui/parametersUI/selectedClip',          2,        0],
		['/tdArena/ui/parametersUI/composition',           1,        0],
		['/tdArena/ui/previs',                             3,        0],
		['/tdArena/ui/clipLauncherUI',                     0,        0],
		['/tdArena/ui/audioAnalysis',                      4,        0]
	]
}
# yapf: enable


def dividerState(par):
	targetOp = par.eval()

	return targetOp.digits if targetOp else None


def getOpSaveState(op, posPar=None):
	state = {
		'id': op.digits,
		'l': dividerState(op.par.Dividerl),
		'r': dividerState(op.par.Dividerr),
		'b': dividerState(op.par.Dividerb),
		't': dividerState(op.par.Dividert),
	}

	if posPar:
		state['pos'] = op.par[posPar].eval()

	return state


def layoutFilePath(layoutName):
	return tdu.expandPath(path.join('.td-arena', f'layout.{layoutName}.json'))


def layoutExists(layoutName):
	return path.isfile(layoutFilePath(layoutName))


class Grid(LoadableExt):
	@property
	def layoutUserSetting(self):
		return self.userSettings.par.Gridlayout.eval()

	@layoutUserSetting.setter
	def layoutUserSetting(self, value):
		self.userSettings.par.Gridlayout = value

	def __init__(self, ownerComponent, logger, userSettings):
		super().__init__(ownerComponent, logger)
		self.userSettings = userSettings

		self.Init()

	def Init(self):
		self.cellTemplate = self.ownerComponent.op('cellTemplate')
		self.cells = self.ownerComponent.findChildren(name='cell[0-999]')

		self.vDividerTemplate = self.ownerComponent.op('vDividerTemplate')
		self.vDividers = self.ownerComponent.findChildren(name='vDivider[0-999]')
		self.hDividerTemplate = self.ownerComponent.op('hDividerTemplate')
		self.hDividers = self.ownerComponent.findChildren(name='hDivider[0-999]')
		self.constants = self.ownerComponent.op('constant1')
		self.constants.par.value0 = 0
		self.constants.par.value1 = 1

		self.panelMapTable = self.ownerComponent.op('table_panelMap')
		self.cellPanelState = self.ownerComponent.op('table_cellPanelState')

		if self.ownerComponent.op('cell0'):
			self.setLoaded()
		else:
			self.loadLayout()

		self.logInfo('initalized')

	def SelectLayout(self, layoutName):
		self.logInfo(f'selecting layout {layoutName}')
		self.Unload()

		self.layoutUserSetting = '' if layoutName == 'Default' else layoutName

		self.Init()

	def loadLayoutFile(self, layoutName):
		if layoutName == 'Default':
			return DEFAULT_LAYOUT

		try:
			with open(layoutFilePath(layoutName)) as saveFile:
				return json.load(saveFile)
		except (json.JSONDecodeError, FileNotFoundError):
			self.logError(
				f'no layout file found at {layoutFilePath(layoutName)}, '
				'loading default instead'
			)
			return DEFAULT_LAYOUT

	def loadLayout(self, layout=None):
		self.setLoading()
		layout = self.loadLayoutFile(self.layoutUserSetting)

		for spec in layout['vDividers']:
			divider = self.createNextVDivider(spec['id'])
			setDividerReferences(divider, spec)
			divider.par.rightanchor = spec['pos']

		for spec in layout['hDividers']:
			divider = self.createNextHDivider(spec['id'])
			setDividerReferences(divider, spec)
			divider.par.topanchor = spec['pos']

		for spec in layout['cells']:
			setDividerReferences(self.createNextCell(spec['id']), spec)

		panelMap = layout['panelMap']
		self.panelMapTable.appendRows(panelMap, 0)
		self.panelMapTable.setSize(len(panelMap), len(panelMap[0]))
		self.setLoaded()

	# pylint: disable=no-self-use
	def GetAvailableLayouts(self):
		layouts = ['Default']

		# TODO: figure out why rowCallback isn't fired every time
		# if self.layoutExists('User'):
		layouts.append('User')

		return layouts

	def SaveLayout(self):
		if not self.Loaded:
			self.logError('cannot save layout, grid has not been loaded')
			return

		self.logInfo('saving user layout')

		saveState = {
			'cells': [getOpSaveState(cell) for cell in self.cells],
			'vDividers':
			[getOpSaveState(divider, 'rightanchor') for divider in self.vDividers],
			'hDividers':
			[getOpSaveState(divider, 'topanchor') for divider in self.hDividers],
			'panelMap': [getCellValues(row) for row in self.panelMapTable.rows()]
		}

		saveFilePath = layoutFilePath('User')
		with open(saveFilePath, 'w') as saveFile:
			json.dump(saveState, saveFile, indent='\t')

		self.logDebug(f'layout saved to {saveFilePath }')

	def Unload(self):
		self.setUnloaded()

		for cell in self.cells:
			if cell.valid:
				cell.destroy()

		for divider in self.vDividers:
			if divider.valid:
				divider.destroy()

		for divider in self.hDividers:
			if divider.valid:
				divider.destroy()

	def Reset(self):
		self.Init()
		self.Unload()
		self.Init()

	def AddCell(
		self, baseCell, targetDirection: str, droppedItem: DroppedItem = None
	):
		# TODO(#55): this is obnoxious to follow, just use 4 if/else statemetns
		# TODO(#55): If new anchor is not within repositionxmin, reject new division
		# TODO(#55): Support adding cell to a divider instead of a cell
		# TODO(#55): derive min/max cell size from contents
		# TODO(#55): allow 'non-stackable" cells: during init, each gets is own cell that can't be deleted
		# TODO(#54): save/load "layouts"

		assert targetDirection in DIRECTIONS, f'invalid direction requested {targetDirection}'
		oppositeDirection = OPPOSITE_DIRECTIONS[targetDirection]

		targetDivider = getDivider(baseCell, targetDirection)
		oppositeDivider = getDivider(baseCell, oppositeDirection)

		newDivider = self.AddDivider(targetDivider, oppositeDivider, targetDirection)

		self.logInfo(
			f'splitting cellID {baseCell.digits} to the {targetDirection} with {nameIfSet(newDivider)}'
		)

		newCell = self.createNextCell()
		setDivider(newCell, oppositeDirection, newDivider)
		setDivider(newCell, targetDirection, targetDivider)

		setDivider(baseCell, targetDirection, newDivider)

		if targetDirection in ('b', 't'):
			setDivider(newDivider, 'l', getDivider(baseCell, 'l'))
			setDivider(newDivider, 'r', getDivider(baseCell, 'r'))
			setDivider(newCell, 'l', getDivider(baseCell, 'l'))
			setDivider(newCell, 'r', getDivider(baseCell, 'r'))
		else:
			setDivider(newDivider, 'b', getDivider(baseCell, 'b'))
			setDivider(newDivider, 't', getDivider(baseCell, 't'))
			setDivider(newCell, 'b', getDivider(baseCell, 'b'))
			setDivider(newCell, 't', getDivider(baseCell, 't'))

		self.logInfo(f'new cellID {newCell.digits} created')

		if droppedItem:
			self.MovePanelIntoCell(newCell, droppedItem)

	def MovePanelIntoCell(self, targetCell, droppedItem: DroppedItem):
		itemHeadingOp = op(droppedItem.itemPath)
		sourceCellPanelsDat = itemHeadingOp.parent.cell.op('./null_cellPanels')
		targetCellPanelsDat = targetCell.op('./null_cellPanels')
		panelPath = sourceCellPanelsDat[itemHeadingOp.digits + 1, 'path'].val

		self.logInfo(
			(
				f'moving panel {panelPath} into cellID {targetCell.digits}',
				f' at index {droppedItem.selectedItemIndex}'
			)
		)
		self.panelMapTable[panelPath, 'cellID'] = targetCell.digits

		# Move path to requested index in sibling panel order
		# NOTE: this dat is already sorted by the `order` column
		panelPaths = [c.val for c in targetCellPanelsDat.col('path')[1:]]
		if panelPath in panelPaths:
			panelPaths.remove(panelPath)
		panelPaths.insert(droppedItem.selectedItemIndex, panelPath)
		for index, value in enumerate(panelPaths):
			self.panelMapTable[value, 'order'] = index

		self.RemoveEmptyCells()

	def RemoveEmptyCells(self):
		mappedCellIDs = {int(c.val) for c in self.panelMapTable.col('cellID')[1:]}
		for cell in self.cells:
			if cell.digits not in mappedCellIDs:
				self.logInfo(f'removing empty cellID {cell.digits}')
				self.RemoveCell(cell)

	# pylint: disable=too-many-branches,too-many-statements
	def AddDivider(self, targetDivider, oppositeDivider, direction):
		if direction == 'r':
			newDivider = self.createNextVDivider()
			targetX = 1
			oppositeX = 0
			if targetDivider:
				targetX = targetDivider.par.rightanchor.eval()
				setDivider(newDivider, 'r', targetDivider)
				setDivider(targetDivider, 'l', newDivider)
			if oppositeDivider:
				oppositeX = oppositeDivider.par.rightanchor.eval()
				setDivider(newDivider, 'l', oppositeDivider)
				setDivider(oppositeDivider, 'r', newDivider)
			newDivider.par.rightanchor = (targetX + oppositeX) / 2
		elif direction == 'l':
			newDivider = self.createNextVDivider()
			targetX = 0
			oppositeX = 1
			if targetDivider:
				targetX = targetDivider.par.rightanchor.eval()
				setDivider(newDivider, 'l', targetDivider)
				setDivider(targetDivider, 'r', newDivider)
			if oppositeDivider:
				oppositeX = oppositeDivider.par.rightanchor.eval()
				setDivider(newDivider, 'r', oppositeDivider)
				setDivider(oppositeDivider, 'l', newDivider)
			newDivider.par.rightanchor = (targetX + oppositeX) / 2
		elif direction == 'b':
			newDivider = self.createNextHDivider()
			targetY = 0
			oppositeY = 1
			if targetDivider:
				targetY = targetDivider.par.topanchor.eval()
				setDivider(newDivider, 'b', targetDivider)
				setDivider(targetDivider, 't', newDivider)
			if oppositeDivider:
				oppositeY = oppositeDivider.par.topanchor.eval()
				setDivider(newDivider, 't', oppositeDivider)
				setDivider(oppositeDivider, 'b', newDivider)
			newDivider.par.topanchor = (targetY + oppositeY) / 2
		elif direction == 't':
			newDivider = self.createNextHDivider()
			targetY = 1
			oppositeY = 0
			if targetDivider:
				targetY = targetDivider.par.topanchor.eval()
				setDivider(newDivider, 't', targetDivider)
				setDivider(targetDivider, 'b', newDivider)
			if oppositeDivider:
				oppositeY = oppositeDivider.par.topanchor.eval()
				setDivider(newDivider, 'b', oppositeDivider)
				setDivider(oppositeDivider, 't', newDivider)
			newDivider.par.topanchor = (targetY + oppositeY) / 2
		else:
			raise NotImplementedError(
				f'creating dividers in the direction "{direction}" not supported'
			)

		return newDivider

	def RemoveCell(self, cell):
		if len(self.cells) <= 1:
			self.logWarning('cannot remove the last cell of the grid')
			return

		for direction in DIRECTIONS:
			cellDivider = getDivider(cell, direction)
			if not cellDivider:
				continue

			dividersToCheck = self.vDividers if direction in ('b', 't') else self.hDividers #yapf:disable
			elementsSharingDivider = findAdjacentToDivider(
				dividersToCheck + self.cells, cellDivider, direction, exclude=[cell]
			)
			if elementsSharingDivider:
				continue

			oppositeDirection = OPPOSITE_DIRECTIONS[direction]
			cellOppositeDivider = getDivider(cell, oppositeDirection)
			for elementToUpdate in findAdjacentToDivider(
				self.cells + self.vDividers + self.hDividers,
				cellDivider,
				oppositeDirection,
				exclude=[cell]
			):
				self.logDebug(
					f'updating {elementToUpdate.name}:{oppositeDirection} -> {nameIfSet(cellOppositeDivider)}'
				)
				setDivider(elementToUpdate, oppositeDirection, cellOppositeDivider)

			if cellOppositeDivider and getDivider(
				cellOppositeDivider, direction
			) == cellDivider:
				closest = self.closestDividerTo(
					cellOppositeDivider, direction, exclude=[cellDivider]
				)
				self.logDebug(
					f'updating {cellOppositeDivider.name}:{direction} -> closest ({nameIfSet(closest)})'
				)
				setDivider(cellOppositeDivider, direction, closest)

			self.logDebug(
				f'destroying {cell.name}:{direction} -> {nameIfSet(cellDivider)}'
			)
			setDivider(cell, direction, None)
			if cellDivider.name.startswith('vDivider'):
				self.vDividers.remove(cellDivider)
			else:
				self.hDividers.remove(cellDivider)
			cellDivider.destroy()

		self.logInfo(f'destroying {cell.name}')
		cell.destroy()
		self.cells.remove(cell)

	def OnDividerClick(self, divider):
		if divider.name.startswith('vDivider'):
			directions = ('l', 'r')
		else:
			directions = ('b', 't')

		for direction in directions:
			closestDivider = self.closestDividerTo(divider, direction)
			if closestDivider and closestDivider != getDivider(divider, direction):
				self.logDebug(
					f'updating {divider.name}:{direction} -> closest ({nameIfSet(closestDivider)})'
				)
				setDivider(divider, direction, closestDivider)

	def closestDividerTo(self, divider, direction, exclude=None):
		adjacent = findAdjacentToDivider(
			self.vDividers if divider.name.startswith('vDivider') else self.hDividers,
			divider, OPPOSITE_DIRECTIONS[direction], exclude
		)
		if not adjacent:
			return None

		pos = 'x' if direction in ('l', 'r') else 'y'
		if direction in ('l', 'b'):
			isCloser = lambda d1, d2: getattr(d1, pos) > getattr(d2, pos)
		else:
			isCloser = lambda d1, d2: getattr(d1, pos) < getattr(d2, pos)

		return reduce(lambda d1, d2: d1 if isCloser(d1, d2) else d2, adjacent)

	def createNextCell(self, cellID=None):
		if cellID is None:
			cellID = nextID(self.cells)
		cell = self.ownerComponent.copy(self.cellTemplate, name=f'cell{cellID}')
		cell.par.display = 1

		self.cells.append(cell)
		layoutComps(self.cells, columns=1)

		return cell

	def createNextVDivider(self, dividerID=None):
		if dividerID is None:
			dividerID = nextID(self.vDividers)
		template = self.vDividerTemplate
		divider = self.ownerComponent.copy(template, name=f'vDivider{dividerID}')
		divider.par.display = 1

		self.vDividers.append(divider)
		layoutComps(self.vDividers, columns=1, xBase=200)

		return divider

	def createNextHDivider(self, dividerID=None):
		if dividerID is None:
			dividerID = nextID(self.hDividers)
		template = self.hDividerTemplate
		divider = self.ownerComponent.copy(template, name=f'hDivider{dividerID}')
		divider.par.display = 1

		self.hDividers.append(divider)
		layoutComps(self.hDividers, columns=1, xBase=400)

		return divider
