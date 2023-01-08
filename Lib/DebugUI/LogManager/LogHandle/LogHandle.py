class LogHandle:
	def __init__(self, ownerComp, logStorageDat) -> None:
		self.ownerComp = ownerComp
		self.wasPreviouslyActive = False
		self.logStorageDat = logStorageDat
		self.logDataBeforeSave = None

	def OnBeforeSave(self):
		if self.ownerComp.par.Active.eval():
			self.wasPreviouslyActive = True
			self.ownerComp.par.Active = False

		self.logDataBeforeSave = self.logStorageDat.text
		self.logStorageDat.clear(keepFirstRow=True)

	def OnAfterSave(self):
		if self.wasPreviouslyActive:
			self.ownerComp.par.Active = True
			self.wasPreviouslyActive = False

		if self.logDataBeforeSave is not None:
			self.logStorageDat.text = self.logDataBeforeSave
			self.logDataBeforeSave = None
