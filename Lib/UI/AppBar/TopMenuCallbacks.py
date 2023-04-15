"""
TopMenu callbacks

Callbacks always take a single argument, which is a dictionary
of values relevant to the callback. Print this dictionary to see what is
being passed. The keys explain what each item is.

TopMenu info keys:
	'widget': the TopMenu widget
	'item': the item label in the menu list
	'index': either menu index or -1 for none
	'indexPath': list of parent menu indexes leading to this item
	'define': TopMenu define DAT definition info for this menu item
	'menu': the popMenu component inside topMenu
"""

###############################
# TD Arena Menu
###############################


def tdArenaPreferences(_info):  # noqa: ANN001
	op.userSettings.openParameters()


def tdArenaQuit(_info):  # noqa: ANN001
	op.uiAppBar.CloseUI()


###############################
# Composition Menu
###############################


def compositionNew(_info):  # noqa: ANN001
	op.tda.NewComposition()


def compositionOpen(_info):  # noqa: ANN001
	op.tda.OpenComposition(promptIfConfigured=True)


def getCompositionRecentFiles(_info):  # noqa: ANN001
	"""
	A rowCallback used in the Top Menu DAT table to automatically generate rows.
	These callbacks must return a dictionary or list of dictionaries that mimic
	the columns in the Top Menu DAT. Dictionaries only need the columns with
	data in them, but must have corresponding columns in the Top Menu DAT in
	order to be recognized.
	"""
	return [
		{
			'item2': 'File 1'
		}, {
			'item2': 'File 2',
			'highlight': True
		}, {
			'item2': 'File three',
			'dividerAfter': True
		}
	]


def compositionSave(_info):  # noqa: ANN001
	op.tda.SaveComposition()


def compositionSaveAs(_info):  # noqa: ANN001
	op.tda.SaveComposition(saveAs=True)


###############################
# Render menu
###############################


def renderReinitComposition(_info):  # noqa: ANN001
	op.tda.ReinitComposition()


def renderUseEngine(_info):  # noqa: ANN001
	op.tda.ToggleEngine()


def renderReloadEngine(_info):  # noqa: ANN001
	op.tda.ReloadEngine()


def renderUnload(_info):  # noqa: ANN001
	op.tda.Unload()


###############################
# View Menu
###############################


def getViewLayouts(_info):  # noqa: ANN001
	# TODO: for some reason rowcallbacks don't fire every time
	# selectedLayout = op.userSettings.par.Gridlayout.eval() or 'Default'
	layouts = [
		{
			'item2': layoutName,
			'callback': 'viewLayoutsSelect',
			# 'highlight': layoutName == selectedLayout
		} for layoutName in op.uiGrid.GetAvailableLayouts()
	]
	layouts[-1]['dividerAfter'] = True

	footer = [{'item2': 'Save', 'callback': 'viewLayoutsSave'}]

	return layouts + footer


def viewLayoutsSelect(info):  # noqa: ANN001
	op.uiGrid.SelectLayout(info['define']['name'])


def viewLayoutsSave(_info):  # noqa: ANN001
	op.uiGrid.SaveLayout()


def viewToggleUiDpiScaling(_info):  # noqa: ANN001
	op.userSettings.par.Uidpiscaling = not op.userSettings.par.Uidpiscaling.eval()


def viewDebugWindow(_info):  # noqa: ANN001
	if op.debug_ui.IsOpen:
		op.debug_ui.Close()
	else:
		op.debug_ui.Open()


###############################
# standard menu callbacks
###############################


def onSelect(_info):  # noqa: ANN001
	"""
	User selects a menu option
	"""
	# debug(info)


def onRollover(_info):  # noqa: ANN001
	"""
	Mouse rolled over an item
	"""


def onOpen(_info):  # noqa: ANN001
	"""
	Menu opened
	"""
	# debug(_info)


def onClose(_info):  # noqa: ANN001
	"""
	Menu closed
	"""


def onMouseDown(_info):  # noqa: ANN001
	"""
	Item pressed
	"""


def onMouseUp(_info):  # noqa: ANN001
	"""
	Item released
	"""


def onClick(_info):  # noqa: ANN001
	"""
	Item pressed and released
	"""


def onLostFocus(_info):  # noqa: ANN001
	"""
	Menu lost focus
	"""
