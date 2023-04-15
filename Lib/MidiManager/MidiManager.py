from tda import BaseExt


class MidiManager(BaseExt):

	def __init__(self, ownerComponent, logger):  # noqa: ANN001
		super().__init__(ownerComponent, logger)
		self.logInfo('MidiManager Initalized')

	def Load(self):
		pass
