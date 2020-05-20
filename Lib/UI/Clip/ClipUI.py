class ClipUI:
    @property
    def ClipAddress(self):
        return "/composition/layers/{}/clips/{}".format(
            self.ownerComponent.parent.layerUI.digits, self.ownerComponent.digits
        )

    def __init__(self, ownerComponent, browserUI, stateUI, compCtrl):
        self.ownerComponent = ownerComponent
        self.browserUI = browserUI
        self.stateUI = stateUI
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

            self.stateUI.SendMessage(
                "{}/source/movie/load".format(self.ClipAddress), fileName, filePath
            )
        else:
            raise AssertionError(
                "Could not match node to clip type: {}".format(droppedNode)
            )

    def OnLeftClickThumb(self):
        self.stateUI.SendMessage("{}/connect".format(self.ClipAddress))

    def OnRightClickThumb(self):
        self.stateUI.SendMessage("{}/clear".format(self.ClipAddress))
