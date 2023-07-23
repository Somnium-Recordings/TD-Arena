from collections import OrderedDict
from dataclasses import dataclass
from fnmatch import fnmatch
from itertools import chain
from typing import Optional, Protocol, Union

from logger import logging_mixins
from tdaUtils import matchesType

OSCValue = Union[str, int, float, bool, list[int], list[float]]


class OSCValueHandler(Protocol):

	def __call__(self, updatedValue: OSCValue) -> None:
		...


class OSCUpdateHandler(Protocol):

	def __call__(self, address: str, updatedValue: OSCValue) -> None:
		...


class AddressMapper(Protocol):

	def __call__(self, address: str) -> str:
		...


@dataclass
class OSCListener():
	handler: OSCUpdateHandler


@dataclass
class OSCValueListener():
	handler: OSCValueHandler


@dataclass
class OSCControl():
	handler: OSCUpdateHandler
	alwaysRequestValue: bool = False


# Mapping = Union[OSCValueHandler, OSCListener, OSCValueListener, OSCControl]
Handler = Union[OSCUpdateHandler]


@dataclass
class Subscriber():
	handler: Handler
	handleValueRequests: bool = False


SubscriberList = dict[str, Subscriber]


@dataclass
class AddressMapping:
	subscribers: SubscriberList


@dataclass
class TrackedAddressMapping(AddressMapping):
	initialValueRequested: bool = False
	currentValue: Optional[OSCValue] = None


class OSCDispatcher(logging_mixins.ComponentLoggerMixin):

	def __init__(self, ownerComponent: OP) -> None:
		self.ownerComponent = ownerComponent
		self.addressMappings = dict[str, AddressMapping]()

	def MapControl(self, target: OP, address: str, handler: Handler) -> None:
		mapping = self.addressMappings.get(address, None)

		if not isinstance(mapping, TrackedAddressMapping):
			mapping = TrackedAddressMapping(
				mapping.subscribers if mapping else SubscriberList()
			)
			self.addressMappings[address] = mapping

		subscriber = self.Map(target, address, handler)

		if mapping.currentValue:
			self.logDebug(
				f'currentValue known, calling handler immediately {address}@{target}'
			)
			subscriber.handler(address, mapping.currentValue)
		elif not mapping.initialValueRequested:
			self.logDebug(f'requesting initial value for {address}@{target}')
			self.Dispatch(target, address, '?')
			mapping.initialValueRequested = True

		# if we don't have a current value, dispatch(target, address, ?)
		#    OR always_request_value = True  --- Do we really need this?
		# if we do, immediately call the handler
		#
		# ensure address does not contain wildcards
		# promote AddressMapping to TrackedAddressMapping

	def Map(
		self,
		target: OP,
		address: str,
		handler: Handler,
		*,
		handleValueRequests: bool = False
	) -> Subscriber:
		if address not in self.addressMappings:
			self.addressMappings[address] = AddressMapping(SubscriberList())

		subscriber = Subscriber(handler, handleValueRequests=handleValueRequests)
		self.addressMappings[address].subscribers[str(target)] = subscriber

		return subscriber

	def MapMultiple(self, target: OP, mapping: OrderedDict[str, Handler]) -> None:
		...

	def Unmap(self, target: OP, address: Optional[str]) -> None:
		...

	def Dispatch(self, source: OP, address: str, *values: OSCValue) -> None:
		addressMappings = self.getMatchingMappings(address)
		if not addressMappings:
			self.logWarning(f'{source} dispatched unmatched OSC address {address}')
			return

		self.logDebug(f'{source} dispatching {address} with {values}')

		isCurrentValueRequest = len(values) == 1 and values[0] == '?'
		if not isCurrentValueRequest:
			valueHasChanged = self.updateTrackedValues(addressMappings, values)
			if not valueHasChanged:
				self.logDebug(f'{address} unchanged, skipping handler calls')
				return

		# if source is a control and pickup enabled, ignore value unless
		# in sync or it has "crossed the current value"

		matchedSubscribers = self.matchSubscribers(
			source, addressMappings, isCurrentValueRequest=isCurrentValueRequest
		)

		if not matchedSubscribers:
			self.logWarning(
				f'{source} dispatched {address}:{values} but no subscribers found'
			)
			return

		for subscriber in matchedSubscribers:
			# TODO: if not op(target).valid, unregister control and log warning
			subscriber.handler(address, *values)

	def getMatchingMappings(self, address: str) -> list[AddressMapping]:
		return [
			addressMapping
			for mappedAddress, addressMapping in self.addressMappings.items()
			if fnmatch(address, mappedAddress)
		]

	def updateTrackedValues(
		self, addressMappings: list[AddressMapping], values: tuple[OSCValue, ...]
	) -> bool:
		"""
		Returns whether at least one tracked value has changed or not
		"""
		trackedAddressMappings = matchesType(addressMappings, TrackedAddressMapping)

		if not trackedAddressMappings:
			# We have no way to know if a value has changed or not when its not tracked
			# so always mark it changed in these cases
			return True

		hasChanged = False

		for mapping in trackedAddressMappings:
			if mapping.currentValue != values[0]:
				hasChanged = True
				mapping.currentValue = values[0]

		return hasChanged

	def matchSubscribers(
		self, source: OP, addressMappings: list[AddressMapping], *,
		isCurrentValueRequest: bool
	) -> list[Subscriber]:
		matchedSubscribers = chain.from_iterable(
			addressMapping.subscribers.items() for addressMapping in addressMappings
		)

		return [
			mapping for target, mapping in matchedSubscribers if (
				str(source) != target and
				(not isCurrentValueRequest or mapping.handleValueRequests)
			)
		]
