from enum import IntEnum
from itertools import chain

from .midi_device_ext import (
	CONTROLS,
	MidiCtrlMap,
	MidiDeviceExt,
	MidiMap,
	MidiNoteMap,
)


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


APC40_MAPPINGS_LIST: list[MidiMap] = list(
	chain(
		*[
			[
				MidiNoteMap(control=CONTROLS[f'layer{n}select'], channel=n, note=51),
				MidiCtrlMap(control=CONTROLS[f'layer{n}fader'], channel=n, index=7),
				MidiCtrlMap(control=CONTROLS[f'layer{n}knob'], channel=1, index=47 + n)
			] for n in range(1, 9)
		]
	)
)

APC40_MAPPINGS = {
	mapping.midiAddress: mapping
	for mapping in APC40_MAPPINGS_LIST
}


class APC40Ext(MidiDeviceExt):

	@property
	def name(self):
		return 'APC40 mkII'

	@property
	def mappings(self):
		return APC40_MAPPINGS

	def setupDevice(self) -> None:
		self.setMode(APC40Mode.ABLETON_LIVE_ALT)

	def setMode(self, mode: APC40Mode):
		self.midiOut.sendExclusive(71, 1, 41, 96, 0, 4, mode, 8, 2, 7)
