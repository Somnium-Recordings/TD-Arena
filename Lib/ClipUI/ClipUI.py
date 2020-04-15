class ClipUI:
    @property
    def ClipLocation(self):
        return (
            self.ownerComponent.parent.deckUI.digits,
            self.ownerComponent.parent.layerUI.digits,
            self.ownerComponent.digits,
        )

    def __init__(self, ownerComponent, movieBrowser, compCtrl):
        self.ownerComponent = ownerComponent
        self.movieBrowser = movieBrowser
        self.compCtrl = compCtrl

    #
    #  arguments for dropping nodes           (and files)
    #
    #       args[0] dropped node name            (or filename)
    #       args[1] x position
    #       args[2] y position
    #       args[3] dragged index
    #       args[4] total dragged
    #       args[5] operator                     (or file extension)
    #       args[6] dragged node parent network  (or parent directory)
    #       args[7] dropped network
    #
    def OnDrop(self, *args):
        (movieName, moviePath) = self.movieBrowser.GetMovie(args[0])
        self.compCtrl.LoadMovieClip(self.ClipLocation, movieName, moviePath)

    def OnLeftClickThumb(self):
        print("left clicking")

    def OnRightClickThumb(self):
        self.compCtrl.ClearClip(self.ClipLocation)
