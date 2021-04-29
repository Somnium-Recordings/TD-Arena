from tda import BaseExt, Par
from win32 import (findWindowByName, isMaximizedWindow, minimizeWindow,
                   toggleMaximizeWindow)


class AppBar(BaseExt):
	def __init__(self, ownerComponent, logger):
		super().__init__(ownerComponent, logger)

		self.Maximized: bool
		self._Maximized: Par[bool]

		TDF = op.TDModules.mod.TDFunctions
		TDF.createProperty(self, 'Maximized', value=False)

	@property
	def uiWindow(self):
		return findWindowByName('TD Arena')

	def OnUIResize(self):
		print('resized')
		self.Maximized = isMaximizedWindow(self.uiWindow)

	def MinimizeUI(self):
		print('minimizing')
		minimizeWindow(self.uiWindow)

	def ToggleMaximizeUI(self):
		print('toggling')
		toggleMaximizeWindow(self.uiWindow)
