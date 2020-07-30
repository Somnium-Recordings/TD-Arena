from tda import LoadableExt
from tdaUtils import clearChildren, intIfSet, layoutComps

DEFAULT_STATE = [
	['Clipid', 'Operand'], [None, 'add'], [None, 'add'], [None, 'add']
]
STATE_KEY = 'layers'


class LayerCtrl(LoadableExt):
	@property
	def LayerCount(self):
		return max(0, len(self.layers) - 1) if self.Loaded else 0

	def __init__(self, ownerComponent, logger, state, clipCtrl, thumbnails):  # pylint: disable=too-many-arguments
		super().__init__(ownerComponent, logger)
		self.state = state
		self.clipCtrl = clipCtrl
		self.thumbnails = thumbnails
		self.layerTemplate = ownerComponent.op('./layerTemplate0')
		self.composition = ownerComponent.op('../composition')
		assert self.composition, 'could not find composition component'

	def Init(self):
		self.setUnloaded()

		self.layerContainer = self.composition.op('layers')
		if self.layerContainer:
			self.logDebug('clearing layers in composition')
			clearChildren(self.layerContainer)
		else:
			self.logInfo('layers op not found in composition, initalizing')
			self.layerContainer = self.composition.create(baseCOMP, 'layers')

		self.layers = []
		self.SendState()

		self.logInfo('initialized')

	def Load(self):
		self.setLoading()
		self.logInfo('loading composition')

		for layerNumber, layer in enumerate(
			self.state.Get(STATE_KEY, DEFAULT_STATE)[1:]
		):
			(clipID, Operand) = layer
			self.createLayer(layerNumber, clipID, Operand)

		self.logInfo('loaded {} layers in composition'.format(len(self.layers)))
		self.setLoaded()
		self.SendState()

	def ClearClipID(self, clipID):
		assert self.layers, 'cloud not clear clip ID, layers not loaded'

		for layer in self.layers:
			if layer.par.Clipid == str(clipID):
				layer.par.Clipid = None

		self.clipCtrl.DeleteClip(clipID)

	def SetClip(self, layerNumber, clipID):
		offsetLayerID = layerNumber + 1  # layer 0 is master
		assert offsetLayerID < len(
			self.layers
		), 'could not set clip for unknown layer ID {}'.format(layerNumber)
		layer = self.layers[offsetLayerID]

		previousClipID = intIfSet(layer.par.Clipid.val)
		layer.par.Clipid = clipID

		if clipID is not None:
			self.clipCtrl.ActivateClip(clipID)

		if previousClipID is not None and previousClipID != clipID:
			self.clipCtrl.DeactivateClip(previousClipID)

	def createLayer(self, layerNumber, clipId, operand):
		layerName = 'layer{}'.format(layerNumber)
		self.logDebug('creating layer: {}'.format(layerName))

		newLayer = self.layerContainer.copy(self.layerTemplate, name=layerName)
		# TODO: be smarter about this, direct map?
		newLayer.par.Clipid = clipId
		newLayer.par.Operand = operand

		self.layers.append(newLayer)

		self.layoutLayerContainer()

		return newLayer

	def layoutLayerContainer(self):
		layoutComps(self.layers, columns=1)

	def SendState(self):
		self.logDebug('sending state')

		currentState = self.getState()
		self.state.Update('layers', currentState)

		clipIds = [
			# Skip title row and "master" layer for now
			[layer[0]] for layer in currentState[2:]
		] if currentState else None
		self.thumbnails.OnLayerStateUpdate(clipIds)

	def getState(self):
		if not self.Loaded:
			return None

		# NOTE: layer 0 is master
		# TODO: clipName -> Clipname, operand -> Operand
		state = [['Clipid', 'Operand']]
		state.extend([self.getLayerState(layer) for layer in self.layers])

		return state

	def getLayerState(self, layer):  # pylint: disable=no-self-use
		clipID = intIfSet(layer.par.Clipid.eval())

		return [clipID, layer.par.Operand.eval()]
