import math

NETWORK_LAYOUT_COLUMNS = 4


class ClipManager:
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
            clipId = clip.digits
            self.clipComps[clipId] = clip
            if clipId >= self.nextClipID:
                self.nextClipID = clipId + 1

    def LoadMovieClip(self, name, path):
        clip = self.createNextClip(self.movieClipTemplate)

        clip.par.Clipname = name
        clip.par.Moviepath = "movies://{}".format(path)

        return clip

    def createNextClip(self, clipTemplate):
        assert self.clips, "could not create clip, composition not loaded"

        clipId = self.nextClipID
        clip = self.clips.copy(clipTemplate, name="clip{}".format(clipId))
        self.clipComps[clipId] = clip
        self.nextClipID += 1

        self.updateClipNetworkPositions()

        return clip

    def updateClipNetworkPositions(self):
        # TODO: should we skip if ui.performMode == False?
        for i, comp in enumerate(self.clipComps.values()):
            comp.nodeX = 0 + (i % NETWORK_LAYOUT_COLUMNS) * 200
            comp.nodeY = -130 - math.floor(i / NETWORK_LAYOUT_COLUMNS) * 200
