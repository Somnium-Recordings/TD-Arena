class LogHandleExt:

	def __init__(self, ownerComp, logStorageDat) -> None:  # noqa: ANN001
		self.ownerComp = ownerComp
		self.wasPreviouslyActive = False
		self.logStorageDat = logStorageDat
		self.logDataBeforeSave = None
		self.SetToDefaultState()

	def SetToDefaultState(self):
		self.ownerComp.par.Active = self.ownerComp.par.Defaultstate.eval()
		self.ownerComp.par.Visible = self.ownerComp.par.Defaultstate.eval()

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
