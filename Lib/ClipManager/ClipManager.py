class ClipManager:
    def __init__(self, ownerComponent):
        self.ownerComponent = ownerComponent
        self.clipTable = self.ownerComponent.op("table_clips")
        print("Clip Manager Initializting")

    def LoadMovieClip(self, *args):
        print("loading movie clip")
        print(args)

