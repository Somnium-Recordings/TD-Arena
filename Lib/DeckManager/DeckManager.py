import math


class DeckManager:
    def __init__(self, ownerComponent):
        self.ownerComponent = ownerComponent
        self.deckList = None
        self.composition = None

        # TODO: support "savable" compositions
        self.loadComposition()

    def loadComposition(self):
        self.composition = self.ownerComponent.op("../composition")
        assert self.composition, "could not find composition component"

        self.deckList = self.composition.op("deckList")
        assert self.deckList, "could not find deckList dat in composition/deckList"

        self.decks = self.composition.op("decks")
        assert self.deckList, "could not find decks container in composition/decks"

    def AddDeck(self):
        # TODO: show add button if DeckManager not initialized
        # TODO: find way to prompt for deck name
        self.deckList.appendRow(["Deck {}".format(self.deckList.numRows)])

    def SetClip(self, deckNumber, layerNumber, clipNumber, clipId):
        # TODO: handle cases where deck not found
        deckOpName = "deck{}".format(deckNumber)
        deck = self.decks.op(deckOpName)
        assert deck, "could not find requested deck ({})to add clip to".format(
            deckOpName
        )
        deck[layerNumber, clipNumber] = clipId

    # @property
    # def DeckList(self):
    #     return self.ownerComponent.
