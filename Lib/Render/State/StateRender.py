import json

from tda import BaseExt
from tdaUtils import getCellValues


def compositionPath(name):
	return tdu.expandPath('composition://{}.json'.format(name))


# TODO: StateRender shouldn't need to depend on deckCtrl and clipCtrl
class StateRender(BaseExt):
	def __init__(self, ownerComponent, logger, deckCtrl, clipCtrl):
		super().__init__(ownerComponent, logger)
		self.stateOut = ownerComponent.op('udpout_state')
		self.errors = ownerComponent.op('error1')
		self.deckCtrl = deckCtrl
		self.clipCtrl = clipCtrl

		self.CurrentState = {}  # track state for saving/loading
		self.logInfo('initilized')

	def Update(self, key, newState):
		self.CurrentState[key] = newState
		self.stateOut.send(json.dumps({key: newState}))

	def Get(self, key, default):
		return self.CurrentState[key] if key in self.CurrentState else default

	def OnErrorStateChange(self):
		self.Update('errors', [getCellValues(error) for error in self.errors.rows()])

	def Save(self, compositionName):
		filePath = compositionPath(compositionName)
		self.logInfo('saving state to {}'.format(filePath))

		with open(filePath, 'w') as compositionFile:
			json.dump(self.CurrentState, compositionFile, indent='\t')

	def Load(self, compositionName):
		filePath = compositionPath(compositionName)
		self.logInfo('loading state from {}'.format(filePath))

		with open(filePath) as compositionFile:
			self.CurrentState = json.load(compositionFile)
