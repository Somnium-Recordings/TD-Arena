import math

NETWORK_LAYOUT_COLUMNS = 4


class ClipCtrl:
    def __init__(self, ownerComponent):
        self.ownerComponent = ownerComponent
        self.movieClipTemplate = ownerComponent.op("movieClipTemplate")

        self.nextClipID = None
        self.clipComps = None
        self.composition = None
        self.clips = None

        # TODO: support "savable" compositions
        self.loadComposition()

    def loadComposition(self):
        self.nextClipID = 0
        self.clipComps = {}

        self.composition = self.ownerComponent.op("../composition")
        assert self.composition, "could not find composition component"

        self.clips = self.composition.op("clips")
        assert self.clips, "could not find clips container in composition/clips"

        for clip in self.clips.findChildren(name="clip*", depth=1, type=COMP):
            clipID = clip.digits
            self.clipComps[clipID] = clip
            if clipID >= self.nextClipID:
                self.nextClipID = clipID + 1

    def LoadMovieClip(self, name, path):
        clip = self.createNextClip(self.movieClipTemplate)

        return self.setMovieClip(name, path, clip)

    def ReplaceMovieClip(self, name, path, clipID):
        clip = self.clipComps[clipID]
        assert clip, "could not replace movie clip of unknown clip id {}".format(clipID)

        return self.setMovieClip(name, path, clip)

    def setMovieClip(self, name, path, clip):
        clip.par.Clipname = name
        clip.par.Moviepath = "movies://{}".format(path)

        return clip

    def DeleteClip(self, clipID):
        assert self.clipComps, "could not delete clip, composition not loaded"

        clip = self.clipComps.pop(clipID, None)
        if clip:
            clip.destroy()
            self.updateClipNetworkPositions()

    def createNextClip(self, clipTemplate):
        assert self.clips, "could not create clip, composition not loaded"

        clipID = self.nextClipID
        clip = self.clips.copy(clipTemplate, name="clip{}".format(clipID))
        self.clipComps[clipID] = clip
        self.nextClipID += 1

        self.updateClipNetworkPositions()

        return clip

    def updateClipNetworkPositions(self):
        # TODO: should we skip if ui.performMode == False?
        for i, comp in enumerate(self.clipComps.values()):
            comp.nodeX = 0 + (i % NETWORK_LAYOUT_COLUMNS) * 200
            comp.nodeY = -130 - math.floor(i / NETWORK_LAYOUT_COLUMNS) * 200
