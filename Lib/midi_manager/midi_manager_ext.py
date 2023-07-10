from typing import cast

from statemachine import State, StateMachine
from tda import BaseExt

from .midi_controllers import APC40


class MidiManagerExt(BaseExt, StateMachine):
	Active: bool
	ConnectionUnavailable: bool
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
		| connection_unavailable.to(connected, cond='isConnectionAvailable')
		| connection_unavailable.to(connection_unavailable)
		| disconnected.to(connected, cond='isConnectionAvailable')
		| disconnected.to(connection_unavailable)
	)

	def __init__(self, ownerComponent, logger):  # noqa: ANN001
		BaseExt.__init__(self, ownerComponent, logger)
		StateMachine.__init__(self)

		TDF = op.TDModules.mod.TDFunctions
		TDF.createProperty(self, 'Active', False)  # noqa: FBT003
		TDF.createProperty(self, 'ConnectionUnavailable', False)  # noqa: FBT003
		TDF.createProperty(self, 'TargetDeviceID', 1)

		self.midiInputs = cast(DAT, op('/local/midi/midi_inputs'))
		self.midiOutputs = cast(DAT, op('/local/midi/midi_outputs'))
		self.midiDevice = cast(DAT, op('/local/midi/device'))

		self.midiIn = cast(CHOP, ownerComponent.op('midiin1'))
		self.midiOut = cast(midioutCHOP, ownerComponent.op('midiout1'))

		self.targetDevice = APC40(self.midiOut, deviceID=self.TargetDeviceID)

		self.Toggle()
		self.logInfo('MidiManager Initialized')

	def isConnectionAvailable(self):
		mod('/sys/devices/midi/initDevice').onStart()

		# TD pattern matching doesn't support spaces, so replace them with "?"
		matchableName = self.targetDevice.name.replace(' ', '?')

		if not (
			self.midiInputs.findCell(matchableName)
			and self.midiInputs.findCell(matchableName)
		):
			self.logWarning(
				f'unable to activate midi control, "{self.targetDevice.name}" is not connected'
			)
			return False

		return True

	def configureMidiDevice(self):
		midiConfig = [
			# id
			self.targetDevice.deviceID,
			# indevice
			self.targetDevice.name,
			# outdevice
			self.targetDevice.name,
			# definition
			'',
			# channel
			self.targetDevice.deviceID,
		]

		if self.midiDevice.row(str(self.targetDevice.deviceID)):
			self.midiDevice.replaceRow(str(self.targetDevice.deviceID), midiConfig)
		else:
			self.midiDevice.appendRow(midiConfig)

		self.targetDevice.OnConnect()

	####
	# State Machine Callbacks
	####
	def on_enter_connection_unavailable(self):
		self.ConnectionUnavailable = True

	def on_exit_connection_unavailable(self):
		self.ConnectionUnavailable = False

	def on_enter_connected(self):
		self.logInfo(f'connected to "{self.targetDevice.name}"')
		self.configureMidiDevice()
		self.Active = True

	def on_exit_connected(self):
		self.logInfo(f'disconnected from "{self.targetDevice.name}"')
		self.Active = False
