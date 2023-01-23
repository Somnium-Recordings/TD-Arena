def onTableChange(_dat):
	op('button_saveSelectedSystemToxes').par.display = parent.toxManager.HasSelectedSystemToxes() # yapf: disable
	op('button_saveSelectedCompositionToxes').par.display = parent.toxManager.HasSelectedCompositionToxes() # yapf: disable
