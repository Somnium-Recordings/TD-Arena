class ClipUI:
    def __init__(self, ownerComponent, clipManager):
        self.ownerComponent = ownerComponent
        self.clipManager = clipManager
        print("Clip UI initializing")

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
        print("dropped with args:")
        print(args)
        self.clipManager.LoadMovieClip(args)
