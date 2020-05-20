from collections import OrderedDict
from fnmatch import fnmatchcase

TDJ = op.TDModules.mod.TDJSON


class OscDispatcher:
	def __init__(self, initialMappings=None):
		self.mappings = OrderedDict(initialMappings or {})

	def map(self, address, handler):
		self.mappings[address] = handler

	def matchHandler(self, address):
		for mappedAddress, handler in self.mappings.items():
			if fnmatchcase(address, mappedAddress):
				return handler

		return None

	def dispatch(self, address, *args):
		handler = self.matchHandler(address)
		assert handler, 'unmatched osc address {}'.format(address)

		handler(address, *args)


def getCellValues(datRow):
	return [cell.val for cell in datRow]


class StateRender:  # pylint: disable=too-many-instance-attributes
	def __init__(self, ownerComponent, compCtrl, deckCtrl, clipCtrl):
		self.ownerComponent = ownerComponent
		self.renderState = ownerComponent.op('text_renderState')
		self.errors = ownerComponent.op('error1')
		self.compCtrl = compCtrl
		self.deckCtrl = deckCtrl
		self.clipCtrl = clipCtrl
		self.state = None
		self.dirty = False

		self.dispatcher = OscDispatcher(
			{
				'/composition/layers/*/clips/*/connect': self.compCtrl.ConnectClip,
				'/composition/layers/*/clips/*/clear': self.compCtrl.ClearClip,
				'/composition/layers/*/clips/*/source/load': self.compCtrl.LoadClip,
			}
		)

		# TODO: support "savable" compositions
		self.InitalizeState()

	def InitalizeState(self):
		self.state = {'clips': [], 'decks': [], 'errors': []}
		self.OnDeckStateChange(sendState=False)
		self.OnClipStateChange(sendState=False)
		self.sendState()

	def ReceiveMessage(self, address, *args):
		self.dispatcher.dispatch(address, *args)

	def OnDeckStateChange(self, sendState=True):
		state = []
		for index, listRow in enumerate(self.deckCtrl.DeckList.rows()):
			deck = self.deckCtrl.GetDeckOp(index)

			state.append(
				{
					'name': listRow[0].val,
					'layers': [getCellValues(layer) for layer in deck.rows()],
				}
			)

		self.state['decks'] = state
		if sendState:
			self.sendState()

	def OnClipStateChange(self, sendState=True):
		self.state['clips'] = [
			getCellValues(clip) for clip in self.clipCtrl.ClipState.rows()
		]

		if sendState:
			self.sendState()

	def OnErrorStateChange(self, sendState=True):
		self.state['errors'] = [getCellValues(error) for error in self.errors.rows()]

		if sendState:
			self.sendState()

	def sendState(self):
		self.dirty = True
		# Batch state changes to once per frame, this also helps
		# with races from multiple changes occuring close together
		# TODO: I think there might still be a race here
		run('args[0].flushState()', self, delayFrames=1)

	def flushState(self):
		if not self.dirty:
			return

		TDJ.jsonToDat(self.state, self.renderState)
		self.dirty = False
