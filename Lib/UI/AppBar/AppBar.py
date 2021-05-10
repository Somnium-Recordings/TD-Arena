from tda import BaseExt, Par
from win32 import (findWindowByName, isMaximizedWindow, minimizeWindow,
                   toggleMaximizeWindow)


class AppBar(BaseExt):
	def __init__(self, ownerComponent, logger, uiWindow):
		super().__init__(ownerComponent, logger)

		self.uiWindow = uiWindow

		self.Maximized: bool
		self._Maximized: Par[bool]

		TDF = op.TDModules.mod.TDFunctions
		TDF.createProperty(self, 'Maximized', value=False)

	@property
	def ContentSize(self):
		return self.ownerComponent.op('null_contentSize')

	@property
	def uiWindowhandle(self):
		return findWindowByName(self.uiWindow.par.title.eval())

	def OnUIResize(self, retrying=False):
		w = self.uiWindowhandle

		if w:
			self.Maximized = isMaximizedWindow(w)
		elif not retrying:
			self.logDebug(
				'could not find window to handle OnUIResize, trying again in 10 frames'
			)
			run('args[0].OnUIResize(retrying=True)', self, delayFrames=10)
		else:
			self.logError('failed on handle onUIResize after retry')

	def OnLeftMouse(self):
		pass

	def MinimizeUI(self):
		w = self.uiWindowhandle
		if not w:
			self.logError('unable to find window to minimize')
			return

		self.logInfo('minimizing ui window')
		minimizeWindow(w)

	def CloseUI(self):
		if ui.performMode:
			self.logInfo('exiting td arena')
			project.quit()
		else:
			self.logInfo('closing ui window')
			self.uiWindow.par.winclose.pulse()

	def ToggleMaximizeUI(self):
		w = self.uiWindowhandle
		if not w:
			self.logError('unable to find window to toggle maximied')
			return

		self.logInfo('toggling ui window maximize')
		toggleMaximizeWindow(w)
