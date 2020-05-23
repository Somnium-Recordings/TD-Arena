TDJ = op.TDModules.mod.TDJSON


def getCellValues(datRow):
	return [cell.val for cell in datRow]


# TODO: StateRender shouldn't need to depend on deckCtrl and clipCtrl
class StateRender:  # pylint: disable=too-many-instance-attributes
	def __init__(self, ownerComponent, logger, deckCtrl, clipCtrl):
		self.ownerComponent = ownerComponent
		self.logger = logger
		self.renderState = ownerComponent.op('text_renderState')
		self.errors = ownerComponent.op('error1')
		self.deckCtrl = deckCtrl
		self.clipCtrl = clipCtrl
		self.state = None
		self.dirty = False

		# TODO: support "savable" compositions
		self.InitalizeState()
		self.logInfo('initilized')

	def InitalizeState(self):
		self.state = {'clips': [], 'decks': [], 'errors': []}
		# self.OnDeckStateChange(sendState=False)
		# self.OnClipStateChange(sendState=False)
		self.sendState()

	def Update(self, key, newState):
		self.state[key] = newState
		self.sendState()

	# def OnDeckStateChange(self, sendState=True):
	# 	state = []
	# 	# TODO: get list of decks here rather than depending on the deckCtrl and clipCtrls
	# 	for index, listRow in enumerate(self.deckCtrl.DeckList.rows()):
	# 		deck = self.deckCtrl.GetDeckOp(index)

	# 		state.append(
	# 			{
	# 				'name': listRow[0].val,
	# 				'layers': [getCellValues(layer) for layer in deck.rows()],
	# 			}
	# 		)

	# 	self.state['decks'] = state
	# 	if sendState:
	# 		self.sendState()

	def OnClipStateChange(self, sendState=True):
		# TODO: can we just watch the clipState dat rather than each clip?
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

	def logInfo(self, *args):
		self.logger.Info(self.ownerComponent, *args)
