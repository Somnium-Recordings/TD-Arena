from abc import ABC, abstractmethod
from itertools import chain
from typing import Optional, TypedDict, cast

from tda import BaseExt
from transitions import Machine
from ui_state import ui_state_ext


class _MappableControl(TypedDict):
	name: str
	address: str


# Replace with NotRequired once we get python 3.11
class MappableControl(_MappableControl, total=False):
	sendMessage: str


class _MidiMap(TypedDict):
	control: MappableControl
	channel: int


class MidiMap(_MidiMap, total=False):
	index: int
	note: int


def toMidiAddress(mapping: MidiMap) -> str:
	channel = f'ch{mapping["channel"]}'

	if 'note' in mapping:
		return f'{channel}n{mapping["note"]}'

	if 'index' in mapping:
		return f'{channel}ctrl{mapping["index"]}'

	raise NotImplementedError(
		'midi maps without a note or index are not implemented'
	)


CONTROL_LIST = list(
	chain(
		*[
			[
				MappableControl(
					name=f'layer{n}select',
					address=f'/composition/layers/{n}/selected',
					sendMessage=f'/composition/layers/{n}/select'
				),
				MappableControl(
					name=f'layer{n}fader',
					address=f'/composition/layers/{n}/video:Opacity',
				),
				MappableControl(
					name=f'layer{n}knob',
					address=f'/composition/layers/{n}/video:Opacity',
				),
			] for n in range(1, 9)
		]
	)
)
CONTROLS = {ctrl['name']: ctrl for ctrl in CONTROL_LIST}


class MidiDeviceExt(ABC, BaseExt):
	State: str
	DeviceID: Optional[int]

	@property
	@abstractmethod
	def name(self) -> str:
		...

	@property
	@abstractmethod
	def mappings(self) -> dict[str, MidiMap]:
		...

	@property
	def ctrlSrcName(self):
		return f'midi-out:{self.name}'

	def Connect(self, deviceID: int) -> None:
		...

	def __init__(self, ownerComponent: OP, logger):
		BaseExt.__init__(self, ownerComponent, logger)

		TDF = op.TDModules.mod.TDFunctions
		TDF.createProperty(self, 'DeviceID', None)
		TDF.createProperty(self, 'State', 'uninitialized')

		self.machine = Machine(
			model=self,
			states=[
				'uninitialized', 'connecting', 'connected', 'connection_unavailable',
				'disconnected'
			],
			initial=self.State,
			model_attribute='State',
			transitions=[
				{
					'trigger': 'Connect',
					'source': '*',
					'dest': 'connection_unavailable',
					'unless': 'isConnectionAvailable'
				},
				{
					'trigger': 'Connect',
					'source': ['uninitialized', 'connection_unavailable', 'disconnected'],
					'dest': 'connecting',
				},
				{
					'trigger': 'Disconnect',
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
				},
				# TODO: refresh status?
			]
		)

		self.ownerComponent = ownerComponent
		self.midiIn = cast(CHOP, ownerComponent.op('midiin1'))
		self.midiOut = cast(midioutCHOP, ownerComponent.op('midiout1'))

		self.midiInputs = cast(DAT, op('/local/midi/midi_inputs'))
		self.midiOutputs = cast(DAT, op('/local/midi/midi_outputs'))
		self.midiDevice = cast(DAT, op('/local/midi/device'))

		self.uiState = cast(ui_state_ext.UIStateExt, op.ui_state.ext.UIStateExt)

		self.logInfo('initialized')

	def __del__(self):
		# Ensure we disconnect gracefully on teardown
		# NOTE: this is only really relevant during development
		if self.State == 'connected':
			self.Disconnect()  # TODO: rename to Disconnect?

	@abstractmethod
	def setupDevice(self) -> None:
		pass

	def isConnectionAvailable(self, deviceID: Optional[int]):  # noqa: ARG002
		# TODO: should we do this in the midi manager rather than each device?
		mod('/sys/devices/midi/initDevice').onStart()

		# TD pattern matching doesn't support spaces, so replace them with "?"
		matchableName = self.name.replace(' ', '?')

		if not (
			self.midiInputs.findCell(matchableName)
			and self.midiInputs.findCell(matchableName)
		):
			self.logWarning(
				f'unable to activate midi control, "{self.name}" is not connected'
			)
			return False

		return True

	def configureDevice(self):
		midiConfig = [
			self.DeviceID,  # id
			self.name,  #     inDevice
			self.name,  #     outDevice
			'',  #            definition
			self.DeviceID,  # channel
		]

		if self.midiDevice.row(str(self.DeviceID)):
			self.midiDevice.replaceRow(str(self.DeviceID), midiConfig)
		else:
			self.midiDevice.appendRow(midiConfig)

	####
	# State Machine Callbacks
	####

	def on_enter_connecting(self, deviceID: int):
		self.logInfo(f'connecting to "{self.name}"')
		self.DeviceID = deviceID
		self.configureDevice()

	def on_enter_connected(self):
		self.logInfo(f'connected to "{self.name}"')
		# Activate midi chops
		self.setupDevice()
		self.registerHandlers()

	def on_exit_connected(self):
		self.logInfo(f'disconnected from "{self.name}"')
		self.deregisterHandlers()

	####
	# End State Machine Callbacks
	####

	def registerHandlers(self):
		# [print(address) for mapping in MappableControl]
		self.uiState.RegisterCtrl(
			'/composition/layers/1/video:Opacity',
			self.ctrlSrcName,
			self.onCtrlValueChange,
			alwaysRequestValue=True
		)

	def deregisterHandlers(self):
		self.uiState.DeregisterCtrl(
			'/composition/layers/1/video:Opacity', self.ctrlSrcName
		)

	def onCtrlValueChange(
		self,
		address: str,  # noqa: ARG002
		value: ui_state_ext.OSCValue
	) -> None:
		# TODO: map oscValue to deviceValue using mapping table
		self.midiOut.sendControl(1, 48, value)

	def OnDeviceValueChange(self, midiAddress: str, value: ui_state_ext.OSCValue):
		# if midiAddress not in self.mappings:
		# self.LogWarning('foo')
		# if type is "msg", send with no value
		#   - self.uiState.SendMessage ???
		# if type is "ctrl", use map to map/normalize midi value
		#   - self.uiState.UpdateCtrlValue
		debug('recieved: ', midiAddress, value)
