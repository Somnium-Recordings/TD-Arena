from collections import OrderedDict
from dataclasses import dataclass
from fnmatch import fnmatch
from itertools import chain
from typing import Optional, Protocol, Union
from weakref import ReferenceType, ref

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
	handlerRef: ref[Handler]
	handleValueRequests: bool = False


SubscriberMap = dict[str, Subscriber]


@dataclass
class AddressMapping:
	subscribers: SubscriberMap


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
				mapping.subscribers if mapping else SubscriberMap()
			)
			self.addressMappings[address] = mapping

		self.Map(target, address, handler)

		if mapping.currentValue:
			self.logDebug(
				f'currentValue known, calling handler immediately {address}@{target}'
			)
			handler(address, mapping.currentValue)
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
	) -> None:
		if address not in self.addressMappings:
			self.addressMappings[address] = AddressMapping(SubscriberMap())

		addressMapping = self.addressMappings[address]

		if str(target) in addressMapping.subscribers:
			# TODO: can we use WeakKeyDictionary + finalize to automatically unsubscribe?
			# This happens if components don't Unmap on __del__
			self.logWarning(f'overwriting existing mapping for {address}@{target}')

		self.logDebug(f'mapping {address}@{target}')
		addressMapping.subscribers[str(target)] = Subscriber(
			ref(handler, self.Unmap), handleValueRequests=handleValueRequests
		)

	def MapMultiple(self, target: OP, mapping: OrderedDict[str, Handler]) -> None:
		...

	def Unmap(
		self,
		unmapTarget: Union[OP, ReferenceType[Handler]],
		unmapAddress: Optional[str] = None
	) -> None:
		self.logDebug(
			'processing unmap request for %s@%s, ', unmapAddress or 'any', unmapTarget
		)
		matchedMappings = [
			(address, mapping)
			for address, mapping in self.addressMappings.items()
			if unmapAddress is None or address == unmapAddress
		]

		subscribersToClear = list[tuple[str, str]]()
		for address, mapping in matchedMappings:
			subscribersToClear += [
				(address, target)
				for target, subscriber in mapping.subscribers.items()
				if unmapTarget in (target, subscriber.handlerRef)
			]

		self.logDebug('found %i targets to clear', len(subscribersToClear))

		for address, source in subscribersToClear:
			self.logDebug('unmapping %s@%s', address, source)
			del self.addressMappings[address].subscribers[source]

		for address, mapping in matchedMappings:
			if not mapping.subscribers:
				self.logDebug('clearing empty address mapping %s', address)
				del self.addressMappings[address]

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
			handler = subscriber.handlerRef()
			if handler is not None:
				handler(address, *values)

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
