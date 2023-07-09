from enum import Enum
from typing import cast

from statemachine import State, StateMachine
from tda import BaseExt


class MidiManagerExt(BaseExt, StateMachine):
	Active: bool
	TargetDeviceID: int

	uninitialized = State(initial=True)
	connection_unavailable = State()
	disconnected = State()
	connected = State()

	Toggle = (
		uninitialized.to(connected, cond='isConnectionAvailable')
		| uninitialized.to(connection_unavailable)
		| connected.to(disconnected, cond='isConnectionAvailable')
		| connected.to(connection_unavailable)
		| connection_unavailable.to(disconnected, cond='isConnectionAvailable')
		| connection_unavailable.to(connection_unavailable)
		| disconnected.to(connected, cond='isConnectionAvailable')
		| disconnected.to(connection_unavailable)
	)

	def __init__(self, ownerComponent, logger):  # noqa: ANN001
		BaseExt.__init__(self, ownerComponent, logger)
		StateMachine.__init__(self)

		TDF = op.TDModules.mod.TDFunctions
		TDF.createProperty(self, 'Active', False)  # noqa: FBT003
		TDF.createProperty(self, 'TargetDeviceID', 1)

		self.targetDeviceName = 'APC40 mkII'

		self.midiInputs = cast(DAT, op('/local/midi/midi_inputs'))
		self.midiOutputs = cast(DAT, op('/local/midi/midi_outputs'))
		self.midiDevice = cast(DAT, op('/local/midi/device'))

		self.midiIn = cast(CHOP, ownerComponent.op('midiin1'))
		self.midiOut = cast(CHOP, ownerComponent.op('midiout1'))

		self.Toggle()
		self.logInfo('MidiManager Initalized')

	def isConnectionAvailable(self):
		mod('/sys/devices/midi/initDevice').onStart()

		# TD pattern matching doesn't support spaces, so replace them with "?"
		matchableName = self.targetDeviceName.replace(' ', '?')

		if not (
			self.midiInputs.findCell(matchableName)
			and self.midiInputs.findCell(matchableName)
		):
			self.logWarning(
				f'unable to activate midi control, "{self.targetDeviceName}" is not connected'
			)
			return False

		return True

	def configureMidiDevice(self):
		midiConfig = [
			# id
			self.TargetDeviceID,
			# indevice
			self.targetDeviceName,
			# outdevice
			self.targetDeviceName,
			# definition
			'',
			# channel
			self.TargetDeviceID
		]

		if self.midiDevice.row(str(self.TargetDeviceID)):
			self.midiDevice.replaceRow(str(self.TargetDeviceID), midiConfig)
		else:
			self.midiDevice.appendRow(midiConfig)

	####
	# State Machine Callbacks
	####
	def on_enter_connected(self):
		self.logInfo(f'connected to "{self.targetDeviceName}"')
		self.configureMidiDevice()
		self.Active = True

	def on_exit_connected(self):
		self.logInfo(f'disconnected from "{self.targetDeviceName}"')
		self.Active = False


class APC40Mode(Enum):
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

	def __init__(self, midiOut):
		self.midiOut = midiOut

	def setMode(self, mode: APC40Mode):
		self.midiOut.sendExclusive(71, 1, 41, 96, 0, 4, mode, 8, 2, 7)
