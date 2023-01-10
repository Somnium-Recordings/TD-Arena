class LogManager:
	@property
	def LogCountsDat(self):
		return self.ownerComp.op('./null_counts')

	def __init__(self, ownerComp) -> None:
		self.ownerComp = ownerComp

	def SetGlobalLogParam(self, paramName: str, value: int):
		for handle in self.allLogHandles():
			handle.par[paramName].val = value

	def PulseGlobalLogParam(self, paramName: str):
		for handle in self.allLogHandles():
			handle.par[paramName].pulse()

	def allLogHandles(self):
		return self.ownerComp.findChildren(name='logHandle[0-99]')
