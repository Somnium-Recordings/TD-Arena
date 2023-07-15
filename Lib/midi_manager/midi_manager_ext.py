from typing import cast

from tda import BaseExt

from .midi_device_ext import MidiDeviceExt

# TODO:
#   - Connect automatically if not connected when composition is loaded
#   - Unbind handlers / disconnect when composition unloaded


class MidiManagerExt(BaseExt):
	ConnectionUnavailable: bool

	@property
	def State(self) -> str:
		return self.targetDevice.State

	def __init__(self, ownerComponent: OP, logger):
		super().__init__(ownerComponent, logger)

		self.targetDevice = cast(MidiDeviceExt, ownerComponent.op('./device_APC40'))

		self.logInfo('initialized')

	def Toggle(self):
		debug('this still work?')
		if self.targetDevice.State in ['connecting', 'connected']:
			self.targetDevice.Disconnect()
		else:
			self.targetDevice.Connect(deviceID=1)
