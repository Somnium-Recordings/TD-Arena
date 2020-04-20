class ClipUI:
    @property
    def ClipLocation(self):
        return (
            self.ownerComponent.parent.deckUI.digits,
            self.ownerComponent.parent.layerUI.digits,
            self.ownerComponent.digits,
        )

    def __init__(self, ownerComponent, browserUI, compCtrl):
        self.ownerComponent = ownerComponent
        self.browserUI = browserUI
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
        droppedNode = args[0]
        (fileName, filePath) = self.browserUI.GetPath(droppedNode)

        if droppedNode.startswith("movie"):
            self.compCtrl.LoadMovieClip(self.ClipLocation, fileName, filePath)
        else:
            raise AssertionError(
                "Could not match node to clip type: {}".format(droppedNode)
            )

    def OnLeftClickThumb(self):
        self.compCtrl.LaunchClip(self.ClipLocation)

    def OnRightClickThumb(self):
        self.compCtrl.ClearClip(self.ClipLocation)
