from tdaUtils import intIfSet, layoutComps


class LayerCtrl:
	@property
	def LayerCount(self):
		return self.composition.par.Layers

	def __init__(self, ownerComponent, logger):
		self.ownerComponent = ownerComponent
		self.logger = logger

		self.deckTemplate = ownerComponent.op('./layerTemplate0')

		# NOTE: These lines should be mirrored in Reinit
		self.composition = None
		self.layerContainer = None
		self.layers = None
		self.logInfo('initialized')

	def Reinit(self):
		self.composition = None
		self.layerContainer = None
		self.layers = None
		self.logInfo('reinitialized')

	def Load(self):
		self.logInfo('loading composition')

		self.composition = self.ownerComponent.op('../composition')
		assert self.composition, 'could not find composition component'

		self.layerContainer = self.composition.op('layers')
		if not self.layerContainer:
			self.logInfo('layers op not found in composition, initalizing')
			self.layerContainer = self.composition.create(baseCOMP, 'layers')

		self.layers = {}
		# NOTE: count + 1 since layer 0 is the "master" layer
		for i in range(self.LayerCount + 1):
			layerName = 'layer{}'.format(i)
			self.layers[layerName] = self.findOrCreateLayer(layerName)

		self.layoutLayerContainer()

		self.logInfo('loaded {} layers in composition'.format(self.LayerCount))

	def ClearClipID(self, clipID):
		assert self.layers, 'cloud not clear clip ID, layers not loaded'

		for layer in self.layers.values():
			if layer.par.Clipid == str(clipID):
				layer.par.Clipid = None

	def SetClip(self, layerID, clipID):
		offsetLayerID = layerID + 1  # layer 0 is master
		layer = self.layers.get(offsetLayerID, None)
		assert layer, 'could not set clip for unknown layer ID{}'.format(layerID)
		layer = self.layers[offsetLayerID]

		previousClipID = intIfSet(layer.par.Clipid.val)
		layer.par.Clipid = clipID

		return previousClipID

	def createLayer(self, layerName):
		self.logInfo('creating layer: {}'.format(layerName))
		return self.layerContainer.copy(self.deckTemplate, name=layerName)

	def findOrCreateLayer(self, layerName):
		existingDeck = self.layerContainer.op('./' + layerName)

		return existingDeck or self.createLayer(layerName)

	def layoutLayerContainer(self):
		layoutComps(self.layers.values(), columns=1)

	def logInfo(self, *args):
		self.logger.Info(self.ownerComponent, *args)
