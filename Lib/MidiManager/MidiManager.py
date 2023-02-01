from tda import BaseExt


class MidiManager(BaseExt):

	def __init__(self, ownerComponent, logger):
		super().__init__(ownerComponent, logger)
		self.logInfo('MidiManager Initalized')
