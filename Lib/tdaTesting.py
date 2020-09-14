# pylint: disable=too-few-public-methods
from unittest.mock import MagicMock


class Mockcell:
	def __init__(self, val: str, row: int, col: int):
		self.val = val
		self.row = row
		self.col = col


def createMockRow(rowNumber, rowData):
	return [
		Mockcell(val, rowNumber, colNumber) for colNumber, val in enumerate(rowData)
	]


class MockTable:
	"""
	TODO: should probably add some basic tests for this
	"""
	def __init__(self, rows):
		self._rowData = [createMockRow(i, r) for i, r in enumerate(rows)]

	def rows(self):
		return self._rowData

	def _rowIndexByName(self, name):
		for i, row in enumerate(self._rowData):
			if row[0].val == name:
				return i

		return None

	def row(self, index):
		if isinstance(index, int):
			return self._rowData[index]

		foundIndex = self._rowIndexByName(index)
		return self._rowData[foundIndex] if foundIndex is not None else None

	def appendRow(self, cells: list):
		self._rowData.append(createMockRow(len(self._rowData), cells))

	def appendRows(self, rows: list):
		for row in rows:
			self.appendRow(row)

	def deleteRow(self, index):
		if isinstance(index, int):
			del self._rowData[index]
		else:
			foundIndex = self._rowIndexByName(index)
			if foundIndex is None:
				raise IndexError
			del self._rowData[foundIndex]

		for rowNumber, row in enumerate(self._rowData):
			for cell in row:
				cell.row = rowNumber

	def clear(self):
		self._rowData = []


def mockOp():
	paths = {}
	op = MagicMock()

	def addPath(path, instance):
		instance.path = path
		paths[path] = instance

	op.addPath = addPath

	def resolve(path):
		if path not in paths:
			paths[path] = MagicMock()
			paths[path].path = path

		return paths[path]

	op.side_effect = resolve

	return op
