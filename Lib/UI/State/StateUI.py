TDJ = op.TDModules.mod.TDJSON

MAX_WAIT_CYCLES = 10


class StateUI:
    def __init__(self, ownerComponent):
        self.ownerComponent = ownerComponent
        self.state = ownerComponent.op("touchin_state")

        self.deckState = ownerComponent.op("deckState")
        self.deckList = self.deckState.op("table_deckList")

        self.clipState = ownerComponent.op("clipState")
        self.clipList = self.clipState.op("table_clipList")

        self.oscOut = ownerComponent.op('oscout1')
    
    def SendMessage(self, address, *args):
        self.oscOut.sendOSC(address, args)

    def OnChange(self):
        state = TDJ.datToJSON(self.state)
        self.updateDeckState(state["decks"])
        self.updateClipState(state["clips"])

    def updateClipState(self, clips):
        self.syncToDat(clips, self.clipList)


    def updateDeckState(self, decks):
        deckNames = [[deck["name"]] for deck in decks]
        self.syncToDat(deckNames, self.deckList)

        for index, deck in enumerate(decks):
            # TODO: don't use replicator for decks so we avoid race
            #       condition when creating decks
            deckOp = self.getDeckOp(index)
            if not deckOp:
                return self.updateAfterDeckCreation(decks)

            self.syncToDat(deck["layers"], deckOp)

        # self.deckList.setSize(len(decks), 1)
        # for index, deck in enumerate(decks):
        #     self.deckList[index, 0] = deck["name"]

        #     self.syncToDat(deck["layers"], deckOp)

    def getDeckOp(self, index):
        return self.deckState.op("table_deck{}".format(index))

    def syncToDat(self, data, targetDat):
        rowCount = len(data)
        columnCount = len(data[0]) if rowCount > 0 else 0
        targetDat.setSize(rowCount, columnCount)

        for rowIndex, row in enumerate(data):
            for columnIndex, cell in enumerate(row):
                targetDat[rowIndex, columnIndex] = cell or ""

    """
    TODO: this sucks...
    """

    def updateAfterDeckCreation(self, decks, waitCount=0):
        if waitCount > MAX_WAIT_CYCLES:
            raise AssertionError(
                "expected replicator to create UIState deck storage in less than {} cycles".format(
                    MAX_WAIT_CYCLES
                )
            )

        for index, _ in enumerate(decks):
            if not self.getDeckOp(index):
                return run(
                    "args[0].updateAfterDeckCreation(args[1], args[2])",
                    self,
                    decks,
                    waitCount + 1,
                    delayFrames=2,
                )

        return self.updateDeckState(decks)
