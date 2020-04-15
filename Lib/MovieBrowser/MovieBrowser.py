class MovieBrowser:
    def __init__(self, ownerComponent):
        self.ownerComponent = ownerComponent
        print("Movie browser initializing")

    def GetMovie(self, movieCompName):
        comp = self.ownerComponent.op(movieCompName)
        assert (
            comp is not None
        ), 'requested movie path for unknown movie comp: "{}"'.format(movieCompName)

        data = comp.op("./select_video")
        return (data[1, "basename"].val, data[1, "relpath"].val)
