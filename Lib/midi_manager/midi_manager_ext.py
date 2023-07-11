from typing import cast

from tda import BaseExt
from transitions import Machine

from .midi_controllers import APC40

# TODO:
#   - Connect automatically if not connected when composition is loaded
#   - Unbind handlers / disconnect when composition unloaded


class MidiManagerExt(BaseExt, Machine):
	ConnectionUnavailable: bool
	TargetDeviceID: int

	def __init__(self, ownerComponent, logger):  # noqa: ANN001
		TDF = op.TDModules.mod.TDFunctions
		TDF.createProperty(self, 'TargetDeviceID', 1)
		# NOTE: This need the be in place before we call Machine.__init so that the
		#       state is property set
		TDF.createProperty(self, 'State', 'machine-not-initialized')

		BaseExt.__init__(self, ownerComponent, logger)
		Machine.__init__(
			self,
			states=[
				'uninitialized', 'connecting', 'connected', 'connection_unavailable',
				'disconnected'
			],
			initial='uninitialized',
			model_attribute='State',
			transitions=[
				{
					'trigger': 'Toggle',
					'source': '*',
					'dest': 'connection_unavailable',
					'unless': 'isConnectionAvailable'
				},
				{
					'trigger': 'Toggle',
					'source': ['uninitialized', 'connection_unavailable', 'disconnected'],
					'dest': 'connecting',
				},
				{
					'trigger': 'Toggle',
					'source': ['connecting', 'connected'],
					'dest': 'disconnected',
				},
				{
					# We go to connecting -> MidiOutConnected -> connecting to ensure the
					# midi out chop has had a chance to register the state change and active.
					#
					# Without waiting for this (most likely just a frame), we run into issues
					# where we try to midiOUt.sendControl(...) before the chop is ready to
					# process the requests
					'trigger': 'MidiOutConnected',
					'source': 'connecting',
					'dest': 'connected'
				}
			]
		)

		self.midiInputs = cast(DAT, op('/local/midi/midi_inputs'))
		self.midiOutputs = cast(DAT, op('/local/midi/midi_outputs'))
		self.midiDevice = cast(DAT, op('/local/midi/device'))

		self.midiIn = cast(CHOP, ownerComponent.op('midiin1'))
		self.midiOut = cast(midioutCHOP, ownerComponent.op('midiout1'))

		self.targetDevice = APC40(self.midiOut, deviceID=self.TargetDeviceID)

		self.logInfo('MidiManager Initialized')

	def __del__(self):
		# Ensure we disconnect gracefully on teardown
		# NOTE: this is only really relevant during development
		if self.State == 'connected':
			self.Toggle()

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

	####
	# State Machine Callbacks
	####
	def on_enter_connecting(self):
		self.logInfo(f'connecting to "{self.targetDevice.name}"')

	def on_enter_connected(self):
		self.configureMidiDevice()
		self.targetDevice.Connect()
		self.logInfo(f'connected to "{self.targetDevice.name}"')

	def on_exit_connected(self):
		self.logInfo(f'disconnected from "{self.targetDevice.name}"')
		self.targetDevice.Disconnect()
