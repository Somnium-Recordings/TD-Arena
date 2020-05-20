LOAD_FRAME_DELAY = 2
MAX_WAIT_CYCLES = 20


class ToxSource:
    def __init__(self, ownerComponent):
        self.ownerComponent = ownerComponent
        # self.engine = ownerComponent.op("./engine1")
        self.thumb = ownerComponent.op("./null_thumb")
        self.state = ownerComponent.op("./constant_state")
        self.tox = ownerComponent.op("./tox")

    def Load(self):
        print("loading tox")
        self.tox.par.reinitnet.pulse()
        self.setIsLoaded()
        # self.movie.preload()
        # self.waitForPreload()

    # def waitForPreload(self, waitCount=0):
    #     assert (
    #         waitCount < MAX_WAIT_CYCLES
    #     ), "preloading video took more than {} cycles".format(MAX_WAIT_CYCLES)

    #     if not self.movie.isFullyPreRead:
    #         run("args[0].waitForPreload(args[1])", self, waitCount + 1, delayFrames=2)
    #         return

    #     self.setThumbail()

    # def setThumbail(self):
    #     # seek to middle of clip for thumbnail
    #     self.movie.par.cuepoint = 0.5
    #     self.movie.par.cue = 1

    #     # switch output to loaded video so we can capture as thumb
    #     self.setIsLoaded()

    #     # wait frames so thumbnail null has image in it it to "lock"
    #     run("args[0].lockThumbnail()", self, delayFrames=3)

    # def lockThumbnail(self):
    #     self.thumb.lock = True
    #     self.movie.par.cuepoint = 0
    #     self.movie.par.cue = 0

    def setIsLoaded(self):
        self.state.par.value0 = 0
