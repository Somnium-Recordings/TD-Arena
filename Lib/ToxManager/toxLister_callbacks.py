"""
All callbacks for this treeLister go here. For available callbacks, see:

https://docs.derivative.ca/Palette:treeLister#Custom_Callbacks

treeLister also has all lister callbacks:
https://docs.derivative.ca/Palette:lister#Custom_Callbacks
"""

import traceback

# def onInit(info):
# 	debug('initalized')

# 	info['listerExt'].DefaultRoots = ['/None']

# def getObjectFromID(info):
# 	return {'name': 'TreeObject'}

# def getIDFromObject(info):
# 	return '/None'

# def getObjectChildren(info):
# 	return []

# def onRefresh(info):
# 	print('refreshed')


def onReloadInput(info):  # noqa: ANN001
	"""
	Note, there is a FromPathsSelectRows function, but it ends up in an
	infinite loop when there is a gap in the tree.
	i.e. /a
	      -> /a/b
		     -> /a/b/c/d
	"""  # noqa: E101
	try:
		treeLister = info['listerExt']

		objectsToSelect = []
		dirtyPaths = []
		for (path, rowObj) in info['jsonIDObjDict'].items():
			if rowObj['dirty'] == '1':
				objectsToSelect.append(rowObj)
				dirtyPaths.append(path)

		# Create an entry for each step of a path to ensure it's fully expanded
		# i.e. /a/b/c -> /a/b/c, /a/b, /a
		pathsToExpand = set()
		for path in list(dirtyPaths):
			while path != '':
				pathsToExpand.add(path)
				path, _, _ = path.rpartition('/')

		treeLister.CollapseAll()
		for path in pathsToExpand:
			treeLister.ToggleExpand(path, True)  # noqa: FBT003

		treeLister.Refresh()

		# NOTE: This must happen after the Refresh() call
		treeLister.SelectObjects(objectsToSelect)

	# For some reason the lister doesn't actually dump the error
	except Exception as e:
		print(traceback.format_exc())  # noqa: T201
		raise e


def onClick(info):  # noqa: ANN001
	if info['rowData'] is None or info['colName'] == 'Expando':
		return

	row = info['rowData']['rowObject']
	if 'filePath' not in row or row['filePath'] == '':
		return

	lister = info['ownerComp']
	rowNumber = lister.GetObjectRowNum(row)

	if row in lister.SelectedRowObjects:
		lister.DeselectRow(rowNumber)
	else:
		lister.SelectRow(rowNumber, addRow=True)


def onClickRight(info):  # noqa: ANN001
	if info['rowData'] is None or info['colName'] == 'Expando':
		return

	# networkPath =
	if networkPath := info['rowData']['rowObject']['networkPath']:
		op.toxManager.OpenNetworkAtPath(networkPath)
