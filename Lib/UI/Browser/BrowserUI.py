class BrowserUI:
    def __init__(self, ownerComponent):
        self.ownerComponent = ownerComponent

    def GetPath(self, compName):
        comp = self.ownerComponent.op(compName)
        assert comp is not None, 'requested path for unknown file: "{}"'.format(
            compName
        )

        data = comp.op("./select_file")
        return (
            data[1, "basename"].val,
            # eg: movie://some-move-name.mov
            "{}://{}".format(
                self.ownerComponent.par.Resourcetype, data[1, "relpath"].val
            ),
        )
