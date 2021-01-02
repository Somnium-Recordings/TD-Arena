from tda import BaseExt


class UI(BaseExt):
	def __init__(self, ownerComponent, logger) -> None:
		super().__init__(ownerComponent, logger)

	# dropName: dropped node name or filename
	# [x/y]Pos: position in network pane
	# index: index of dragged item
	# totalDragged: total amount of dragged items
	# dropExt: operator type or file extension of dragged item
	# baseName: dragged node parent network or parent directory of dragged file
	# destPath: dropped network
	def OnDrop(
		self, dropName, xPos, yPos, index, totalDragged, dropExt, baseName, destPath
	):  # pylint: disable=too-many-arguments
		pass

	#
	#  drag arguments for nodes          (and files)
	#
	#       arg1 dragged node name            (or filename)
	#       arg2 dragged index
	#       arg3 total dragged
	#       arg4 operator                     (or file extension)
	#       arg5 dragged node parent network  (or parent directory)
	def OnDrag(self, dragName, index, num, dragExt, baseName):  # pylint: disable=too-many-arguments,unused-argument,no-self-use
		print('dragging')
