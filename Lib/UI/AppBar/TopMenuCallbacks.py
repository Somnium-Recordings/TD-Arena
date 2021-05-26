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

# TD Arena Menu


def tdArenaPreferences(_info):
	op.tda.openParameters()


def tdArenaQuit(_info):
	op.uiAppBar.CloseUI()


# Composition Menu


def compositionNew(_info):
	op.uiState.SendMessage('/composition/new')


def getCompositionRecentFiles(_info):
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


def compositionSave(_info):
	op.uiState.SendMessage('/composition/save')


# View Menu


def viewDebugWindow(_info):
	if op.debugUI.IsOpen:
		op.debugUI.Close()
	else:
		op.debugUI.Open()


# standard menu callbacks


def onSelect(_info):
	"""
	User selects a menu option
	"""
	# debug(info)


def onRollover(_info):
	"""
	Mouse rolled over an item
	"""


def onOpen(_info):
	"""
	Menu opened
	"""
	# debug(_info)


def onClose(_info):
	"""
	Menu closed
	"""


def onMouseDown(_info):
	"""
	Item pressed
	"""


def onMouseUp(_info):
	"""
	Item released
	"""


def onClick(_info):
	"""
	Item pressed and released
	"""


def onLostFocus(_info):
	"""
	Menu lost focus
	"""
