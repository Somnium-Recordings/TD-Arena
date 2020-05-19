import tdaUtils

class LayerCtrl:
    def __init__(self, ownerComponent):
        self.ownerComponent = ownerComponent
        self.composition = None
        self.layers = None
        self.layerOPs = None

        # TODO: support "savable" compositions
        self.loadComposition()

    def loadComposition(self):
        self.composition = self.ownerComponent.op("../composition")
        assert self.composition, "could not find composition component"

        self.layers = self.composition.op("layers")
        assert self.layers, "could not find decks container in composition/layers"

        self.RefreshLayerReferences()

    def ClearClipID(self, clipID):
        assert self.layerOPs, "cloud not clear clip ID, layers not loaded"

        for layer in self.layerOPs.values():
            if layer.par.Clipid == str(clipID):
                layer.par.Clipid = None

    def SetClip(self, layerID, clipID):
        offsetLayerID = layerID + 1 # layer 0 is master
        assert (
            offsetLayerID in self.layerOPs
        ), "could not set clip for unknown layer ID{}".format(layerID)
        layer = self.layerOPs[offsetLayerID]

        previousClipID = tdaUtils.intIfSet(layer.par.Clipid.val)
        layer.par.Clipid = clipID

        return previousClipID

    def RefreshLayerReferences(self):
        self.layerOPs = {}
        for layer in self.layers.findChildren(name="layer*", depth=1, type=COMP):
            layerId = layer.digits
            self.layerOPs[layerId] = layer
