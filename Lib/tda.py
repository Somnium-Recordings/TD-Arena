from collections import namedtuple


# TODO: Move to td stubs
class TDFileInfo(str):
	"""
	Created using tdu.FileInfo
	See: https://docs.derivative.ca/FileInfo_Class
	"""

	path: str
	'The filepath'

	ext: str
	'After and including "."'

	baseName: str
	'The basename of the file'

	fileType: str
	'''
	The TD filetype (from tdu.fileTypes)
	See: https://docs.derivative.ca/Tdu_Module
	'''

	absPath: str
	'The absolute path to filepath'

	dir: str
	'The containing directory of filepath'

	exists: bool
	'Exists in file-system'

	isDir: bool
	'Is a directory in the file-system'

	isFile: bool
	'Is a file in the file-system'


class BaseExt():

	def __init__(self, ownerComponent, logger):  # noqa: ANN001
		self.ownerComponent = ownerComponent
		self.logger = logger

	def logInfo(self, *args):  # noqa: ANN002
		self.logger.Info(self.ownerComponent, *args)

	def logDebug(self, *args):  # noqa: ANN002
		self.logger.Debug(self.ownerComponent, *args)

	def logWarning(self, *args):  # noqa: ANN002
		self.logger.Warning(self.ownerComponent, *args)

	def logError(self, *args):  # noqa: ANN002
		self.logger.Error(self.ownerComponent, *args)


class LoadableExt(BaseExt):

	def __init__(self, ownerComponent, logger):  # noqa: ANN001
		super().__init__(ownerComponent, logger)
		self.Loaded: bool
		self._Loaded: Par

		TDF = op.TDModules.mod.TDFunctions
		TDF.createProperty(self, 'Loaded', value=False, readOnly=True)

		self.Loading: bool
		self._Loading: Par
		TDF.createProperty(self, 'Loading', value=False, readOnly=True)

	def setUnloaded(self):
		self._Loaded.val = False
		self._Loading.val = False

	def setLoading(self):
		self._Loaded.val = False
		self._Loading.val = True

	def setLoaded(self, wasSuccessful=True):  # noqa: ANN001, FBT002
		self._Loaded.val = wasSuccessful
		self._Loading.val = False


# TODO(#56): look into better way to import things from other extensions
DroppedItem = namedtuple(
	'DroppedItem', [
		'dropName', 'dropExt', 'baseName', 'destPath', 'itemPath',
		'selectedItemIndex'
	]
)
