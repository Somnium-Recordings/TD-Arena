import typing as T
from collections import OrderedDict
from fnmatch import fnmatchcase

from tda import BaseExt

# TODO: when we upgrade to python 3.10 switch to using Required specifiers
# TODO: enable if touch updates to 3.8 wehre TypedDict is around
#       (I don't want to install typing_extensions)
# class OSCHandler(T.TypedDict, total=False):
# 	handler: T.Callable
# 	sendAddress: bool
# 	mapAddress: T.Callable[[str], str]

OSCMappings: T.OrderedDict[str, T.Dict]


class OSCDispatcher(BaseExt):

	def __init__(
		self, ownerComponent, logger, mappings=None, defaultMapping=None
	) -> None:
		super().__init__(ownerComponent, logger)
		self.mappings: OSCMappings = mappings if mappings else OrderedDict()
		self.defaultMapping = defaultMapping

		self.logInfo('OSCDispatcher initialized')

	def Map(self, address, handler):
		self.mappings[address] = handler

	def MapMultiple(self, mappings):
		for address, handler in mappings.items():
			self.Map(address, handler)

	def getMapping(self, address, args):
		if (len(args) == 1 and args[0] == '?'):
			return self.getMapping('?', [])

		for mappedAddress, mapping in self.mappings.items():
			if fnmatchcase(address, mappedAddress):
				return mapping

		# We explicitily use defaultMapping instead of `*` so that uiState
		# can define a default that doesn't take precidence over mappings
		# added later. For example from the TdArena class.
		return self.defaultMapping

	def Dispatch(self, address, *args):
		mapping = self.getMapping(address, args)
		assert mapping, 'unmapped osc address {}'.format(address)

		handler = mapping.get('handler', None)
		assert handler, 'expected handler to be defined for {}'.format(address)

		self.logDebug(f'dispatching {address} with {args}')

		if 'mapAddress' in mapping:
			address = mapping['mapAddress'](address)

		if mapping.get('sendAddress', True):
			handler(address, *args)
		else:
			handler(*args)
