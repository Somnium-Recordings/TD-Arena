class CompositionCtrl:
    def __init__(self, ownerComponent, clipCtrl, deckCtrl, layerCtrl):
        self.ownerComponent = ownerComponent
        self.clipCtrl = clipCtrl
        self.deckCtrl = deckCtrl
        self.layerCtrl = layerCtrl

    def LoadMovieClip(self, clipLocation, movieName, moviePath):
        clipID = self.deckCtrl.GetClipID(clipLocation)

        if clipID:
            self.clipCtrl.ReplaceWithMovieClip(movieName, moviePath, clipID)
        else:
            clip = self.clipCtrl.LoadMovieClip(movieName, moviePath)
            self.deckCtrl.SetClip(clipLocation, clip.digits)

    def ClearClip(self, clipLocation):
        clipID = self.deckCtrl.ClearClip(clipLocation)

        if clipID:
            self.clipCtrl.DeleteClip(clipID)
            self.layerCtrl.ClearClipID(clipID)

    def LaunchClip(self, clipLocation):
        (_, layerNumber, _) = clipLocation
        clipID = self.deckCtrl.GetClipID(clipLocation)
        previousClipID = self.layerCtrl.SetClip(layerNumber, clipID)

        if clipID: # clipID is None when launching an empty clip
            self.clipCtrl.ActivateClip(clipID)

        if previousClipID and previousClipID != clipID:
            self.clipCtrl.DeactivateClip(previousClipID)
