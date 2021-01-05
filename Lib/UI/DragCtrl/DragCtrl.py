from collections import namedtuple
from fnmatch import fnmatchcase

from tda import BaseExt, Par

DroppedItem = namedtuple(
	'DroppedItem', [
		'dropName', 'dropExt', 'baseName', 'destPath', 'itemPath',
		'selectedItemIndex'
	]
)

DROP_SCRIPT_MAP = [
	'DISABLED_ACTION_STATE',
	'Ondropcenterscript',
	'Ondropleftscript',
	'Ondroprightscript',
	'Ondropbottomscript',
	'Ondroptopscript'
] # yapf: disable


class DragCtrl(BaseExt):
	def __init__(self, ownerComponent, logger) -> None:
		super().__init__(ownerComponent, logger)
		TDF = op.TDModules.mod.TDFunctions

		self.IsDragging: bool
		self._IsDragging: Par[bool]
		TDF.createProperty(self, 'IsDragging', value=False, readOnly=True)

		self.DraggedPath: str
		self._DraggedPath: Par[str]
		TDF.createProperty(self, 'DraggedPath', value='', readOnly=True)

	# dropName: dropped node name or filename
	# [x/y]Pos: position in network pane
	# index: index of dragged item
	# totalDragged: total amount of dragged items
	# dropExt: operator type or file extension of dragged item
	# baseName: dragged node parent network or parent directory of dragged file
	# destPath: dropped network
	def OnDrop(
		self, dropName, xPos, yPos, index, totalDragged, dropExt, baseName, destPath
	):  # pylint: disable=too-many-arguments,unused-argument
		dragControls = op(destPath)
		lastAction = dragControls.op('./null_lastAction')
		dropAction = int(lastAction['dropAction'])
		assert 0 <= dropAction <= len(DROP_SCRIPT_MAP), (
			f'unmapped drop action index {dropAction} not in {DROP_SCRIPT_MAP}'
		)

		if dropAction == 0:
			self.logInfo('dropped on disabled region, skipping processing')
			return

		droppedItem = DroppedItem(
			dropName, dropExt, baseName, destPath, f'{baseName}/{dropName}',
			int(lastAction['selectedItemIndex'])
		)
		self.logInfo(f'dropped {droppedItem.itemPath} on {destPath}')

		scriptPar = DROP_SCRIPT_MAP[dropAction]
		dropScript = dragControls.par[scriptPar].eval()

		self.logInfo(f'calling {scriptPar} on {destPath}')
		run(dropScript, droppedItem)

	#
	#  drag arguments for nodes          (and files)
	#
	#       arg1 dragged node name            (or filename)
	#       arg2 dragged index
	#       arg3 total dragged
	#       arg4 operator                     (or file extension)
	#       arg5 dragged node parent network  (or parent directory)
	def OnDrag(self, dragName, index, num, dragExt, baseName):  # pylint: disable=too-many-arguments,unused-argument,no-self-use
		self._IsDragging.val = True
		self._DraggedPath.val = f'{baseName}/{dragName}.{dragExt}'
		print('dragging')

	def OnDragRelease(self):
		self._IsDragging.val = False
		self._DraggedPath.val = ''
		print('drag released')

	def DragAction(self, u, v, controls):
		print(f'checking action for {controls.path}')
		return 1 if u > .5 else 0
