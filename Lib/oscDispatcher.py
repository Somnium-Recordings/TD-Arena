from collections import OrderedDict
from fnmatch import fnmatchcase
from typing import Any, Callable, Optional, Protocol, TypeVar, Union

from logger import logging_mixins
from typing_extensions import Required, TypedDict

OSCValue = Union[str, int, float, bool, list[int], list[float]]
_OSCValue_contra = TypeVar(
	'_OSCValue_contra', bound=OSCValue, contravariant=True
)


class OSCHandlerAddressCallback(Protocol[_OSCValue_contra]):

	def __call__(self, address: str, newValue: _OSCValue_contra) -> None:
		...


class OSCHandlerCallback(Protocol[_OSCValue_contra]):

	def __call__(self, updatedValue: _OSCValue_contra) -> None:
		...


class OSCHandler(TypedDict, total=False):
	# TODO: handle these types better
	# handler: Required[Union[OSCHandlerCallback, OSCHandlerAddressCallback]]
	handler: Required[Callable]
	sendAddress: bool
	mapAddress: Callable[[str], str]


OSCMappings = OrderedDict[str, OSCHandler]


class OSCDispatcher(logging_mixins.ComponentLoggerMixin):

	def __init__(
		self,
		ownerComponent,  # noqa: ANN001
		logger: Any = None,  # noqa: ARG002, ANN401
		mappings: Optional[OSCMappings] = None,
		defaultMapping=None  # noqa: ANN001
	) -> None:
		self.ownerComponent = ownerComponent
		self.mappings = mappings if mappings else OSCMappings()
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

	def Dispatch(self, address: str, *args: OSCValue):
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
