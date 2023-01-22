import time


def formatTimestamp(timestamp):
	winSecs = int(timestamp / 10000000)  ## divide by 10 000 000 to get seconds
	epoch = max(winSecs - 11644473600, 0)
	timeStr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch))
	return timeStr


def isCloneOfSelf(c):
	return op(c.par.clone).id == c.id


def isClone(o):
	return o is not None and o.par.clone


# Check the parents to to handle cases where we have an external
# tox that is replicated inside of another component
def isCloneAndNotOfSelf(c, parentsToCheck=1):
	opsToCheck = [c.parent(i) for i in range(parentsToCheck + 1)]

	return next(
		filter(None, [isClone(o) and not isCloneOfSelf(o) for o in opsToCheck]),
		False
	)


#########################################################
#                                                       #
# OpFind Callbacks Below                                #
#                                                       #
#########################################################

# me - this DAT
# dat - the DAT that is querying
# curOp - the OP being queried
# row - the table row index

# Uncomment following two functions to add custom columns


def onInitGetColumnNames(_dat):
	return ['networkPath', 'filePath', 'dirty', 'lastEditedTime']


#
def onFindOPGetValues(_dat, curOp, _row):
	return [
		curOp.path,
		curOp.par.externaltox.eval(), curOp.dirty,
		formatTimestamp(curOp.externalTimeStamp)
	]


# Return True / False to include / exclude an operator in the table
def onFindOPGetInclude(_dat, curOp, _row):
	# We check for a non-empty external tox, but if it's an expression
	# it passes that check, even when empty. This covers that case
	if not curOp.par.externaltox.eval():
		return False

	if op.toxManager.IsCompositionNetworkPath(curOp.path):
		return True

	# TODO: maybe use tags or something here instead so it works for renders
	# TODO: maybe instead of doing this we can just leave the clones in, but use
	#       the "onlySaveOneWithSamePath" logic we use for composition components?
	if isCloneAndNotOfSelf(curOp):
		return False

	return True


# Provide an extensive dictionary of what was matched for each operator.
# Multiple matching tags, parameters and cells will be included.
# For each match, a corresponding key is included in the dictionary:
#
#  results:
#
#  'name': curOp.name
#  'type': curOp.OPType
#  'path': curOp.path
#  'parent' : curOp.parent()
#  'comment': curOp.comment
#  'tags' : [list of strings] or empty list
#  'text' : [list of Cells] or empty list
#  'par': dictionary of matching parameter attributes.
#    example entries:
#        tx : { 'name': True, 'value':True , 'expression':True } # Parameter tx matched on name, value, expression
#        ty : { 'value' : True } # Parameter ty matched on value
#

# def onOPFound(dat, curOp, row, results):
# 	return
