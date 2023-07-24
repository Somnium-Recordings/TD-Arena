from typing import cast

from logger import logging_mixins

from .midi_device_ext import MidiDeviceExt

# TODO:
#   - Connect automatically if not connected when composition is loaded
#   - Unbind handlers / disconnect when composition unloaded


class MidiManagerExt(logging_mixins.ComponentLoggerMixin):
	ConnectionUnavailable: bool

	@property
	def State(self) -> str:
		return self.targetDevice.State

	def __init__(self, ownerComponent: OP):
		self.ownerComponent = ownerComponent

		self.targetDevice = cast(MidiDeviceExt, ownerComponent.op('./device_APC40'))

		self.logInfo('initialized')

	def Toggle(self):
		if self.targetDevice.State in ['connecting', 'connected']:
			self.targetDevice.Disconnect()
		else:
			self.targetDevice.Connect(deviceID=1)
