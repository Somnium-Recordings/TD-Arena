import math

NETWORK_LAYOUT_COLUMNS = 4


class ClipCtrl:
    @property
    def StateDATs(self):
        """
        paths to DATs that RenderState should watch for changes
        """
        return self.ClipState.path

    def __init__(self, ownerComponent):
        self.ownerComponent = ownerComponent
        self.clipIDTable = ownerComponent.op("./table_clipIDs")
        self.clipTemplate = ownerComponent.op("./clipTemplate")
        self.movieSourceTemplate = ownerComponent.op("./movieSourceTemplate")
        self.ClipState = ownerComponent.op("null_clipState")

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
        self.clipIDTable.clear()
        for clip in self.clips.findChildren(name="clip*", depth=1, type=COMP):
            clipID = clip.digits
            self.clipComps[clipID] = clip
            if clipID >= self.nextClipID:
                self.nextClipID = clipID + 1

            self.clipIDTable.appendRow([clipID])

    def LoadMovieClip(self, name, path):
        clip = self.createNextClip()
        source = self.loadSource(clip, self.movieSourceTemplate)

        return self.setMovieClip(name, path, clip, source)

    def ReplaceWithMovieClip(self, name, path, clipID):
        clip = self.clipComps[clipID]
        assert clip, "could not replace movie clip of unknown clip id {}".format(clipID)

        source = self.loadSource(clip, self.movieSourceTemplate)

        return self.setMovieClip(name, path, clip, source)

    def ActivateClip(self, clipID):
        clip = self.clipComps[clipID]
        assert clip, "could not activate unknown clip id {}".format(clipID)
        source = clip.op("source")

        clip.par.Active = 1

        source.par.Onactivate.pulse()

    def DeactivateClip(self, clipID):
        clip = self.clipComps[clipID]
        assert clip, "could not deactivate unknown clip id {}".format(clipID)

        clip.par.Active = 0

    def setMovieClip(self, name, path, clip, source):
        clip.par.Clipname = name
        source.par.Moviepath = path

        return clip

    def DeleteClip(self, clipID):
        assert self.clipComps, "could not delete clip, composition not loaded"

        cell = self.clipIDTable.findCell(clipID)
        if cell is not None:
            self.clipIDTable.deleteRow(cell.row)

        clip = self.clipComps.pop(clipID, None)
        if clip is not None:
            clip.destroy()
            self.updateClipNetworkPositions()

    def loadSource(self, clip, sourceTemplate):
        existingSource = clip.op("source")
        if existingSource:
            # TODO: is there a more performant way to do this?
            # How does this perform if clip is active?
            existingSource.destroy()

        newSource = clip.copy(sourceTemplate, name="source")
        # TODO: figure out a better way to handle this. 
        # Right now if we don't do this the source looses its Moviepath property on reload
        newSource.par.externaltox = None

        return newSource

    def createNextClip(self):
        assert self.clips, "could not create clip, composition not loaded"

        clipID = self.nextClipID
        clip = self.clips.copy(self.clipTemplate, name="clip{}".format(clipID))
        self.clipComps[clipID] = clip
        self.nextClipID += 1

        self.clipIDTable.appendRow([clipID])

        self.updateClipNetworkPositions()

        return clip

    def updateClipNetworkPositions(self):
        # TODO: should we skip if ui.performMode == False?
        for i, comp in enumerate(self.clipComps.values()):
            comp.nodeX = 0 + (i % NETWORK_LAYOUT_COLUMNS) * 200
            comp.nodeY = -130 - math.floor(i / NETWORK_LAYOUT_COLUMNS) * 200
