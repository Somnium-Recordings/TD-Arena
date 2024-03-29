from typing import Optional

from tda import LoadableExt
from tdaUtils import (
	addSectionParameters,
	clearChildren,
	getLayerID,
	intIfSet,
	layoutComps,
)

# NOTE: if you change the layer count, update default deck state as well .
DEFAULT_LAYER_COUNT = 4
DEFAULT_STATE = {
	str(layerID): {
		'Layername': 'Composition' if layerID == 0 else f'Layer {layerID}',
		'Nextlayerid': layerID + 1 if layerID < DEFAULT_LAYER_COUNT - 1 else None
	}
	for layerID in range(DEFAULT_LAYER_COUNT)
}


class LayerCtrl(LoadableExt):

	@property
	def LayerCount(self):
		return max(0, len(self.layers) - 1) if self.Loaded else 0

	def __init__(self, ownerComponent, logger, clipCtrl):  # noqa: ANN001
		super().__init__(ownerComponent, logger)
		self.clipCtrl = clipCtrl
		self.layerTemplate = ownerComponent.op('./layerTemplate')
		self.composition = ownerComponent.op('../composition')
		self.layerList = ownerComponent.op('./table_layerIDs')
		self.layerState = ownerComponent.op('./null_layerState')
		assert self.composition, 'could not find composition component'

	def Init(self, renderState):  # noqa: ANN001
		self.setUnloaded()
		self.renderState = renderState

		self.layerContainer = self.composition.op('layers')
		if self.layerContainer:
			self.logDebug('clearing layers in composition')
			clearChildren(self.layerContainer)
		else:
			self.logInfo('layers op not found in composition, initalizing')
			self.layerContainer = self.composition.create(baseCOMP, 'layers')

		self.nextLayerID = 0
		self.layers = {}
		self.layerList.clear()

		self.logInfo('initialized')

	def Load(self, saveState=None):  # noqa: ANN001
		self.setLoading()
		self.logInfo('loading composition from state')

		state = saveState or DEFAULT_STATE
		for layerID, layer in state.items():
			self.createLayer(
				layerName=layer['Layername'],
				# NOTE: we cast to int because we cant use numeric keys in json
				layerID=int(layerID),
				nextLayerID=layer['Nextlayerid'],
			)

		self.updateLayerOrder()

		self.logInfo(f'loaded {len(self.layers)} layers in composition')
		self.setLoaded()

	def GetSaveState(self):
		return {
			layerID: {
				'Layername': layer.par.Layername.eval(),
				'Nextlayerid': intIfSet(layer.par.Nextlayerid.eval())
			}
			for layerID, layer in self.layers.items()
		}

	def Clear(self, layerID: int):
		self.logInfo(f'clearing clip from layer {layerID}')
		currentClipID = self.layers[layerID].par.Clipid
		self.layers[layerID].par.Clipid = ''

		# TODO: once we fix types here, verify clipID can't be the number 0
		if currentClipID != '':  # noqa: PLC1901
			self.clipCtrl.DeactivateClip(int(currentClipID))

	def Insert(self, layerNumber: int, direction):  # noqa: ANN001
		self.logInfo(f'inserting layer {direction} layer {layerNumber}')
		targetLayer = self.getLayerByOrder(
			layerNumber if direction == 'below' else layerNumber - 1
		)
		newLayer = self.createLayer(nextLayerID=targetLayer.par.Nextlayerid.eval())
		targetLayer.par.Nextlayerid.val = newLayer.digits
		self.updateLayerOrder()

	def Remove(self, layerNumber: int):
		self.logInfo(f'removing layer {layerNumber}')
		previousLayer = self.getLayerByOrder(layerNumber - 1)
		targetLayer = self.getLayerByOrder(layerNumber)
		targetLayerID = targetLayer.digits

		assert targetLayerID != 0, 'the composition cannot be removed'

		previousLayer.par.Nextlayerid.val = targetLayer.par.Nextlayerid.eval()
		self.layerList.deleteRow(str(targetLayerID))
		del self.layers[targetLayerID]
		targetLayer.destroy()

		self.updateLayerOrder()

	def ClearClipID(self, clipID: int):
		assert self.layers, 'cloud not clear clip ID, layers not loaded'

		for layer in self.layers.values():
			if layer.par.Clipid == str(clipID):
				layer.par.Clipid = None

		self.clipCtrl.DeleteClip(clipID)

	def getLayerByOrder(self, layerNumber: int):
		layer = next(
			(
				l for l in self.layers.values()  # noqa: E741
				if l.par.Layerorder.eval() == layerNumber
			),
			None
		)
		assert layer, f'could not find layer number {layerNumber} to set clip in'

		return layer

	def SetClip(self, layerNumber, clipID: int):  # noqa: ANN001
		layer = self.getLayerByOrder(layerNumber)

		previousClipID = intIfSet(layer.par.Clipid.val)
		layer.par.Clipid = clipID

		if clipID is not None:
			self.clipCtrl.ActivateClip(clipID)

		if previousClipID is not None and previousClipID != clipID:
			self.clipCtrl.DeactivateClip(previousClipID)

	def SelectLayer(self, address):  # noqa: ANN001
		layerID = getLayerID(address)
		self.composition.par.Previstarget = f'composition/layers/layer{layerID}/video/null_previs'
		# previousSelectedLayer = self.composition.par.Selectedlayer.eval()
		self.composition.par.Selectedlayer = layerID

	def createLayer(
		self,
		layerName: Optional[str] = None,
		layerID: Optional[int] = None,
		nextLayerID: Optional[int] = None,
	):
		if layerID is None:
			layerID = self.nextLayerID
			self.nextLayerID += 1
		elif layerID >= self.nextLayerID:
			self.nextLayerID = layerID + 1

		opName = f'layer{layerID}'
		self.logDebug(f'creating layer: {opName}')

		newLayer = self.layerContainer.copy(self.layerTemplate, name=opName)
		newLayer.par.Layername = layerName or f'Layer {layerID}'
		newLayer.par.Nextlayerid = nextLayerID

		videoContainer = newLayer.op('./video')
		addSectionParameters(videoContainer, order=-1, name='Video')

		self.layers[layerID] = newLayer
		self.layerList.appendRow([layerID])

		self.layoutLayerContainer()

		return newLayer

	def updateLayerOrder(self):
		layer = self.layers[0]  # composition/head will always be layer id 0
		order = 0
		while layer:
			layer.par.Layerorder = order
			order += 1
			nextLayerID = layer.par.Nextlayerid.eval()
			layer = (
				self.layers[int(nextLayerID)]
				# TODO: is layerID always a string?
				if nextLayerID != '' else None  # noqa: PLC1901
			)

	def layoutLayerContainer(self):
		layoutComps(self.layers.values(), columns=1)
