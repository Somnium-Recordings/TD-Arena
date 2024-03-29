from pathlib import Path

from tda import BaseExt


class Paths(BaseExt):

	def __init__(self, ownerComp, logger):  # noqa: ANN001
		super().__init__(ownerComp, logger)
		self.configuredPaths = ownerComp.op('null_configuredPaths')
		self.examine = ownerComp.op('examine_projectPaths')
		self.setPaths = ownerComp.op('table_setPaths')
		self.Apply()
		self.logInfo('initialized')

	def Apply(self):
		newPaths = {}
		for protocol, path in self.configuredPaths.rows():
			expanded = Path(path.val).expanduser()
			if not expanded.exists():
				self.logError(
					f'configured path for protocol ({protocol}) does not exist: {expanded}'
				)
				continue
			newPaths[protocol.val] = expanded
			self.logDebug(f'{protocol}:// set to {path}')

		configuredProtocols = [*project.paths]  # unpack keys
		self.logDebug(f'configured protocols: {configuredProtocols}')

		# clear any project paths that are no longer configured
		staleProtocols = [p for p in configuredProtocols if p not in newPaths]
		for p in staleProtocols:
			self.logDebug(f'clearing stale protocol: {p}')
			del project.paths[p]

		for protocol, path in newPaths.items():
			project.paths[protocol] = path

		self.setPaths.clear()
		for protocol in project.paths:
			self.setPaths.appendRow([protocol, project.paths[protocol]])
