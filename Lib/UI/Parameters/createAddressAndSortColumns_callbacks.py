from tdaUtils import parameterPathToAddress


def onSetupParameters(_scriptOp):  # noqa: ANN001
	pass


def onPulse(_par):  # noqa: ANN001
	return


def onCook(scriptOp):  # noqa: ANN001
	scriptOp.clear()
	paramDat = scriptOp.inputs[0]

	scriptOp.insertRow(['address', *paramDat.row(0), 'order'])

	for rowNum in range(1, paramDat.numRows):
		paramLabel = paramDat[rowNum, 'label'].val
		paramName = paramDat[rowNum, 'name'].val
		targetOpPath = paramDat[rowNum, 'path'].val
		targetOp = op(targetOpPath)

		address = parameterPathToAddress(targetOpPath, paramName)

		# While clearing out ui elements, the targetOp can get deleted before the
		# table is updated causing errors. The None check prevents that
		if (
			targetOp is None or targetOp.par[paramName] is None
			or paramLabel == 'Opacity'
		):
			order = -1
		else:
			order = targetOp.par[paramName].order

		scriptOp.appendRow([address, *paramDat.row(rowNum), order])
