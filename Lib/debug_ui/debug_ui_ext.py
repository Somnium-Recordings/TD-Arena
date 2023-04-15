class DebugUIExt:

	@property
	def IsOpen(self):
		return self.WindowInfo['winopen']

	def __init__(self, ownerComp) -> None:  # noqa: ANN001
		self.ownerComp = ownerComp
		self.window = ownerComp.op('window_debug')
		self.WindowInfo = ownerComp.op('info_window')

	def Open(self):
		if not self.IsOpen:
			self.window.par.winopen.pulse()

	def Close(self):
		self.window.par.winclose.pulse()

	def Toggle(self):
		if self.IsOpen:
			self.Close()
		else:
			self.Open()
