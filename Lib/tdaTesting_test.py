# pylint: disable=too-few-public-methods,too-many-arguments
import pytest
from tdaTesting import MockCell, MockTable


class TestMockCell:

	def test_toString(self):
		testCell = MockCell('foo', 0, 1)
		assert str(testCell) == 'foo'


class TestMockTable:

	@pytest.fixture
	def testTable(self):
		return MockTable([
			['0-0', '0-1'],
			['1-0', '1-1'],
		])

	def test_row(self, testTable: MockTable):
		assert str(testTable.row(0)[0]) == '0-0'
		assert str(testTable.row('1-0')[1]) == '1-1'

	def test_appendRow(self, testTable: MockTable):
		assert testTable.numRows == 2

		testTable.appendRow(['2-0', '2-1'])
		assert testTable.numRows == 3

		testTable.appendRows([['3-0', '3-1'], ['4-0', '4-1']])
		assert testTable.numRows == 5
		assert testTable.row(4)[0].val == '4-0'

	def test_deleteRow(self, testTable: MockTable):
		testTable.deleteRow(0)
		assert testTable.row(0)[0].val == '1-0'
		assert testTable.row(0)[0].row == 0

		testTable.deleteRow('1-0')
		assert testTable.numRows == 0

		with pytest.raises(IndexError):
			testTable.deleteRow(0)

	def test_clear(self, testTable: MockTable):
		testTable.clear()
		assert testTable.numRows == 0

	def test_getItem(self, testTable: MockTable):
		assert testTable[1, 0].val == '1-0'
		assert testTable['1-0', 1].val == '1-1'
		assert testTable['1-0', '0-1'].val == '1-1'
		assert testTable['1-0', 'invalid'] is None
		assert testTable['invalid', 'invalid'] is None
		assert testTable[99, '0-1'] is None
