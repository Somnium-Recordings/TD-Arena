# pylint: disable=too-few-public-methods, unused-argument
#
# Patterns / APIs lifted from winappdbg
#
# @see https://github.com/MarioVilas/winappdbg
#

import ctypes
import typing

windll = ctypes.windll
user32 = windll.user32
kernel32 = windll.kernel32

GetLastError = kernel32.GetLastError

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

ERROR_SUCCESS = 0

Structure = ctypes.Structure

LPSTR = ctypes.c_char_p
LPWSTR = ctypes.c_wchar_p
LPVOID = ctypes.c_void_p
UINT = ctypes.c_uint


class POINT(Structure):
	_fields_ = [('x', ctypes.c_long), ('y', ctypes.c_long)]


class RECT(Structure):
	_fields_ = [
		('left', ctypes.c_long), ('top', ctypes.c_long), ('right', ctypes.c_long),
		('bottom', ctypes.c_long)
	]


sizeof = ctypes.sizeof
byref = ctypes.byref

POINTER = ctypes.POINTER
HANDLE = LPVOID
HWND = HANDLE


# typedef struct _WINDOWPLACEMENT {
#     UINT length;
#     UINT flags;
#     UINT showCmd;
#     POINT ptMinPosition;
#     POINT ptMaxPosition;
#     RECT rcNormalPosition;
# } WINDOWPLACEMENT;
class WINDOWPLACEMENT(Structure):
	showCmd: UINT

	_fields_ = [
		('length', UINT),
		('flags', UINT),
		('showCmd', UINT),
		('ptMinPosition', POINT),
		('ptMaxPosition', POINT),
		('rcNormalPosition', RECT),
	]


PWINDOWPLACEMENT = POINTER(WINDOWPLACEMENT)


def RaiseIfZero(result, func=None, arguments=()):
	"""
    Error checking for most Win32 API calls.

    The function is assumed to return an integer, which is C{0} on error.
    In that case the C{WindowsError} exception is raised.
    """
	if not result:
		raise ctypes.WinError()
	return result


def FindWindowW(lpClassName=None, lpWindowName=None) -> HANDLE:
	_FindWindowW = user32.FindWindowW
	_FindWindowW.argtypes = [LPWSTR, LPWSTR]
	_FindWindowW.restype = HWND

	hWnd = _FindWindowW(lpClassName, lpWindowName)
	if not hWnd:
		errcode = GetLastError()
		if errcode != ERROR_SUCCESS:
			raise ctypes.WinError(errcode)
	return hWnd


def ShowWindow(hWnd: HANDLE, nCmdShow=SW_SHOW) -> bool:
	_ShowWindow = user32.ShowWindow
	_ShowWindow.argtypes = [HWND, ctypes.c_int]
	_ShowWindow.restype = bool
	return _ShowWindow(hWnd, nCmdShow)


def GetWindowPlacement(hWnd: HANDLE) -> WINDOWPLACEMENT:
	_GetWindowPlacement = user32.GetWindowPlacement
	_GetWindowPlacement.argtypes = [HWND, PWINDOWPLACEMENT]
	_GetWindowPlacement.restype = bool
	_GetWindowPlacement.errcheck = RaiseIfZero

	lpwndpl = WINDOWPLACEMENT()
	lpwndpl.length = sizeof(lpwndpl)
	_GetWindowPlacement(hWnd, byref(lpwndpl))

	return lpwndpl


def CloseWindow(hWnd: HANDLE) -> bool:
	_CloseWindow = user32.CloseWindow
	_CloseWindow.argtypes = [HWND]
	_CloseWindow.restype = bool
	_CloseWindow.errcheck = RaiseIfZero

	return _CloseWindow(hWnd)


def DestroyWindow(hWnd: HANDLE) -> bool:
	_DestroyWindow = user32.DestroyWindow
	_DestroyWindow.argtypes = [HWND]
	_DestroyWindow.restype = bool
	_DestroyWindow.errcheck = RaiseIfZero

	return _DestroyWindow(hWnd)


def findWindowByName(name: str, retrying=False) -> typing.Optional[HANDLE]:
	try:
		w = FindWindowW(None, name)

		if w is None:
			# Touch designer adds a * if the project is unsaved,
			# try that before erroring
			w = FindWindowW(None, f'{name}*')
	except WindowsError:
		# For some reason this function throws a file not found error
		# when opening the window for the first time. We return None here
		# and handle retry on the consuming side.
		return None

	return w


def minimizeWindow(hWnd: HANDLE):
	ShowWindow(hWnd, SW_MINIMIZE)


def closeWindow(hWnd: HANDLE):
	DestroyWindow(hWnd)


def isMaximizedWindow(hWnd: HANDLE):
	wp = GetWindowPlacement(hWnd)
	return wp.showCmd == SW_SHOWMAXIMIZED


def toggleMaximizeWindow(hWnd: HANDLE):
	ShowWindow(hWnd, SW_RESTORE if isMaximizedWindow(hWnd) else SW_MAXIMIZE)
