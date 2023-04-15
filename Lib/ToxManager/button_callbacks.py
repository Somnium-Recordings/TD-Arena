def onOffToOn(panelValue):  # noqa: ANN001
	toxLister = op('toxLister')
	buttonName = panelValue.owner.name

	if buttonName == 'button_reload':
		parent.toxManager.RefreshToxList()

	elif buttonName == 'button_expandAll':
		for pathCell in op('null_allToxes').col('path')[1:]:
			toxLister.OpenToPath(pathCell.val, False)  # noqa: FBT003
		toxLister.Refresh()

	elif buttonName == 'button_collapseAll':
		toxLister.CollapseAll()
		toxLister.Refresh()

	elif buttonName == 'button_saveAllSystemToxes':
		op.toxManager.SaveSystemToxes(selected=False)

	elif buttonName == 'button_saveSelectedSystemToxes':
		op.toxManager.SaveSystemToxes(selected=True)

	elif buttonName == 'button_saveSelectedCompositionToxes':
		op.toxManager.SaveCompositionToxes()

	else:
		raise KeyError(f'{buttonName} is not handled')
