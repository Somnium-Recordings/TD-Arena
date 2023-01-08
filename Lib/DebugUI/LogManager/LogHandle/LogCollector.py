import math
from collections import namedtuple
from typing import List, Optional, Union

from tda import Cell
from tdaUtils import getCellValues

# NOTE: message needs to stay first for search/matching to work correctly
LogRecord = namedtuple(
	'LogRecord', [
		'message', 'source', 'absframe', 'frame', 'severity', 'type', 'timestamp',
		'count'
	]
)
LOG_STORAGE_COLS = LogRecord._fields


def getLogVal(row: List[Cell], col: str) -> str:
	return row[LOG_STORAGE_COLS.index(col)].val


def setLogVal(row: List[Cell], col: str, val: str) -> None:
	row[LOG_STORAGE_COLS.index(col)].val = val


def rowToLogRecord(row: List[Cell], rowCols: List[str]) -> LogRecord:
	return LogRecord._make(
		[
			# TODO: if this is slow, maybe cache the column map
			row[rowCols.index(colName)].val if colName in rowCols else ''
			for colName in LOG_STORAGE_COLS
		]
	)


class LogCollector:
	@property
	def lastCollectedFrame(self) -> int:
		return self.ownerComp.par.Lastcollectedframe.eval()

	@lastCollectedFrame.setter
	def lastCollectedFrame(self, val: Union[int, float]) -> int:
		self.ownerComp.par.Lastcollectedframe = 0 if math.isinf(val) else int(val)

	# TODO: clear logs on first load
	def __init__(self, ownerComp) -> None:
		self.ownerComp = ownerComp
		self.logStorage = ownerComp.op('table_logStorage')
		self.unprocessedLogs = ownerComp.op('null_unprocessedLogs')
		self.onLogChangeHandler = ownerComp.op('datexec_onLogChange')

		self.Reset()

	def Reset(self) -> None:
		self.logStorage.clear()
		self.logStorage.appendRow(LOG_STORAGE_COLS)

		self.lastCollectedFrame = 0
		self.ProcessLogChange(self.unprocessedLogs)

		# activate onLogChange dat execute in case log processing resulted in it
		# getting turned off previously
		self.onLogChangeHandler.par.active = 1

	def ProcessLogChange(self, dat) -> None:
		if dat.numRows == 0:
			return

		headerRow: Cell
		logRows: List[Cell]
		headerRow, *logRows = dat.rows()
		logColumns = getCellValues(headerRow)

		# TODO: Error if missing critical columns like message, source or absframe

		# Treat "0" as negative infinity so we can display negative frames
		# (e.g. frames from previous sessions)
		highestCollectedFrame = self.lastCollectedFrame or float('-inf')

		for logRow in logRows:
			logRecord = rowToLogRecord(logRow, logColumns)

			logFrame = int(logRecord.absframe)
			# If the frame number is higher than the current frame, the log is from
			# a past session. Convert it to a negative number so that it doesn't prevent
			# future logs from being read.
			if logFrame > absTime.frame + 1:
				logFrame = -logFrame
				logRecord = logRecord._replace(absframe=logFrame)

			highestCollectedFrame = max(self.lastCollectedFrame, logFrame)
			self.processLogRecord(logRecord)

		# We need to wait to update the lastCollectedFrame until after
		# we have finished processing all the records. If we do it after
		# the first record, the filter will kick in and we won't be able
		# to access the table data for the remaining records
		self.lastCollectedFrame = highestCollectedFrame

	def processLogRecord(self, logRecord: LogRecord) -> None:
		log = self.findMatchingLog(logRecord)

		if log is None:
			self.logStorage.appendRow(logRecord)
		else:
			logCount = int(getLogVal(log, 'count') or '1')
			setLogVal(log, 'count', logCount + 1)
			setLogVal(log, 'timestamp', logRecord.timestamp)
			setLogVal(log, 'absframe', logRecord.absframe)
			setLogVal(log, 'frame', logRecord.frame)

	def findMatchingLog(self, logRecord: LogRecord) -> Optional[int]:
		return next(
			(
				log for log in self.logStorage.rows(logRecord.message)
				# TODO: should we also match severity?
				# TODO: should we just make the "matched props" dynamic?
				if getLogVal(log, 'source') == logRecord.source
			),
			None
		)
