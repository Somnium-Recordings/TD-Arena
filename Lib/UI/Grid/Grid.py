from functools import reduce

from tda import BaseExt
from tdaUtils import layoutComps

DIRECTIONS = ('l', 'r', 'b', 't')
OPPOSITE_DIRECTIONS = {'l': 'r', 'r': 'l', 't': 'b', 'b': 't'}


def nextID(ops):
	return reduce(lambda acc, op: max(acc, op.digits), ops, -1) + 1


def setDivider(op, direction, divider):
	# TODO:  Remove unnecessary getattr, access by index instead
	getattr(op.par, f'Divider{direction}').val = divider.name if divider else ''


def getDivider(op, direction):
	return getattr(op.par, f'Divider{direction}').eval()


def nameIfSet(op):
	return op.name if op else str(op)


def findAdjacentToDivider(
	searchCollection, targetDivider, direction, exclude=None
):
	return [
		x for x in searchCollection
		if getDivider(x, direction) == targetDivider and x not in (exclude or [])
	]


class Grid(BaseExt):
	def __init__(self, ownerComponent, logger):
		super().__init__(ownerComponent, logger)
		self.Init()

	def Init(self):
		self.cellTemplate = self.ownerComponent.op('cellTemplate')
		self.cells = self.ownerComponent.findChildren(name='cell[0-999]')

		self.vDividerTemplate = self.ownerComponent.op('vDividerTemplate')
		self.vDividers = self.ownerComponent.findChildren(name='vDivider[0-999]')
		self.hDividerTemplate = self.ownerComponent.op('hDividerTemplate')
		self.hDividers = self.ownerComponent.findChildren(name='hDivider[0-999]')

		if not self.ownerComponent.op('cell0'):
			self.createNextCell()

		self.logInfo('initalized')

	def Reset(self):
		self.Init()
		for cell in self.cells:
			cell.destroy()

		for divider in self.vDividers:
			divider.destroy()

		for divider in self.hDividers:
			divider.destroy()

		self.Init()

	def AddCell(self, baseCell, targetDirection: str):
		# TODO: this is obnoxious to follow, just use 4 if/else statemetns
		# TODO: If new anchor is not within repositionxmin, reject new division
		# TODO: Support adding cell to a divider instead of a cell
		# TODO: derive min/max cell size from contents
		# TODO: allow "non-stackable" cells: during init, each gets is own cell that can't be deleted
		# TODO: save/load "layouts"

		assert targetDirection in DIRECTIONS, f'invalid direction requested {targetDirection}'
		oppositeDirection = OPPOSITE_DIRECTIONS[targetDirection]

		targetDivider = getDivider(baseCell, targetDirection)
		oppositeDivider = getDivider(baseCell, oppositeDirection)

		newDivider = self.AddDivider(targetDivider, oppositeDivider, targetDirection)

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

		self.logInfo(
			f'splitting cell {baseCell.digits} to the {targetDirection} with {nameIfSet(newDivider)}'
		)

	# TODO: this code is awful, clean up before merge
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

	def createNextCell(self):
		nextCellID = nextID(self.cells)
		cell = self.ownerComponent.copy(self.cellTemplate, name=f'cell{nextCellID}')
		cell.par.display = 1

		self.cells.append(cell)
		layoutComps(self.cells, columns=1)

		return cell

	def createNextVDivider(self):
		nextDividerID = nextID(self.vDividers)
		template = self.vDividerTemplate
		divider = self.ownerComponent.copy(template, name=f'vDivider{nextDividerID}')
		divider.par.display = 1

		self.vDividers.append(divider)
		layoutComps(self.vDividers, columns=1, xBase=200)

		return divider

	def createNextHDivider(self):
		nextDividerID = nextID(self.hDividers)
		template = self.hDividerTemplate
		divider = self.ownerComponent.copy(template, name=f'hDivider{nextDividerID}')
		divider.par.display = 1

		self.hDividers.append(divider)
		layoutComps(self.hDividers, columns=1, xBase=400)

		return divider
