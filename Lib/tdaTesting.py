from unittest.mock import MagicMock


class MockCell:

	def __init__(self, val: str, row: int, col: int):
		self.val = val
		self.row = row
		self.col = col

	def __str__(self) -> str:
		return str(self.val)


def createMockRow(rowNumber, rowData):  # noqa: ANN001
	return [
		MockCell(val, rowNumber, colNumber) for colNumber, val in enumerate(rowData)
	]


class MockTable:

	def __init__(self, rows):  # noqa: ANN001
		self._rowData = [createMockRow(i, r) for i, r in enumerate(rows)]

	def __getitem__(self, pos):  # noqa: ANN001
		rowIndex, colIndex = pos

		if not isinstance(colIndex, int):
			colIndex = self._colIndexByName(colIndex)
			if colIndex is None:
				return None

		row = self.row(rowIndex)
		if row is None:
			return None

		return row[colIndex]

	@property
	def numRows(self):
		return len(self._rowData)

	def rows(self):
		return self._rowData

	def _colIndexByName(self, name):  # noqa: ANN001, ANN202
		if len(self._rowData) == 0:
			return None

		headingRow = self._rowData[0]
		for i, cell in enumerate(headingRow):
			if cell.val == name:
				return i

		return None

	def _rowIndexByName(self, name):  # noqa: ANN001, ANN202
		for i, row in enumerate(self._rowData):
			if row[0].val == name:
				return i

		return None

	def row(self, index):  # noqa: ANN001
		if isinstance(index, int):
			try:
				return self._rowData[index]
			except IndexError:
				return None

		foundIndex = self._rowIndexByName(index)
		return self._rowData[foundIndex] if foundIndex is not None else None

	def appendRow(self, cells: list):
		self._rowData.append(createMockRow(len(self._rowData), cells))

	def appendRows(self, rows: list):
		for row in rows:
			self.appendRow(row)

	def deleteRow(self, index):  # noqa: ANN001
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


class MockOP(MagicMock):

	def __init__(self) -> None:
		super().__init__()
		self.paths = {}

		self.side_effect = self.resolve

	def addPath(self, path, instance):  # noqa: ANN001
		instance.path = path
		self.paths[path] = instance

	def resolve(self, path):  # noqa: ANN001
		if path not in self.paths:
			self.addPath(path, MagicMock())

		return self.paths[path]


class MockParameter:

	def __init__(self, val) -> None:  # noqa: ANN001
		self._val = val

	def eval(self):
		return self._val


class MockParameterBag:

	def __init__(self, pars):  # noqa: ANN001
		self._parameters = pars

	def __getattr__(self, attr):  # noqa: ANN001
		if attr not in self._parameters:
			raise AttributeError

		return self._parameters[attr]

	# TODO: __setattr__, if not MockParameter, coerce to class
