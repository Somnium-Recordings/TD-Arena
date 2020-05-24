from tda import BaseExt
from tdaUtils import getCellValues

TDJ = op.TDModules.mod.TDJSON


# TODO: StateRender shouldn't need to depend on deckCtrl and clipCtrl
class StateRender(BaseExt):
	def __init__(self, ownerComponent, logger, deckCtrl, clipCtrl):
		super().__init__(ownerComponent, logger)
		self.renderState = ownerComponent.op('text_renderState')
		self.errors = ownerComponent.op('error1')
		self.deckCtrl = deckCtrl
		self.clipCtrl = clipCtrl
		self.state = None
		self.dirty = False

		self.InitalizeState()
		self.logInfo('initilized')

	def InitalizeState(self):
		self.state = {'errors': []}
		self.sendState()

	def Update(self, key, newState):
		self.state[key] = newState
		self.sendState()

	def OnErrorStateChange(self, sendState=True):
		self.state['errors'] = [getCellValues(error) for error in self.errors.rows()]

		if sendState:
			self.sendState()

	def sendState(self):
		"""
		TODO: can we use storage and an exec dat -> tdOut to let touch manage emitting changes?
		alternatively, waht if we create a run loop to check every frame?
		   - would that loop keep going if the comp is re-initilized?
		"""
		self.dirty = True
		# Batch state changes to once per frame, this also helps
		# with races from multiple changes occuring close together
		# TODO: I think there might still be a race here
		run('args[0].flushState()', self, delayFrames=1)

	def flushState(self):
		if not self.dirty:
			return

		self.logDebug('flushing satate')
		TDJ.jsonToDat(self.state, self.renderState)
		self.dirty = False
