from abc import ABC, abstractmethod
from dataclasses import dataclass
from itertools import chain
from typing import Callable, Optional, Protocol, Union, cast

from logger import logging_mixins
from transitions import Machine
from ui_state import ui_state_ext


@dataclass
class MappableControl():
	name: str
	oscAddress: str
	sendMessage: Optional[str] = None


@dataclass
class _MidiMap(ABC):
	control: MappableControl
	channel: int

	@property
	@abstractmethod
	def midiAddress(self) -> str:
		...


@dataclass
class MidiNoteMap(_MidiMap):
	note: int

	@property
	def midiAddress(self):
		return f'ch{self.channel}n{self.note}'


@dataclass
class MidiCtrlMap(_MidiMap):
	index: int
	pickup: bool = False

	@property
	def midiAddress(self):
		return f'ch{self.channel}ctrl{self.index}'


MidiMap = Union[MidiNoteMap, MidiCtrlMap]

CONTROL_LIST = list(
	chain(
		*[
			[
				MappableControl(
					name=f'layer{n}select',
					oscAddress=f'/composition/layers/{n}/selected',
					sendMessage=f'/composition/layers/{n}/select'
				),
				MappableControl(
					name=f'layer{n}fader',
					oscAddress=f'/composition/layers/{n}/video:Opacity',
				),
				MappableControl(
					name=f'layer{n}knob',
					oscAddress=f'/composition/layers/{n}/video:Opacity',
				),
			] for n in range(1, 9)
		]
	)
)
CONTROLS = {ctrl.name: ctrl for ctrl in CONTROL_LIST}


class ConnectFn(Protocol):

	def __call__(self, deviceID: int) -> None:
		...


class MidiDeviceExt(ABC, logging_mixins.ComponentLoggerMixin):
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
	def ctrlOutSrcName(self):
		return f'midi-out:{self.name}'

	@property
	def ctrlInSrcName(self):
		return f'midi-in:{self.name}'

	@property
	def mappedOscAddresses(self) -> set[str]:
		return {mapping.control.oscAddress for mapping in self.mappings.values()}

	# Triggers defined by the statemachine
	Connect: ConnectFn
	Disconnect: Callable[[], None]

	def __init__(self, ownerComponent: OP):
		self.ownerComponent = ownerComponent

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
		for oscAddress in self.mappedOscAddresses:
			self.uiState.RegisterCtrl(
				oscAddress,
				self.ctrlOutSrcName,
				self.onCtrlValueChange,
				alwaysRequestValue=True
			)

	def deregisterHandlers(self):
		for oscAddress in self.mappedOscAddresses:
			self.uiState.DeregisterCtrl(oscAddress, self.ctrlOutSrcName)

	def onCtrlValueChange(
		self, address: str, value: ui_state_ext.OSCValue
	) -> None:
		mappings = [
			mapping for mapping in self.mappings.values()
			if mapping.control.oscAddress == address
		]

		for mapping in mappings:
			self.logDebug(f'{mapping.midiAddress}:{value} <- {self.ctrlOutSrcName}')
			if isinstance(mapping, MidiCtrlMap):
				self.midiOut.sendControl(mapping.channel, mapping.index, value)
			else:
				raise NotImplementedError(f'unimplemented mapping type: {type(mapping)}')
		# mappings = [self.]
		# self.logDebug(f'{midiAddress}:{value} -> {self.ctrlOutSrcName}')

	def OnDeviceValueChange(self, midiAddress: str, value: ui_state_ext.OSCValue):
		"""
		TODO: ignore inputs if system isn't loaded?
		"""
		if midiAddress not in self.mappings:
			self.logWarning(f'unmapped midi address: {midiAddress}')
			return

		mapping = self.mappings[midiAddress]
		self.logDebug(f'{self.ctrlInSrcName}:{value} -> {midiAddress}')

		# TODO: support "pickup" values

		# TODO:
		#   if type is "msg", send with no value
		#     - self.uiState.SendMessage ???
		#   if type is "note", ???
		#   if type is Ctrl
		if isinstance(mapping, MidiCtrlMap):
			self.uiState.UpdateCtrlValue(
				mapping.control.oscAddress,
				value,
				self.ctrlInSrcName,
				pickup=mapping.pickup
			)
		else:
			self.logWarning(f'unsupported midi mapping type: {type(mapping)}')
