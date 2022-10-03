from collections import namedtuple
from typing import Generic, TypeVar

T = TypeVar('T')


class Par(Generic[T]):
	"""
	Minimal type info for the touch designer Parameter class
	"""
	@property
	def val(self) -> T:
		pass

	@val.setter
	def val(self, newVal: T) -> None:
		pass

	def eval(self) -> T:
		pass


# pylint: disable=too-few-public-methods
class Cell():
	@property
	def val(self) -> str:
		pass


class BaseExt():
	def __init__(self, ownerComponent, logger):
		self.ownerComponent = ownerComponent
		self.logger = logger

	def logInfo(self, *args):
		self.logger.Info(self.ownerComponent, *args)

	def logDebug(self, *args):
		self.logger.Debug(self.ownerComponent, *args)

	def logWarning(self, *args):
		self.logger.Warning(self.ownerComponent, *args)

	def logError(self, *args):
		self.logger.Error(self.ownerComponent, *args)


class LoadableExt(BaseExt):
	def __init__(self, ownerComponent, logger):
		super().__init__(ownerComponent, logger)
		self.Loaded: bool
		self._Loaded: Par[bool]

		TDF = op.TDModules.mod.TDFunctions
		TDF.createProperty(self, 'Loaded', value=False, readOnly=True)

		self.Loading: bool
		self._Loading: Par[bool]
		TDF.createProperty(self, 'Loading', value=False, readOnly=True)

	def setUnloaded(self):
		self._Loaded.val = False
		self._Loading.val = False

	def setLoading(self):
		self._Loaded.val = False
		self._Loading.val = True

	def setLoaded(self, wasSuccessful=True):
		self._Loaded.val = wasSuccessful
		self._Loading.val = False


# TODO(#56): look into better way to import things from other extensions
DroppedItem = namedtuple(
	'DroppedItem', [
		'dropName', 'dropExt', 'baseName', 'destPath', 'itemPath',
		'selectedItemIndex'
	]
)
