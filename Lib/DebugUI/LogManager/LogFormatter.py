# pylint: disable=too-many-locals
# me - this DAT
# scriptOp - the OP which is cooking
#
# press 'Setup Parameters' in the OP to call this function to re-create the parameters.
import re
from codecs import decode
from typing import List

TIME_RE = re.compile(r'\d\d:\d\d:\d\d(,\d\d\d)?')

SEVERITY_REMAP = {'ABORT': 'ERROR'}


def onSetupParameters(_scriptOp):
	# page = scriptOp.appendCustomPage('Custom')
	# p = page.appendFloat('Valuea', label='Value A')
	# p = page.appendFloat('Valueb', label='Value B')
	pass


# called whenever custom pulse parameter is pushed
def onPulse(_par):
	pass


LogSource = List[str]


def justifyColumns(rows: List[LogSource]) -> List[str]:
	justifiedColumns = []

	for column in zip(*rows):
		maxWidth = len(max(column, key=len))
		justifiedColumns.append([c.ljust(maxWidth) for c in column])

	return [' '.join(filter(len, row)) for row in zip(*justifiedColumns)]


class GroupedLogCollector:
	def __init__(self) -> None:
		self.storage = {}

	def add(self, message: str, sourceParts: LogSource) -> None:
		if message in self.storage:
			self.storage[message].append(sourceParts)
		else:
			self.storage[message] = [sourceParts]

	def items(self):
		return self.storage.items()


class UngroupedLogCollector:
	def __init__(self) -> None:
		self.storage = []

	def add(self, message: str, sourceParts: LogSource) -> None:
		self.storage.append((message, [sourceParts]))

	def items(self):
		return self.storage


def onCook(scriptOp):
	scriptOp.clear()

	d = scriptOp.inputs[0]
	if op.logManager.par.Groupsimilarlogs.eval():
		logs = GroupedLogCollector()
	else:
		logs = UngroupedLogCollector()

	for i in range(1, d.numRows):
		# TODO: don't .val directly as it can error if column is missing
		timestamp = d[i, 'timestamp'].val
		timeMatch = TIME_RE.search(timestamp)
		timeStr = timeMatch.group(0) if timeMatch else ''
		absFrame = d[i, 'absframe'].val
		logName = d[i, 'logname'].val
		source = d[i, 'source'].val
		count = d[i, 'count'].val
		countMsg = f'({count})' if count else ''

		sourceParts = [absFrame, timeStr, logName, source, countMsg]

		# severity = '{#color(255,0,0)}' + d[i, 'severity'].val + '{#reset()}'
		severity = d[i, 'severity'].val.upper()
		severity = SEVERITY_REMAP.get(severity, severity)

		message = decode(d[i, 'message'].val, 'unicode-escape')
		message = f'{severity}: {message}'

		logs.add(message, sourceParts)

	log = ''
	for message, sources in logs.items():
		print(sources)
		log += '\n'.join(justifyColumns(sources))
		log += '\n' + message + '\n\n'

	scriptOp.text = log
