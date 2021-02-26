from collections import OrderedDict
from fnmatch import fnmatchcase

from tda import BaseExt
from tdaUtils import (getLayerID, mapAddressToDeckLocation,
                      mapAddressToEffectContainer, mapAddressToEffectLocation)


class OSCDispatcher(BaseExt):
	def __init__(
		self, ownerComponent, logger, renderState, compositionCtrl, layerCtrl,
		deckCtrl, clipCtrl, effectCtrl, parameterCtrl
	):  # pylint: disable=too-many-arguments
		super().__init__(ownerComponent, logger)
		self.renderState = renderState
		self.compositionCtrl = compositionCtrl
		self.layerCtrl = layerCtrl
		self.deckCtrl = deckCtrl
		self.effectCtrl = effectCtrl
		self.clipCtrl = clipCtrl
		self.parameterCtrl = parameterCtrl
		self.compositionContainer = ownerComponent.op('../composition')
		self.oscIn = ownerComponent.op('./oscin1')
		self.Init()

	def Init(self):
		self.mappings = OrderedDict(
			{
				'?': {
					'handler': self.parameterCtrl.ReplyWithCurrentValue
				},
				'/composition/load': {
					'handler': self.renderState.Load,
					'sendAddress': False
				},
				'/composition/reinit': {
					'handler': self.renderState.Init,
					'sendAddress': False
				},
				'/composition/new': {
					'handler': self.renderState.New,
					'sendAddress': False
				},
				'/composition/save': {
					'handler': self.renderState.Save,
					'sendAddress': False
				},
				'/composition/clips/*/select': {
					'handler': self.deckCtrl.SelectClip
				},
				'/composition/clips/*/video/effects/add': {
					'handler': self.effectCtrl.AddEffect,
					'mapAddress': mapAddressToEffectContainer
				},
				'/composition/clips/*/video/effects/*/clear': {
					'handler': self.effectCtrl.ClearEffect,
					'mapAddress': mapAddressToEffectLocation
				},
				'/composition/clips/*/video/effects/*/move': {
					'handler': self.effectCtrl.MoveEffect,
					'mapAddress': mapAddressToEffectLocation
				},
				'/composition/layers/*/clear': {
					'handler': self.layerCtrl.Clear,
					'mapAddress': getLayerID
				},
				'/composition/layers/*/video/effects/add': {
					'handler': self.effectCtrl.AddEffect,
					'mapAddress': mapAddressToEffectContainer
				},
				'/composition/layers/*/video/effects/*/clear': {
					'handler': self.effectCtrl.ClearEffect,
					'mapAddress': mapAddressToEffectLocation
				},
				'/composition/layers/*/video/effects/*/move': {
					'handler': self.effectCtrl.MoveEffect,
					'mapAddress': mapAddressToEffectLocation
				},
				'/composition/decks/*/select': {
					'handler': self.deckCtrl.SelectDeck
				},
				'/composition/layers/*/select': {
					'handler': self.layerCtrl.SelectLayer
				},
				'/selecteddeck/layers/*/clips/*/connect': {
					'handler': self.deckCtrl.ConnectClip,
					'mapAddress': mapAddressToDeckLocation
				},
				'/selecteddeck/layers/*/clips/*/clear': {
					'handler': self.deckCtrl.ClearClip,
					'mapAddress': mapAddressToDeckLocation
				},
				'/selecteddeck/layers/*/clips/*/source/load': {
					'handler': self.deckCtrl.LoadClip,
					'mapAddress': mapAddressToDeckLocation
				},
				'/selecteddeck/layers/*/clips/*/video/effects/add': {
					'handler': self.deckCtrl.AddEffect,
					'mapAddress': mapAddressToDeckLocation
				},
				'/selecteddeck/layers/*/insert': {
					'handler': self.deckCtrl.InsertLayer,
					'mapAddress': getLayerID
				},
				'/selecteddeck/layers/*/remove': {
					'handler': self.deckCtrl.RemoveLayer,
					'mapAddress': getLayerID
				},
			}
		)
		self.logInfo('initialized')

	def Map(self, address, handler):
		self.mappings[address] = handler

	def MapMultiple(self, mappings):
		for address, handler in mappings.items():
			self.Map(address, handler)

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

	def Reply(self, address, *args):
		self.logDebug(f'Render -> UI -- {address}:{args}')
		self.oscIn.sendOSC(address, args)

	def getMapping(self, address, args):
		if (len(args) == 1 and args[0] == '?'):
			return self.getMapping('?', [])

		for mappedAddress, mapping in self.mappings.items():
			if fnmatchcase(address, mappedAddress):
				return mapping

		return None
