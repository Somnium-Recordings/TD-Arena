# pylint: disable=too-few-public-methods
class BrowserUI:

	def __init__(self, ownerComponent):  # noqa: ANN001
		self.ownerComponent = ownerComponent
		self.fileList = ownerComponent.op('./fileList')

	def GetPath(self, compName):  # noqa: ANN001
		comp = self.fileList.op(compName)
		assert comp is not None, f'requested path for unknown file: "{compName}"'
		data = comp.op('./select_file')
		return (
			data[1, 'basename'].val,
			tdu.expandPath(
				# eg: movie://some-move-name.mov
				f'{self.ownerComponent.par.Resourcetype}://{data[1, "relpath"].val}'
			),
		)
