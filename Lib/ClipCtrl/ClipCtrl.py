import math

NETWORK_LAYOUT_COLUMNS = 4


class ClipCtrl:
    def __init__(self, ownerComponent):
        self.ownerComponent = ownerComponent
        self.clipTemplate = ownerComponent.op("./clipTemplate")
        self.movieSourceTemplate = ownerComponent.op("./movieSourceTemplate")

        self.nextClipID = None
        self.clipComps = None
        self.composition = None
        self.clips = None

        # TODO: support "savable" compositions
        self.loadComposition()

    def loadComposition(self):
        self.composition = self.ownerComponent.op("../composition")
        assert self.composition, "could not find composition component"

        self.clips = self.composition.op("clips")
        assert self.clips, "could not find clips container in composition/clips"

        self.nextClipID = 0
        self.clipComps = {}
        for clip in self.clips.findChildren(name="clip*", depth=1, type=COMP):
            clipID = clip.digits
            self.clipComps[clipID] = clip
            if clipID >= self.nextClipID:
                self.nextClipID = clipID + 1

    def LoadMovieClip(self, name, path):
        clip = self.createNextClip()
        source = self.loadSource(clip, self.movieSourceTemplate)

        return self.setMovieClip(name, path, clip, source)

    def ReplaceWithMovieClip(self, name, path, clipID):
        clip = self.clipComps[clipID]
        assert clip, "could not replace movie clip of unknown clip id {}".format(clipID)

        source = self.loadSource(clip, self.movieSourceTemplate)

        return self.setMovieClip(name, path, clip, source)

    def setMovieClip(self, name, path, clip, source):
        clip.par.Clipname = name
        source.par.Moviepath = "movies://{}".format(path)

        return clip

    def DeleteClip(self, clipID):
        assert self.clipComps, "could not delete clip, composition not loaded"

        clip = self.clipComps.pop(clipID, None)
        if clip:
            clip.destroy()
            self.updateClipNetworkPositions()

    def loadSource(self, clip, sourceTemplate):
        existingSource = clip.op("source")
        if existingSource:
            # TODO: is there a more performant way to do this?
            # How does this perform if clip is active?
            existingSource.destroy()

        return clip.copy(sourceTemplate, name="source")

    def createNextClip(self):
        assert self.clips, "could not create clip, composition not loaded"

        clipID = self.nextClipID
        clip = self.clips.copy(self.clipTemplate, name="clip{}".format(clipID))
        self.clipComps[clipID] = clip
        self.nextClipID += 1

        self.updateClipNetworkPositions()

        return clip

    def updateClipNetworkPositions(self):
        # TODO: should we skip if ui.performMode == False?
        for i, comp in enumerate(self.clipComps.values()):
            comp.nodeX = 0 + (i % NETWORK_LAYOUT_COLUMNS) * 200
            comp.nodeY = -130 - math.floor(i / NETWORK_LAYOUT_COLUMNS) * 200
