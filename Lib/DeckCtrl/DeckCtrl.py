import math

def intIfSet(stringNumber):
    return int(stringNumber) if stringNumber else stringNumber

class DeckCtrl:
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
        


    def clipCell(self, clipLocation):
        (deckNumber, layerNumber, clipNumber) = clipLocation

        # TODO: handle cases where deck not found
        deckOpName = "deck{}".format(deckNumber)
        deck = self.decks.op(deckOpName)
        assert deck, "could not find requested deck ({})to add clip to".format(
            deckOpName
        )

        return deck[layerNumber, clipNumber]

    # @property
    # def DeckList(self):
    #     return self.ownerComponent.
