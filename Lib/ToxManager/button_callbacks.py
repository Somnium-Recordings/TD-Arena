def onOffToOn(panelValue):
	toxLister = op('toxLister')
	buttonName = panelValue.owner.name

	if buttonName == 'button_reload':
		op('opfind_externalToxes').par.cookpulse.pulse()
		toxLister.par.Reloadinput.pulse()
	elif buttonName == 'button_expandAll':
		for pathCell in op('null_allToxes').col('path')[1:]:
			toxLister.OpenToPath(pathCell.val, False)
		toxLister.Refresh()
	elif buttonName == 'button_collapseAll':
		toxLister.CollapseAll()
		toxLister.Refresh()
	elif buttonName == 'button_saveAllSystemToxes':
		op.toxManager.SaveSystem(selected=False)
	elif buttonName == 'button_saveSelectedToxes':
		op.toxManager.SaveSelected()
	else:
		raise KeyError(f'{buttonName} is not handled')
