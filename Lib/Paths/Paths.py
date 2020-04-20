import os.path


class Paths:
    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
        self.configuredPaths = ownerComp.op("null_configuredPaths")
        self.examine = ownerComp.op("examine_projectPaths")
        self.setPaths = ownerComp.op("table_setPaths")
        self.Apply()

    def Apply(self):
        newPaths = {}
        for protocol, path in self.configuredPaths.rows():
            expanded = os.path.expanduser(path.val)
            if not os.path.exists(expanded):
                print(
                    "configured path for protocol ("
                    + protocol
                    + ") does not exist: "
                    + expanded
                )
                continue
            newPaths[protocol.val] = expanded

        # clear any project paths that are no longer configured
        for protocol in project.paths.copy():
            if protocol not in newPaths:
                del project.paths[protocol]

        for protocol, path in newPaths.items():
            project.paths[protocol] = path

        self.setPaths.clear()
        for protocol in project.paths:
            self.setPaths.appendRow([protocol, project.paths[protocol]])
