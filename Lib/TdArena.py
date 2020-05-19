valueMap = {
    # State
    "Activedeck": {"target": "both"},
    # Resolutions
    "Renderw": {"target": "both"},
    "Renderh": {"target": "both"},
    "Uiw": {"target": "ui", "par": "w"},
    "Uih": {"target": "ui", "par": "h"},
    "Clipthumbw": {"target": "both"},
    "Clipthumbh": {"target": "both"},
    # Networking
    "Localstateoutport": {"target": "local", "par": "Stateoutport"},
    "Localerrorsoutport": {"target": "local", "par": "Errorsoutport"},
    "Enginestateoutport": {"target": "engine", "par": "Stateoutport"},
    "Engineerrorsoutport": {"target": "engine", "par": "Errorsoutport"},
    # Paths
    "Effectspath": {"target": "both"},
    "Generatorspath": {"target": "both"},
    "Moviespath": {"target": "both"},
    "Libpath": {"target": "both"},
}

pulseMap = {
    "Clearrendererrors": {"target": "active", "par": "Clearerrors"},
    "Reloadengine": {"target": "engine", "par": "reload"},
}


class TdArena:
    @property
    def par(self):
        return self.ownerComponent.par

    def __init__(self, ownerComponent):
        self.ownerComponent = ownerComponent
        self.localRender = ownerComponent.op("./render")
        self.engineRender = ownerComponent.op("./engine_render")
        self.ui = ownerComponent.op("./ui")
        self.Sync()

    def Sync(self):
        self.SetLibPath()

        for parName in valueMap.keys():
            par = getattr(self.par, parName)
            # TODO: Could passing same value as prev cause issues?
            self.SyncValueChange(par, par.val)

    def SetLibPath(self):
        # NOTE: os.path.join results in bothforward and backward slashes on Windows
        self.par.Libpath = "{}/{}".format(project.folder, "Lib")

    def SyncValueChange(self, par, prev):
        newVal = par.eval()

        if par.name == "Useengine":
            self.toggleEngine(newVal)
            return

        for targetPar in self.getUpdateTargets(par.name, valueMap):
            targetPar.val = newVal

    def SyncPulse(self, par):
        if par.name == "Sync":
            self.Sync()
            return

        for targetPar in self.getUpdateTargets(par.name, pulseMap):
            targetPar.pulse()

    def getUpdateTargets(self, parName, parameterMap):
        assert parName in parameterMap, 'expected tda par "{}" to be mapped'.format(
            parName
        )
        mapConfig = parameterMap[parName]
        if "par" not in mapConfig:
            mapConfig["par"] = parName

        targets = []
        if mapConfig["target"] == "both":
            targets.append(self.localRender)
            targets.append(self.engineRender)
        elif mapConfig["target"] == "engine":
            targets.append(self.engineRender)
        elif mapConfig["target"] == "local":
            targets.append(self.localRender)
        elif mapConfig["target"] == "ui":
            targets.append(self.ui)
        elif mapConfig["target"] == "active":
            targets.append(
                self.engineRender if self.par.Useengine else self.localRender
            )
        else:
            raise AssertionError("unexpected mapType of {}".format(mapConfig["target"]))

        return [self.getTargetPar(target, mapConfig) for target in targets]

    def getTargetPar(self, targetOp, mapConfig):
        return getattr(targetOp.par, mapConfig["par"])

    def toggleEngine(self, useEngine):
        self.localRender.allowCooking = not useEngine
        self.engineRender.par.power = useEngine
