from collections import OrderedDict
from fnmatch import fnmatchcase
from typing import Callable

from tda import BaseExt
from typing_extensions import Required, TypedDict


class OSCHandler(TypedDict, total=False):
	handler: Required[Callable]
	sendAddress: bool
	mapAddress: Callable[[str], str]


OSCMappings = OrderedDict[str, OSCHandler]


class OSCDispatcher(BaseExt):

	def __init__(
		self,
		ownerComponent,  # noqa: ANN001
		logger,  # noqa: ANN001
		mappings=None,  # noqa: ANN001
		defaultMapping=None  # noqa: ANN001
	) -> None:
		super().__init__(ownerComponent, logger)
		self.mappings: OSCMappings = mappings if mappings else OrderedDict()
		self.defaultMapping = defaultMapping

		self.logInfo('OSCDispatcher initialized')

	def Map(self, address: str, handler: OSCHandler):
		self.mappings[address] = handler

	def MapMultiple(self, mappings: OSCMappings):
		for address, handler in mappings.items():
			self.Map(address, handler)

	def getMapping(self, address: str, args):  # noqa: ANN001
		if (len(args) == 1 and args[0] == '?'):
			return self.getMapping('?', [])

		for mappedAddress, mapping in self.mappings.items():
			if fnmatchcase(address, mappedAddress):
				return mapping

		# We explicitly use defaultMapping instead of `*` so that uiState
		# can define a default that doesn't take precedence over mappings
		# added later. For example from the TdArena class.
		return self.defaultMapping

	def Dispatch(self, address, *args):  # noqa: ANN001, ANN002
		mapping = self.getMapping(address, args)
		assert mapping, f'unmapped osc address {address}'

		handler = mapping.get('handler', None)
		assert handler, f'expected handler to be defined for {address}'

		self.logDebug(f'dispatching {address} with {args}')

		if 'mapAddress' in mapping:
			address = mapping['mapAddress'](address)

		if mapping.get('sendAddress', True):
			handler(address, *args)
		else:
			handler(*args)
