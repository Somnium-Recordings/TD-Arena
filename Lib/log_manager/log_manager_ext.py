from typing import Any


class LogManagerExt:

	@property
	def LogCountsDat(self):
		return self.ownerComp.op('./null_counts')

	def __init__(self, ownerComp: baseCOMP) -> None:
		self.ownerComp = ownerComp

	def SetGlobalLogParam(self, paramName: str, value: int):
		for handle in self.allLogHandles():
			handle.par[paramName].val = value

	def PulseGlobalLogParam(self, paramName: str):
		for handle in self.allLogHandles():
			handle.par[paramName].pulse()

	def SetLoggerParam(
		self,
		logName: str,
		paramName: str,
		value: Any  # noqa: ANN401
	):
		for handle in [
			h for h in self.allLogHandles() if h.par.Name.eval() == logName
		]:
			handle.par[paramName] = value

	def allLogHandles(self):
		return self.ownerComp.findChildren(name='log_handle[0-99]')
