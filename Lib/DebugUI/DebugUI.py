class DebugUI:
	@property
	def IsOpen(self):
		return self.windowInfo['winopen']

	def __init__(self, ownerComp) -> None:
		self.ownerComp = ownerComp
		self.window = ownerComp.op('window_debug')
		self.windowInfo = ownerComp.op('info_window')
		self.ui = ownerComp.op('ui')
		self.storeBorderSize()

	def storeBorderSize(self):
		self.borderW = self.windowInfo['winw'] - self.window.par.winw.eval()
		self.borderH = self.windowInfo['winh'] - self.window.par.winh.eval()

	def setUIResolution(self):
		self.ui.par.w = self.windowInfo['winw'] - self.borderW
		self.ui.par.h = self.windowInfo['winh'] - self.borderH

	def OnWindowOpen(self):
		self.storeBorderSize()
		self.setUIResolution()

	def OnWindowResize(self):
		self.setUIResolution()

	def Open(self):
		self.window.par.winopen.pulse()
