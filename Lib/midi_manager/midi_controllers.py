from enum import IntEnum
from typing import cast

from ui_state import ui_state_ext


class APC40Mode(IntEnum):
	'''
	See: https://6be54c364949b623a3c0-4409a68c214f3a9eeca8d0265e9266c0.ssl.cf2.rackcdn.com/989/documents/APC40Mk2_Communications_Protocol_v1.2.pdf
	Section: "Outbound Message Type 0: Introduction"
	'''

	GENERIC = 64
	'''
	Generic Mode

	Layers change "pages", toggles retain state, etc.
	'''

	ABLETON_LIVE = 65
	'''
	Partial Control
	- All buttons are momentary buttons.
	- Device control knobs and buttons are not banked within the APC40 Mk2.
	- LED Rings around the knobs are controlled by the APC40 but can be updated by the Host.
	- All other LEDs are controlled by the Host.
	'''

	ABLETON_LIVE_ALT = 66
	'''
	Full control
	- All buttons are momentary buttons.
	- Device control knobs and buttons are not banked within the APC40 Mk2.
	- All LEDs are controlled by the Host.
	'''


class APC40():
	name = 'APC40 mkII'

	@property
	def ctrlSrcName(self):
		return f'midi-out:{self.name}'

	def __init__(self, midiOut: midioutCHOP, deviceID: int):
		self.midiOut = midiOut
		self.deviceID = deviceID
		self.uiState = cast(ui_state_ext.UIStateExt, op.ui_state.ext.UIStateExt)

	def Connect(self):
		self.setMode(APC40Mode.ABLETON_LIVE_ALT)
		self.registerHandlers()

	def Disconnect(self):
		self.deregisterHandlers()

	def setMode(self, mode: APC40Mode):
		self.midiOut.sendExclusive(71, 1, 41, 96, 0, 4, mode, 8, 2, 7)

	# NOTE: most below here should probably be either in the midi_manager
	# 		or an ABC
	def registerHandlers(self):
		self.uiState.RegisterCtrl(
			'/composition/layers/1/video:Opacity',
			self.ctrlSrcName,
			self.onReceiveCtrlValue,
			alwaysRequestValue=True
		)

	def deregisterHandlers(self):
		self.uiState.DeregisterCtrl(
			'/composition/layers/1/video:Opacity', self.ctrlSrcName
		)

	def onReceiveCtrlValue(
		self,
		address: str,  # noqa: ARG002
		value: ui_state_ext.OSCValue
	) -> None:
		# map oscValue to deviceValue using mapping table
		self.midiOut.sendControl(1, 48, value)

	def onReceiveDeviceValue(self):
		# if type is "msg", send with no value
		#   - self.uiState.SendMessage ???
		# if type is "ctrl", use map to map/normalize midi value
		#   - self.uiState.UpdateCtrlValue
		...
