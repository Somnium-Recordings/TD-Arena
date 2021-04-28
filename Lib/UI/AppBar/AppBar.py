import ctypes

from tda import BaseExt, Par

# These SW_ constants are used for ShowWindow() and are documented at
# https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-showwindow#parameters
SW_FORCEMINIMIZE = 11
SW_HIDE = 0
SW_MAXIMIZE = 3
SW_MINIMIZE = 6
SW_RESTORE = 9
SW_SHOW = 5
SW_SHOWDEFAULT = 10
SW_SHOWMAXIMIZED = 3
SW_SHOWMINIMIZED = 2
SW_SHOWMINNOACTIVE = 7
SW_SHOWNA = 8
SW_SHOWNOACTIVATE = 4
SW_SHOWNORMAL = 1


class AppBar(BaseExt):
	def __init__(self, ownerComponent, logger):
		super().__init__(ownerComponent, logger)

		self.Maximized: bool
		self._Maximized: Par[bool]

		TDF = op.TDModules.mod.TDFunctions
		TDF.createProperty(self, 'Maximized', value=False)

	@property
	def window(self):
		return ctypes.windll.user32.FindWindowW(None, 'TD Arena')

	def Minimize(self):
		print('minimizing')
		ctypes.windll.user32.ShowWindow(self.window, SW_MINIMIZE)

	def ToggleMaximize(self):
		# NOTE: I'm not using GetWindowPlacement because it's too much of a pain
		#       to create a WindowPlacement struct to access showCmd
		if self.Maximized:
			print('restoring')
			ctypes.windll.user32.ShowWindow(self.window, SW_RESTORE)
		else:
			print('maximizing')
			ctypes.windll.user32.ShowWindow(self.window, SW_MAXIMIZE)
			run('args[0].Maximized = True', self, delayFrames=10)
