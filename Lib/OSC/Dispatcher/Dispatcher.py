from collections import OrderedDict
from fnmatch import fnmatchcase


class OSCDispatcher:
	def __init__(self, ownerComponent, logger):
		self.ownerComponent = ownerComponent
		self.logger = logger
		self.mappings = OrderedDict({})
		self.logInfo('OSC Dispatcher initialized')

	def Map(self, address, handler):
		self.mappings[address] = handler

	def MapMultiple(self, mappings):
		for address, handler in mappings.items():
			self.Map(address, handler)

	def Dispatch(self, address, *args):
		mapping = self.getMapping(address)
		assert mapping, 'unmapped osc address {}'.format(address)
		handler = mapping.get('handler', None)
		assert handler, 'expected handler to be defined for {}'.format(address)

		if mapping.get('sendAddress', True):
			handler(address, *args)
		else:
			handler(*args)

	def getMapping(self, address):
		for mappedAddress, mapping in self.mappings.items():
			if fnmatchcase(address, mappedAddress):
				return mapping

		return None

	def logInfo(self, *args):
		self.logger.Info(self.ownerComponent, *args)
