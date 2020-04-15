class CompositionCtrl:
    def __init__(self, ownerComponent):
        self.ownerComponent = ownerComponent
        print("composition controller initializing")

    def OnDrop(self):
        print("Handling drop")
