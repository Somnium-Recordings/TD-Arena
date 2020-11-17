from tda import LoadableExt
from tdaUtils import (clearChildren, getCellValues, getLayerID, intIfSet,
                      layoutComps)


class LayerCtrl(LoadableExt):
	@property
	def LayerCount(self):
		return max(0, len(self.layers) - 1) if self.Loaded else 0

	def __init__(self, ownerComponent, logger, clipCtrl, thumbnails):  # pylint: disable=too-many-arguments
		super().__init__(ownerComponent, logger)
		self.clipCtrl = clipCtrl
		self.thumbnails = thumbnails
		self.layerTemplate = ownerComponent.op('./layerTemplate0')
		self.composition = ownerComponent.op('../composition')
		self.layerList = ownerComponent.op('./table_layerIDs')
		self.layerState = ownerComponent.op('./null_layerState')
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
		self.layerList.clear()

		self.logInfo('initialized')

	def Load(self, saveState=None):
		self.setLoading()
		self.logInfo('loading composition from state {}')

		state = saveState or self.createDefaultState()
		for layer in state[1:]:
			(layerID, layerName, clipID) = layer
			self.createLayer(layerID, layerName, clipID, 'add')

		self.logInfo('loaded {} layers in composition'.format(len(self.layers)))
		self.setLoaded()

	def GetSaveState(self):
		return [
			getCellValues(layer) for layer in self.layerState.rows()
		] if self.Loaded else None

	def createDefaultState(self):
		state = [
			['Id', 'Layername', 'Clipid'],
			['0', 'Composition', ''],
		]

		for i in range(self.composition.par.Layercount.eval()):
			layerID = i + 1
			state.append([str(layerID), 'Layer{}'.format(layerID), ''])

		return state

	def ClearClipID(self, clipID: int):
		assert self.layers, 'cloud not clear clip ID, layers not loaded'

		for layer in self.layers:
			if layer.par.Clipid == str(clipID):
				layer.par.Clipid = None

		self.clipCtrl.DeleteClip(clipID)

	def SetClip(self, layerNumber, clipID: int):
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

	def SelectLayer(self, address):
		layerID = getLayerID(address)
		self.composition.par.Previstarget = f'composition/layers/layer{layerID}/null_previs'
		self.composition.par.Selectedlayer = layerID

	def createLayer(self, layerNumber, layerName, clipId, operand):
		opName = 'layer{}'.format(layerNumber)
		self.logDebug('creating layer: {}'.format(opName))

		newLayer = self.layerContainer.copy(self.layerTemplate, name=opName)
		# TODO: be smarter about this, direct map?
		newLayer.par.Clipid = clipId
		newLayer.par.Operand = operand
		newLayer.par.Layername = layerName

		self.layers.append(newLayer)
		self.layerList.appendRow([layerNumber])

		self.layoutLayerContainer()

		return newLayer

	def layoutLayerContainer(self):
		layoutComps(self.layers, columns=1)
