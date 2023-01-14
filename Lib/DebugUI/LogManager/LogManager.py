from typing import Any


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

	def SetLoggerParam(self, logName: str, paramName: str, value: Any):
		for handle in [
			h for h in self.allLogHandles() if h.par.Name.eval() == logName
		]:
			handle.par[paramName] = value

	def allLogHandles(self):
		return self.ownerComp.findChildren(name='logHandle[0-99]')
