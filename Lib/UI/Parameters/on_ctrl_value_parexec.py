ctrlSource = op('extension').module.CTRL_SRC_NAME


# Called at end of frame with complete list of individual parameter changes.
# The changes are a list of named tuples, where each tuple is (Par, previous value)
def onValuesChanged(changes):  # noqa: ANN001
	for c in changes:
		par = c.par
		# prev = c.prev
		address = par.owner.par.Valname0.eval()
		op.uiState.UpdateCtrlValue(address, par.eval(), ctrlSource)
