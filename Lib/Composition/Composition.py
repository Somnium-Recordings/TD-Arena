class Composition:
    def __init__(self, ownerComponent):
        self.ownerComponent = ownerComponent
        print("composition initializing")

    def OnDrop(self):
        print("Handling drop")
