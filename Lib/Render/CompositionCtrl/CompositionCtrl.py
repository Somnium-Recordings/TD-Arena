class CompositionCtrl:
    def __init__(self, ownerComponent, clipCtrl, deckCtrl, layerCtrl):
        self.ownerComponent = ownerComponent
        self.clipCtrl = clipCtrl
        self.deckCtrl = deckCtrl
        self.layerCtrl = layerCtrl

    def LoadMovieClip(self, clipLocation, movieName, moviePath):
        clipID = self.deckCtrl.GetClipID(clipLocation)

        # TODO: return None from DeckCtrl to avoid runnig into this again
        if isinstance(clipID, int): # clipID is "" when empty clip
            self.clipCtrl.ReplaceWithMovieClip(movieName, moviePath, clipID)
        else:
            clip = self.clipCtrl.LoadMovieClip(movieName, moviePath)
            self.deckCtrl.SetClip(clipLocation, clip.digits)

    def ClearClip(self, clipLocation):
        clipID = self.deckCtrl.ClearClip(clipLocation)

        if isinstance(clipID, int): # clipID is "" if an empty clip
            self.clipCtrl.DeleteClip(clipID)
            self.layerCtrl.ClearClipID(clipID)

    def LaunchClip(self, clipLocation):
        (_, layerNumber, _) = clipLocation
        clipID = self.deckCtrl.GetClipID(clipLocation)
        previousClipID = self.layerCtrl.SetClip(layerNumber, clipID)

        if isinstance(clipID, int): # clipID is "" when launching an empty clip
            self.clipCtrl.ActivateClip(clipID)

        if isinstance(previousClipID, int) and previousClipID != clipID:
            self.clipCtrl.DeactivateClip(previousClipID)
