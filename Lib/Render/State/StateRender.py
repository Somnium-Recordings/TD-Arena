TDJ = op.TDModules.mod.TDJSON


class StateRender:
    def __init__(self, ownerComponent, deckCtrl, clipCtrl):
        self.ownerComponent = ownerComponent
        self.renderState = ownerComponent.op("text_renderState")
        self.errors = ownerComponent.op('error1')
        self.deckCtrl = deckCtrl
        self.clipCtrl = clipCtrl
        self.state = None
        self.dirty = False

        # TODO: support "savable" compositions
        self.InitalizeState()

    def InitalizeState(self):
        self.state = {"clips": [], "decks": [], "errors": []}
        self.OnDeckStateChange(sendState=False)
        self.OnClipStateChange(sendState=False)
        self.sendState()

    def OnDeckStateChange(self, sendState=True):
        state = []
        for index, listRow in enumerate(self.deckCtrl.DeckList.rows()):
            deck = self.deckCtrl.GetDeckOp(index)

            state.append(
                {
                    "name": listRow[0].val,
                    "layers": [self.getCellValues(layer) for layer in deck.rows()],
                }
            )

        self.state["decks"] = state
        if sendState:
            self.sendState()

    def OnClipStateChange(self, sendState=True):
        self.state["clips"] = [
            self.getCellValues(clip) for clip in self.clipCtrl.ClipState.rows()
        ]

        if sendState:
            self.sendState()
    
    def OnErrorStateChange(self, sendState=True):
        self.state["errors"] = [
            self.getCellValues(error) for error in self.errors.rows()
        ]

        if sendState:
            self.sendState()

    def getCellValues(self, datRow):
        return [cell.val for cell in datRow]

    def sendState(self):
        self.dirty = True
        # Batch state changes to once per frame, this also helps
        # with races from multiple chanegs occuring close together
        # TODO: I think there might still be a race here
        run("args[0].flushState()", self, delayFrames=1)

    def flushState(self):
        if not self.dirty:
            return

        TDJ.jsonToDat(self.state, self.renderState)
        self.dirty = False
