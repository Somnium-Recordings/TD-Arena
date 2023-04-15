from tda import BaseExt, DroppedItem

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
		self._IsDragging: Par
		TDF.createProperty(self, 'IsDragging', value=False, readOnly=True)

		self.DraggedPath: str
		self._DraggedPath: Par
		TDF.createProperty(self, 'DraggedPath', value='', readOnly=True)

	# dropName: dropped node name or filename
	# [x/y]Pos: position in network pane
	# index: index of dragged item
	# totalDragged: total amount of dragged items
	# dropExt: operator type or file extension of dragged item
	# baseName: dragged node parent network or parent directory of dragged file
	# destPath: dropped network
	def OnDrop(
		self,
		dropName,
		xPos,  # noqa: ARG002
		yPos,  # noqa: ARG002
		index,  # noqa: ARG002
		totalDragged,  # noqa: ARG002
		dropExt,
		baseName,
		destPath
	):  # pylint: disable=too-many-arguments,unused-argument
		dropControls = op(destPath)
		lastAction = dropControls.op('./null_lastAction')
		dropAction = int(lastAction['dropAction'])
		assert 0 <= dropAction <= len(DROP_SCRIPT_MAP), (
			f'unmapped drop action index {dropAction} not in {DROP_SCRIPT_MAP}'
		)

		if dropAction == 0:
			self.logInfo('dropped on disabled region, skipping processing')
			return

		droppedItem = DroppedItem(
			dropName,
			dropExt,
			baseName,
			destPath,
			itemPath=f'{baseName}/{dropName}',
			selectedItemIndex=int(lastAction['selectedItemIndex'])
		)
		self.logInfo(f'dropped {droppedItem.itemPath} on {destPath}')

		scriptPar = DROP_SCRIPT_MAP[dropAction]
		dropScript = dropControls.par[scriptPar].eval()

		self.logDebug(f'calling {scriptPar} on {destPath}')
		run(dropScript, droppedItem, fromOP=dropControls, asParameter=scriptPar)

	#
	#  drag arguments for nodes          (and files)
	#
	#       arg1 dragged node name            (or filename)
	#       arg2 dragged index
	#       arg3 total dragged
	#       arg4 operator                     (or file extension)
	#       arg5 dragged node parent network  (or parent directory)
	def OnDrag(self, dragName, index, num, dragExt, baseName):  # pylint: disable=too-many-arguments,unused-argument  # noqa: ARG002
		self._IsDragging.val = True
		self._DraggedPath.val = f'{baseName}/{dragName}.{dragExt}'
		self.logDebug(f'started dragging {self.DraggedPath}')

	def OnDragRelease(self):
		self._IsDragging.val = False
		self._DraggedPath.val = ''
		self.logDebug('drag released')
