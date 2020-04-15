class CompositionCtrl:
    def __init__(self, ownerComponent, clipCtrl, deckCtrl):
        self.ownerComponent = ownerComponent
        self.clipCtrl = clipCtrl
        self.deckCtrl = deckCtrl

    def LoadMovieClip(self, clipLocation, movieName, moviePath):
        clip = self.clipCtrl.LoadMovieClip(movieName, moviePath)

        self.deckCtrl.SetClip(clipLocation, clip.digits)

    def ClearClip(self, clipLocation):
        clipID = self.deckCtrl.ClearClip(clipLocation)

        if clipID:
            self.clipCtrl.DeleteClip(clipID)
