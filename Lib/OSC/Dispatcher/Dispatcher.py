from collections import OrderedDict
from fnmatch import fnmatchcase

from tda import BaseExt
from tdaUtils import addressToValueLocation, mapAddressToClipLocation


class OSCDispatcher(BaseExt):
	def __init__(
		self, ownerComponent, logger, renderState, compositionCtrl, layerCtrl,
		deckCtrl, clipCtrl
	):  # pylint: disable=too-many-arguments
		super().__init__(ownerComponent, logger)
		self.renderState = renderState
		self.compositionCtrl = compositionCtrl
		self.layerCtrl = layerCtrl
		self.deckCtrl = deckCtrl
		self.clipCtrl = clipCtrl
		self.compositionContainer = ownerComponent.op('../composition')
		self.oscIn = ownerComponent.op('./oscin1')
		self.Init()

	def Init(self):
		self.mappings = OrderedDict(
			{
				'?': {
					'handler': self.returnCurrentValueAtAddress
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
				'/composition/decks/*/select': {
					'handler': self.compositionCtrl.SelectDeck
				},
				'/composition/layers/*/select': {
					'handler': self.compositionCtrl.SelectLayer
				},
				'/composition/layers/*/clips/*/connect': {
					'handler': self.deckCtrl.ConnectClip,
					'mapAddress': mapAddressToClipLocation
				},
				'/composition/layers/*/clips/*/clear': {
					'handler': self.deckCtrl.ClearClip,
					'mapAddress': mapAddressToClipLocation
				},
				'/composition/layers/*/clips/*/source/load': {
					'handler': self.deckCtrl.LoadClip,
					'mapAddress': mapAddressToClipLocation
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

		self.logDebug('dispatching {}'.format(address))

		if 'mapAddress' in mapping:
			address = mapping['mapAddress'](address)

		if mapping.get('sendAddress', True):
			handler(address, *args)
		else:
			handler(*args)

	def OSCReply(self, address, *args):
		"""
		TODO: does this really belong here?
		"""
		self.oscIn.sendOSC(address, args)

	def getMapping(self, address, args):
		if (len(args) == 1 and args[0] == '?'):
			return self.getMapping('?', [])

		for mappedAddress, mapping in self.mappings.items():
			if fnmatchcase(address, mappedAddress):
				return mapping

		return None

	def returnCurrentValueAtAddress(self, address, _):
		(controlPath, parName) = addressToValueLocation(
			address,
			self.compositionContainer.path
		) # yapf: disable

		controlOp = op(controlPath)
		if controlOp is None:
			self.logWarning(
				'could not lookup current value for non-existent op {}'.
				format(controlPath)
			)
			return

		par = getattr(controlOp.par, parName, None)
		if par is None:
			self.logWarning(
				'requested par {} does not exist on {}'.format(parName, controlPath)
			)
			return

		self.logDebug('replying with current value at {}'.format(address))
		currentValue = par.menuIndex if par.isMenu else par.eval()
		self.OSCReply(address, currentValue)
