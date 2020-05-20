import math


from tdaUtils import intIfSet


class DeckCtrl:
    @property
    def DeckList(self):
        return self.deckList

    @property
    def StateDATs(self):
        """
        paths to DATs that RenderState should watch for changes
        TODO: use dependency here and update when loadComposition is fired
        """
        compPath = self.composition.path
        return " ".join(
            ["{}/decks/deckList".format(compPath), "{}/decks/deck*".format(compPath)]
        )

    @property
    def ActiveDeck(self):
        """
        TODO: is there a better way to handle this than referencing
              the par from self.render?
        """
        return self.render.par.Activedeck.val

    def __init__(self, ownerComponent, render):
        self.ownerComponent = ownerComponent
        self.render = render
        self.deckList = None
        self.composition = None

        self.deckState = ownerComponent.op("text_deckState")
        self.clipState = ownerComponent.op("null_clipState")

        # TODO: support "savable" compositions
        self.loadComposition()

    def loadComposition(self):
        self.composition = self.ownerComponent.op("../composition")
        assert self.composition, "could not find composition component"

        self.decks = self.composition.op("decks")
        assert self.decks, "could not find decks container in composition/decks"

        self.deckList = self.decks.op("deckList")
        assert self.deckList, "could not find deckList dat in composition/deckList"

    def AddDeck(self):
        # TODO: show add button if DeckCtrl not initialized
        # TODO: find way to prompt for deck name
        self.deckList.appendRow(["Deck {}".format(self.deckList.numRows)])

    def SetClip(self, clipLocation, clipID):
        self.clipCell(clipLocation).val = clipID

    def GetClipID(self, clipLocation):
        return intIfSet(self.clipCell(clipLocation).val)

    def ClearClip(self, clipLocation):
        cell = self.clipCell(clipLocation)
        clipID = cell.val
        cell.val = ""

        return intIfSet(clipID)

    def GetDeckOp(self, index):
        # TODO: cache these
        return self.decks.op("deck{}".format(index))

    def clipCell(self, clipLocation):
        (layerNumber, clipNumber) = clipLocation

        deckOpName = "deck{}".format(self.ActiveDeck)
        deck = self.decks.op(deckOpName)
        assert deck, "could not find requested deck ({})to add clip to".format(
            deckOpName
        )

        return deck[layerNumber, clipNumber]

    # @property
    # def DeckList(self):
    #     return self.ownerComponent.
