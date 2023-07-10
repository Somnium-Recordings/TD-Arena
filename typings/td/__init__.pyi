import datetime as _DT
import enum as _E
from abc import ABC as _ABC
from typing import (
	Any, Callable, Collection, Dict, Iterable, Iterator, List, Mapping,
	NamedTuple, Optional
)
from typing import Sequence as _Sequence
from typing import (
	Set, Sized, SupportsAbs, SupportsBytes, SupportsFloat, SupportsInt, Tuple,
	Type, TypeVar, Union, overload
)

import numpy


class _Expando:

	def __getattr__(self, item) -> Any:
		...


ui: 'UI'


class MOD:

	def __call__(self, *args, **kwargs):
		...

	def __getattr__(self, item) -> Any:
		...


mod: MOD


class Ext:

	def __getattr__(self, item) -> Any:
		...


ext: Ext


class PaneType(_E.Enum):
	NETWORKEDITOR = 0
	PANEL = 0
	GEOMETRYVIEWER = 0
	TOPVIEWER = 0
	CHOPVIEWER = 0
	ANIMATIONEDITOR = 0
	PARAMETERS = 0
	TEXTPORT = 0


class UI:
	clipboard: str
	colors: 'Colors'
	dpiBiCubicFilter: bool
	masterVolume: float
	options: 'Options'
	panes: 'Panes'
	performMode: bool
	preferences: 'Preferences'
	redrawMainWindow: bool
	rolloverOp: 'OP'
	rolloverPar: 'Par'
	lastChopChannelSelected: 'Par'
	showPaletteBrowser: bool
	status: str
	undo: 'Undo'
	windowWidth: int
	windowHeight: int
	windowX: int
	windowY: int

	def copyOPs(self, listOfOPs: List['_AnyOpT']):
		...

	# noinspection PyShadowingNames
	def pasteOPs(
		self, comp: 'COMP', x: Optional[int] = None, y: Optional[int] = None
	):
		...

	# noinspection PyDefaultArgument
	def messageBox(
		self, title: str, message: str, buttons: List[str] = ['Ok']
	) -> int:
		...

	def refresh(self):
		...

	def chooseFile(
		self,
		load=True,
		start=None,
		fileTypes=None,
		title=None,
		asExpression=False
	) -> Optional[str]:
		...

	def chooseFolder(self,
																		title='Select Folder',
																		start=None,
																		asExpression=False) -> Optional[str]:
		...

	def viewFile(self, url_or_path: str):
		...

	def openAbletonControl(self):
		...

	def openBeat(self):
		...

	def openBookmarks(self):
		...

	def openCOMPEditor(self, path):
		...

	def openConsole(self):
		...

	def openDialogHelp(self, title):
		...

	def openErrors(self):
		...

	def openExplorer(self):
		...

	def openExportMovie(self, path=""):
		...

	def openHelp(self):
		...

	def openImportFile(self):
		...

	def openKeyManager(self):
		...

	def openMIDIDeviceMapper(self):
		...

	def openNewProject(self):
		...

	# noinspection PyShadowingBuiltins
	def openOperatorSnippets(self, family=None, type=None, example=None):
		...

	def openPaletteBrowser(self):
		...

	def openPerformanceMonitor(self):
		...

	def openPreferences(self):
		...

	def openSearch(self):
		...

	def openTextport(self):
		...

	def openVersion(self):
		...

	def openWindowPlacement(self):
		...

	def findEditDAT(self, filename: str) -> Optional['DAT']:
		...

	status: str


class Preferences(Mapping[str, Any], _ABC):
	defaults: Dict[str, Any]

	def save(self):
		...

	def resetToDefaults(self):
		...

	def load(self):
		...


class Options(Mapping[str, Any], _ABC):

	def resetToDefaults(self):
		...


_RgbTupletT = Tuple[float, float, float]


class Colors(Mapping[str, _RgbTupletT], _ABC):

	def resetToDefaults(self):
		...


class Panes(Iterable['_AnyPaneT'], Iterator['_AnyPaneT'], Sized):

	def __getitem__(self, key: Union[int, str]) -> '_AnyPaneT':
		...

	def createFloating(
		self,
		type=PaneType.NETWORKEDITOR,
		name=None,
		maxWidth=1920,
		maxHeight=1080,
		monitorSpanWidth=0.9,
		monitorSpanHeight=0.9,
	) -> 'Pane':
		...

	current: '_AnyPaneT'


class Coords(NamedTuple):
	x: int
	y: int
	u: float
	v: float


class Pane:

	def changeType(self, paneType: 'PaneType') -> '_AnyPaneT':
		...

	def close(self):
		...

	def floatingCopy(self) -> '_AnyPaneT':
		...

	def splitBottom(self) -> '_AnyPaneT':
		...

	def splitLeft(self) -> '_AnyPaneT':
		...

	def splitRight(self) -> '_AnyPaneT':
		...

	def splitTop(self) -> '_AnyPaneT':
		...

	def tearAway(self) -> bool:
		...

	bottomLeft: 'Coords'
	id: int
	link: int
	maximize: bool
	name: str
	owner: 'COMP'
	ratio: float
	topRight: 'Coords'
	type: 'PaneType'


class NetworkEditor(Pane):
	showBackdropCHOPs: bool
	showBackdropGeometry: bool
	showBackdropTOPs: bool
	showColorPalette: bool
	showDataLinks: bool
	showList: bool
	showNetworkOverview: bool
	showParameters: bool
	straightLinks: bool
	x: float
	y: float
	zoom: float

	def fitWidth(self, width) -> None:
		...

	def fitHeight(self, height) -> None:
		...

	# noinspection PyShadowingNames
	def home(self, zoom=True, op=None) -> None:
		...

	def homeSelected(self, zoom=True) -> None:
		...

	def placeOPs(
		self,
		listOfOPs,
		inputIndex=None,
		outputIndex=None,
		delOP=None,
		undoName='Operators'
	) -> None:
		...


_AnyPaneT = Union['Pane', 'NetworkEditor']


class Undo:
	globalState: bool
	redoStack: list
	state: bool
	undoStack: list

	def startBlock(self, name, enable=True):
		...

	def clear(self):
		...

	def addCallback(self, callback: Callable[[bool, Any], None], info=None):
		...

	def redo(self):
		...

	def undo(self):
		...

	def endBlock(self):
		...


class WindowStartMode(_E.Enum):
	DEFAULT = 'DEFAULT'
	FULL = 'FULL'
	LEFT = 'LEFT'
	RIGHT = 'RIGHT'
	CUSTOM = 'CUSTOM'


class Project:
	name: str
	folder: str
	saveVersion: str
	saveBuild: str
	saveTime: str
	saveOsName: str
	saveOsVersion: str
	paths: Dict[str, str]
	cookRate: float
	realTime: bool
	isPrivate: bool
	isPrivateKey: bool
	# cacheParameters: bool
	externalToxModifiedInProject: bool
	externalToxModifiedOnDisk: bool
	windowOnTop: bool
	windowStartMode: WindowStartMode
	windowDraw: bool
	windowStartCustomWidth: int
	windowStartCustomHeight: int
	windowStartCustomX: int
	windowStartCustomY: int
	performOnStart: bool
	performWindowPath: 'OP'

	def load(self, path: str) -> None:
		...

	def save(self, path: str, saveExternalToxs=False) -> bool:
		...

	def quit(self, force=False, crash=False) -> None:
		...

	def addPrivacy(self, key) -> bool:
		...

	def removePrivacy(self, key) -> bool:
		...

	def accessPrivateContents(self, key) -> bool:
		...

	def applyWindowSettings(self) -> None:
		...

	def stack(self) -> str:
		...

	def pythonStack(self) -> str:
		...


project: Project


class Monitor:
	index: int
	isPrimary = False
	isAffinity = False
	width: int
	height: int
	left: int
	right: int
	top: int
	bottom: int
	displayName: str
	description: str
	dpiScale: float
	scaledWidth: int
	scaledHeight: int
	scaledLeft: int
	scaledRight: int
	scaledTop: int
	scaledBottom: int
	refreshRate: float


class Monitors(_ABC, _Sequence[Monitor]):
	primary: Monitor
	width: int
	height: int
	left: int
	right: int
	top: int
	bottom: int

	@staticmethod
	def locate(x, y) -> Monitor:
		...

	@staticmethod
	def refresh():
		...


monitors: Monitors


class SysInfo:
	numCPUs: int
	ram: float
	numMonitors: int
	xres: int
	yres: int
	tfs: str


sysinfo: SysInfo


class _Parent:

	def __call__(self, *args, **kwargs) -> '_AnyOpT':
		...

	def __getattr__(self, item) -> '_AnyOpT':
		...


parent: _Parent


class Channel(SupportsInt, SupportsFloat):
	valid: bool
	index: int
	name: str
	owner: '_AnyOpT'
	exports: list
	vals: List[float]

	def __getitem__(self, index: int) -> float:
		...

	def __setitem__(self, index: int, value: Union[int, float]):
		...

	def eval(self, index: Optional[int] = None) -> float:
		...

	def evalFrame(self, frame) -> float:
		...

	def evalSeconds(self, secs) -> float:
		...

	def numpyArray(self) -> numpy.recarray:
		...

	def destroy(self) -> None:
		...

	def average(self) -> float:
		...

	def min(self) -> float:
		...

	def max(self) -> float:
		...

	def __int__(self) -> int:
		...

	def __float__(self) -> float:
		...


_ValueT = Union[float, int, str]


# TODO: Make this generic instead of hard coding available types
# T = TypeVar('T')
# class Par(Generic[T]):
# 	@property
# 	def val(self) -> T:
# 		...
#
# 	@val.setter
# 	def val(self, newVal: T) -> None:
# 		...
#
# 	def eval(self) -> T:
# 		...
class Par:
	valid: bool
	val: _ValueT
	expr: str
	exportOP: Optional['OP']
	exportSource: Optional[Union['Cell', 'Channel']]
	bindExpr: str
	bindMaster: Optional[Union['Channel', 'Cell', 'Par']]
	bindRange: bool
	bindReferences: list
	index: int
	vecIndex: int
	name: str
	label: str
	subLabel: str

	startSection: bool
	readOnly: bool
	displayOnly: bool
	tuplet: 'ParTupletT'
	tupletName: str
	min: _ValueT
	max: _ValueT
	clampMin: bool
	clampMax: bool
	default: _ValueT
	defaultExpr: str
	normMin: float
	normMax: float
	normVal: float
	enable: bool
	enableExpr: str
	order: int
	page: 'Page'
	password: bool
	help: str

	mode: 'ParMode'
	prevMode: 'ParMode'
	menuNames: List[str]
	menuLabels: List[str]
	menuIndex: int
	menuSource: str
	owner: '_AnyOpT'
	styleCloneImmune: bool
	lastScriptChange: Optional['SetInfo']

	collapser: bool
	collapsable: bool
	sequence: Set

	isDefault: bool
	isCustom: bool
	isPulse: bool
	isMomentary: bool
	isMenu: bool
	isNumber: bool
	isFloat: bool
	isInt: bool
	isOP: bool
	isPython: bool
	isString: bool
	isToggle: bool
	style: str

	collapser: bool
	collapsable: bool

	def copy(self, par: 'Par') -> None:
		...

	def eval(self) -> Union[_ValueT, '_AnyOpT']:
		...

	def evalNorm(self) -> _ValueT:
		...

	def evalExpression(self) -> _ValueT:
		...

	def evalExport(self) -> _ValueT:
		...

	def evalOPs(self) -> 'List[_AnyOpT]':
		...

	def pulse(self, value=None, frames=0, seconds=0) -> None:
		...

	def destroy(self) -> None:
		...

	def __int__(self) -> int:
		...

	def __float__(self) -> float:
		...

	def __str__(self) -> str:
		...


class ParGroup(tuple):
	bindExpr: tuple
	bindMaster: tuple
	bindRange: bool
	bindReferences: List[tuple]
	clampMin: tuple
	clampMax: tuple
	collapser: bool
	collapsable: bool
	default: tuple
	defaultExpr: tuple


class SetInfo(tuple):
	dat: Optional['DAT']
	path: str
	function: Optional[str]
	line: Optional[int]
	frame: int
	timeStamp: int


class Sequence:
	owner: 'OP'
	numBlocks: int
	maxBlocks: int
	blocks: List['ParTupletT']


ParTupletT = Union[Tuple['Par'], Tuple['Par', 'Par'],
																			Tuple['Par', 'Par', 'Par'], Tuple['Par', 'Par', 'Par',
																																																					'Par']]
_ParTupleT = TypeVar(
	'_ParTupleT', Tuple[Par], Tuple[Par, Par], Tuple[Par, Par, Par],
	Tuple[Par, Par, Par, Par]
)


class ParTuple(Generic(_ParTupleT)):
	bindRange: bool
	collapsable: bool
	collapser: bool
	enable: bool
	enableExpr: str
	help: str
	label: str
	name: str
	order: int
	page: 'Page'
	password: bool
	readOnly: bool
	sequence: 'Optional[set]'
	startSection: bool
	style: str
	valid: bool
	index: int

	isDefault: bool
	isCustom: bool
	isPulse: bool
	isMomentary: bool
	isMenu: bool
	isNumber: bool
	isFloat: bool
	isInt: bool
	isOP: bool
	isPython: bool
	isString: bool
	isToggle: bool

	def copy(self, parTuple: 'ParTuple') -> None:
		...

	def destroy(self) -> None:
		...

	def eval(self) -> Any:
		...


class ParCollection:
	owner: 'OP'

	def __getattr__(self, item) -> Par:
		...

	def __setattr__(self, key, value: Any):
		...

	def __getitem__(self, item) -> Par:
		...

	def __setitem__(self, key, value: Any):
		...


class ParTupleCollection:
	owner: 'OP'

	def __getattr__(self, item) -> ParTuple:
		...

	def __setattr__(self, key, value: Any):
		...

	def __getitem__(self, item) -> ParTuple:
		...

	def __setitem__(self, key, value: Any):
		...


class Page:
	name: str
	owner: 'OP'
	parTuplets: List[ParTupletT]
	pars: List['Par']
	index: int
	isCustom: bool

	def _appendSized(
		self, name, label=None, size=1, order=None, replace=True
	) -> ParTupletT:
		...

	def _appendBasic(
		self, name, label=None, order=None, replace=True
	) -> ParTupletT:
		...

	appendInt = _appendSized
	appendFloat = _appendSized

	appendOP = _appendBasic
	appendCHOP = _appendBasic
	appendDAT = _appendBasic
	appendMAT = _appendBasic
	appendTOP = _appendBasic
	appendSOP = _appendBasic
	appendCOMP = _appendBasic
	appendOBJ = _appendBasic
	appendPanelCOMP = _appendBasic

	appendMenu = _appendBasic
	appendStr = _appendBasic
	appendStrMenu = _appendBasic

	appendWH = _appendBasic
	appendRGBA = _appendBasic
	appendRGB = _appendBasic
	appendXY = _appendBasic
	appendXYZ = _appendBasic
	appendUV = _appendBasic
	appendUVW = _appendBasic

	appendToggle = _appendBasic
	appendPython = _appendBasic
	appendFile = _appendBasic
	appendFolder = _appendBasic
	appendPulse = _appendBasic
	appendMomentary = _appendBasic
	appendHeader = _appendBasic

	def appendPar(
		self,
		name: str,
		par: Optional['Par'] = None,
		label=None,
		order=None,
		replace=True
	) -> ParTupletT:
		...

	def sort(self, *parameters: str):
		...

	def destroy(self):
		...


class OP:
	valid: bool
	id: int
	name: str
	path: str
	digits: int
	base: str
	passive: bool
	curPar: 'Par'
	time: 'timeCOMP'
	ext: Any
	mod: Any
	par: ParCollection
	parTuple: ParTupleCollection
	pages: List['Page']
	customPars: List['Par']
	customPages: List['Page']
	customTuplets: List[ParTupletT]
	builtInPars: List[Par]
	replicator: Optional['OP']
	storage: Dict[str, Any]
	tags: Set[str]
	children: List['_AnyOpT']
	numChildren: int
	numChildrenRecursive: int
	parent: '_Parent'
	iop: Any
	ipar: Any
	currentPage: 'Page'

	activeViewer: bool
	allowCooking: bool
	bypass: bool
	cloneImmune: bool
	current: bool
	display: bool
	expose: bool
	lock: bool
	selected: bool
	python: bool
	render: bool
	showCustomOnly: bool
	showDocked: bool
	viewer: bool

	color: Tuple[float, float, float]
	comment: str
	nodeHeight: int
	nodeWidth: int
	nodeX: int
	nodeY: int
	nodeCenterX: int
	nodeCenterY: int
	dock: 'OP'
	docked: List['_AnyOpT']

	inputs: List['_AnyOpT']
	outputs: List['_AnyOpT']
	inputConnectors: List['Connector']
	outputConnectors: List['Connector']

	cookFrame: float
	cookTime: float
	cpuCookTime: float
	cookAbsFrame: float
	cookStartTime: float
	cookEndTime: float
	cookedThisFrame: bool
	cookedPreviousFrame: bool
	childrenCookTime: float
	childrenCPUCookTime: float
	childrenCookAbsFrame: float
	childrenCPUCookAbsFrame: float
	gpuCookTime: float
	childrenGPUCookTime: float
	childrenGPUCookAbsFrame: float
	totalCooks: int
	cpuMemory: int
	gpuMemory: int

	type: str
	subType: str
	OPType: str
	label: str
	icon: str
	family: str
	isFilter: bool
	minInputs: int
	maxInputs: int
	isMultiInputs: bool
	visibleLevel: int
	isBase: bool
	isCHOP: bool
	isCOMP: bool
	isDAT: bool
	isMAT: bool
	isObject: bool
	isPanel: bool
	isSOP: bool
	isTOP: bool
	licenseType: str

	def __init__(self):
		...

	def destroy(self):
		...

	def op(self, path) -> '_AnyOpT':
		...

	def ops(self, *args) -> List['_AnyOpT']:
		...

	def shortcutPath(self, o: '_AnyOpT', toParName=None) -> str:
		...

	def relativePath(self, o: '_AnyOpT') -> str:
		...

	def openMenu(self, x=None, y=None):
		...

	def var(self, name, search=True) -> str:
		...

	def evalExpression(self, expr) -> Any:
		...

	def dependenciesTo(self, o: '_AnyOpT') -> List['_AnyOpT']:
		...

	def changeType(self, optype: Type) -> '_AnyOpT':
		...

	def copyParameters(self, o: '_AnyOpT', custom=True, builtin=True):
		...

	def cook(self, force=False, recurse=False):
		...

	def pars(self, *pattern: str) -> List['Par']:
		...

	def openParameters(self):
		...

	def openViewer(self, unique=False, borders=True):
		...

	def closeViewer(self):
		...

	def store(self, key, value):
		...

	def unstore(self, keys1, *morekeys):
		...

	def storeStartupValue(self, key, value):
		...

	def unstoreStartupValue(self, *keys):
		...

	def fetch(self, key, default=None, search=True, storeDefault=False):
		...

	def fetchOwner(self, key) -> '_AnyOpT':
		...

	def addScriptError(self, msg):
		...

	def addError(self, msg):
		...

	def addWarning(self, msg):
		...

	def errors(self, recurse=False) -> str:
		...

	def warnings(self, recurse=False) -> str:
		...

	def scriptErrors(self, recurse=False) -> str:
		...

	def clearScriptErrors(self, recurse=False, error='*'):
		...

	TDResources = _Expando()


# noinspection PyUnusedLocal
def op(path) -> '_AnyOpT':
	...


op.TDResources = _Expando()
op.TDResources.op = op

iop = _Expando()  # type: Any
ipar = _Expando()  # type: Any


# noinspection PyUnusedLocal
def ops(*paths) -> List['_AnyOpT']:
	...


# noinspection PyUnusedLocal
def var(name) -> str:
	...


# noinspection PyUnusedLocal
def varExists(name: str) -> bool:
	...


# noinspection PyUnusedLocal
def varOwner(name: str) -> Optional['_AnyOpT']:
	...


def isMainThread() -> bool:
	...


# clears textport
def clear() -> None:
	...


class Run:
	active: bool
	group: str
	isCell: bool
	isDAT: bool
	isString: bool
	path: OP
	remainingFrames: int
	remainingMilliseconds: int
	source: Union['DAT', 'Cell', str]

	def kill(self):
		...


class Runs(List[Run]):
	...


class td:
	Monitor: Monitor
	Monitors: Monitors
	Attribute: 'Attribute'
	me: OP
	absTime: 'AbsTime'
	app: 'App'
	ext: Any
	families: dict
	licenses: 'Licenses'
	mod: MOD
	monitors: 'Monitors'
	op: 'OP'
	parent: '_Parent'
	iop: 'OP'
	ipar: 'OP'
	project: 'Project'
	root: 'OP'
	runs: Runs
	sysinfo: 'SysInfo'
	ui: 'UI'

	@classmethod
	def passive(cls, o) -> 'OP':
		...

	@classmethod
	def run(
		cls,
		script,
		*args,
		endFrame=False,
		fromOP: Optional['OP'] = None,
		asParameter=False,
		group=None,
		delayFrames=0,
		delayMilliSeconds=0,
		delayRef: Optional['OP'] = None
	) -> Run:
		...

	@classmethod
	def fetchStamp(cls, key, default) -> Union[_ValueT, str]:
		...

	@classmethod
	def var(cls, varName) -> str:
		...

	@classmethod
	def varExists(cls, varName) -> bool:
		...

	@classmethod
	def varOwner(cls, varName) -> Optional['OP']:
		...


run = td.run


class _Matrix:
	vals: List[float]
	rows: List[List[float]]
	cols: List[List[float]]

	def __init__(self, *values):
		...

	def transpose(self):
		...

	def invert(self):
		...

	def determinant(self) -> float:
		...

	def copy(self) -> '_Matrix':
		...

	def identity(self):
		...

	def translate(self, tx, ty, tz, fromRight=False):
		...

	def rotate(self, rx, ry, rz, fromRight=False, pivot=None):
		...

	def rotateOnAxis(self, rotationAxis, angle, fromRight=False, pivot=None):
		...

	def scale(self, sx, sy, sz, fromRight=False, pivot=None):
		...

	def lookat(self, eyePos, target, up):
		...

	def decompose(self) -> Tuple[Tuple]:
		...


class _Position:
	x: int
	y: int
	z: int

	def __init__(self, *vals):
		...

	def translate(self, x, y, z):
		...

	def scale(self, x, y, z):
		...

	def copy(self) -> '_Position':
		...

	def __getitem__(self, item: int) -> float:
		...

	def __setitem__(self, key, value):
		...

	def __mul__(self, other: Union[float, _Matrix]) -> Union[float, '_Position']:
		...

	def __add__(
		self, other: Union[float, '_Position', '_Vector']
	) -> Union[float, '_Position']:
		...

	def __sub__(
		self, other: Union[float, '_Position', '_Vector']
	) -> Union[float, '_Position']:
		...

	def __div__(self, other: float) -> '_Position':
		...

	def __abs__(self) -> '_Position':
		...

	def __neg__(self) -> '_Position':
		...


class _Vector:
	x: float
	y: float
	z: float

	def __init__(self, *vals):
		...

	def translate(self, x, y, z):
		...

	def scale(self, x, y, z):
		...

	def __getitem__(self, item: int) -> float:
		...

	def __setitem__(self, key, value):
		...

	def normalize(self):
		...

	def length(self) -> float:
		...

	def lengthSquared(self) -> float:
		...

	def copy(self) -> '_Vector':
		...

	def distance(self, vec: '_Vector') -> float:
		...

	def lerp(self, vec: '_Vector', t: float) -> '_Vector':
		...

	def slerp(self, vec: '_Vector', t: float) -> '_Vector':
		...

	def project(self, vec1: '_Vector', vec2: '_Vector'):
		...

	def reflect(self, vec: '_Vector'):
		...


_OperableWithQuaternion = Union['Quaternion', Tuple[float, float, float,
																																																				float], _Matrix]


class Quaternion:
	x: float
	y: float
	z: float
	w: float

	def lerp(self, q2: _OperableWithQuaternion, factor: float) -> 'Quaternion':
		...

	def length(self) -> float:
		...

	def cross(self, q2: _OperableWithQuaternion) -> _Vector:
		...

	def rotate(self, vec: _Vector) -> _Vector:
		...

	def slerp(self, q2: _OperableWithQuaternion, factor: float) -> 'Quaternion':
		...

	def eulerAngles(self, order='xyz') -> Tuple[float, float, float]:
		...

	def fromEuler(self, order='xyz') -> Tuple[float, float, float]:
		...

	def axis(self) -> _Vector:
		...

	def dot(self, q2: _OperableWithQuaternion) -> float:
		...

	def exp(self) -> 'Quaternion':
		...

	def copy(self) -> 'Quaternion':
		...

	def log(self) -> 'Quaternion':
		...

	def inverse(self) -> None:
		...

	def angle(self) -> float:
		...

	def __imul__(self, other: _OperableWithQuaternion) -> 'Quaternion':
		...


_OperableWithColor = Union['_Color', Tuple[float, float, float, float],
																											List[float], float]


class _Color:
	r: float
	g: float
	b: float
	a: float

	def __init__(self, *vals):
		...

	def __abs__(self) -> '_Color':
		...

	def __add__(self, other: _OperableWithColor) -> '_Color':
		...

	def __sub__(self, other: _OperableWithColor) -> '_Color':
		...

	def __mul__(self, other: _OperableWithColor) -> '_Color':
		...

	def __floordiv__(self, other: _OperableWithColor) -> '_Color':
		...

	def __truediv__(self, other: _OperableWithColor) -> '_Color':
		...

	def __iadd__(self, other: _OperableWithColor) -> '_Color':
		...

	def __isub__(self, other: _OperableWithColor) -> '_Color':
		...

	def __imul__(self, other: _OperableWithColor) -> '_Color':
		...

	def __ifloordiv__(self, other: _OperableWithColor) -> '_Color':
		...

	def __itruediv__(self, other: _OperableWithColor) -> '_Color':
		...

	def __radd__(self, other: _OperableWithColor) -> '_Color':
		...

	def __rsub__(self, other: _OperableWithColor) -> '_Color':
		...

	def __rmul__(self, other: _OperableWithColor) -> '_Color':
		...

	def __rfloordiv__(self, other: _OperableWithColor) -> '_Color':
		...

	def __rtruediv__(self, other: _OperableWithColor) -> '_Color':
		...

	def __len__(self):
		return 4

	def __getitem__(self, item) -> float:
		...

	def __setitem__(self, key, value):
		...

	def __iter__(self):
		...


class _ArcBall:

	def beginPan(self, u, v) -> None:
		...

	def beginRotate(self, u, v) -> None:
		...

	def beginDolly(self, u, v) -> None:
		...

	def pan(self, u, v) -> None:
		...

	def panTo(self, u, v, scale=1.0) -> None:
		...

	def rotateTo(self, u, v, scale=1.0) -> None:
		...

	def dolly(self, z) -> None:
		...

	def dollyTo(self, u, v, scale=1.0) -> None:
		...

	def transform(self) -> _Matrix:
		...

	def setTransform(self, matrix: _Matrix) -> None:
		...

	def identity(self) -> None:
		...


class _PathInfo(str):
	path: str
	ext: str  # includes "."
	fileType: str
	absPath: str
	exists: bool
	isDir: bool
	isFile: bool

	# noinspection PyMissingConstructor,PyUnusedLocal
	def __init__(self, path: Optional[str] = None):
		...


class _Dependency:

	def __init__(self, _=None):
		self.val = None

	def modified(self):
		...

	callbacks: List[Callable[[dict], None]]
	ops: List['_AnyOpT']
	listAttributes: '_ListAttributesList'


class tdu:

	@staticmethod
	def legalName(s: str) -> str:
		...

	@staticmethod
	def legalMenuName(s: str) -> str:
		...

	# noinspection PyShadowingBuiltins
	@staticmethod
	def clamp(inputVal, min, max):
		...

	@staticmethod
	def remap(inputVal, fromMin, fromMax, toMin, toMax):
		...

	@staticmethod
	def rand(seed: Any) -> float:
		...

	@staticmethod
	def base(s: str) -> str:
		...

	@staticmethod
	def digits(s: str) -> Optional[int]:
		...

	ArcBall = _ArcBall
	Dependency = _Dependency
	Position = _Position
	Vector = _Vector
	Color = _Color
	Matrix = _Matrix
	PathInfo = _PathInfo

	# noinspection PyShadowingBuiltins
	@staticmethod
	def split(string, eval=False) -> List[str]:
		...

	@staticmethod
	def expand(pattern: str) -> List[str]:
		...

	@staticmethod
	def match(pattern, inputList, caseSensitive=True) -> List[str]:
		...

	@staticmethod
	def collapsePath(path: str, asExpression=False) -> str:
		...

	@staticmethod
	def expandPath(path: str) -> str:
		...

	@staticmethod
	def tryExcept(
		func1: Callable[[], Any], func2OrValue: Union[Callable[[], Any], Any]
	) -> Any:
		...

	@staticmethod
	def forceCrash():
		...

	fileTypes = {
		'audio': ['aif', 'aiff', 'flac', 'm4a', 'mp3', 'ogg', 'wav'],
		'channel': ['aif', 'aiff', 'bchan', 'bclip', 'chan', 'clip', 'csv', 'wav'],
		'component': ['tox'],
		'geometry': ['bhclassic', 'hclassic', 'obj', 'tog'],
		'image': [
			'bmp', 'dds', 'dpx', 'exr', 'ffs', 'fit', 'fits', 'gif', 'hdr', 'jpeg',
			'jpg', 'pic', 'png', 'swf', 'tga', 'tif', 'tiff'
		],
		'midi': ['mid', 'midi'],
		'movie': [
			'3gp', 'avi', 'flv', 'm2ts', 'm4v', 'mkv', 'mov', 'mp4', 'mpeg', 'mpg',
			'mts', 'mxf', 'r3d', 'ts', 'webm', 'wmv'
		],
		'object': ['3ds', 'abc', 'dae', 'dxf', 'fbx', 'obj', 'usd', 'usda', 'usdc'],
		'project': ['toe'],
		'text': [
			'csv', 'dat', 'frag', 'glsl', 'html', 'md', 'py', 'rtf', 'tsv', 'txt',
			'vert', 'xml'
		],
		'material': ['sbsar'],
		'pointdata':
		['csv', 'exr', 'fit', 'fits', 'obj', 'ply', 'pts', 'txt', 'xyz']
	}


class JustifyType(_E.Enum):
	TOPLEFT = 0
	TOPCENTER = 0
	TOPRIGHT = 0
	CENTERLEFT = 0
	CENTER = 0
	CENTERRIGHT = 0
	BOTTOMLEFT = 0
	BOTTOMCENTER = 0
	BOTTOMRIGHT = 0


class ParMode(_E.Enum):
	CONSTANT = 0
	EXPRESSION = 1
	EXPORT = 2
	BIND = 3


ExpandoStub = _Expando


class Cell(SupportsInt, SupportsAbs, SupportsFloat, SupportsBytes):
	val: str
	row: int
	col: int

	def offset(self, r: int, c: int) -> Optional['Cell']:
		...


_NameOrIndex = Union[str, int, 'Cell', 'Channel']
_NamesOrIndices = Iterable[_NameOrIndex]


class DAT(OP):

	def row(self, *nameorindex: _NameOrIndex, caseSensitive=True) -> List[Cell]:
		...

	def col(self, *nameorindex: _NameOrIndex, caseSensitive=True) -> List[Cell]:
		...

	def rows(self,
										*nameorindex: _NameOrIndex,
										caseSensitive=True) -> List[List[Cell]]:
		...

	def cols(self,
										*nameorindex: _NameOrIndex,
										caseSensitive=True) -> List[List[Cell]]:
		...

	def clear(self, keepSize=False, keepFirstRow=False, keepFirstCol=False):
		...

	# noinspection PyMethodOverriding
	def copy(self, dat: 'DAT'):
		...

	def appendRow(
		self,
		cells: Union[List[Any], Tuple[Any, ...]],
		nameOrIndex: Optional[_NameOrIndex] = None,
		sort: Optional[_NameOrIndex] = None
	):
		...

	def appendCol(
		self,
		cells: List[Any],
		nameOrIndex: Optional[_NameOrIndex] = None,
		sort: Optional[_NameOrIndex] = None
	):
		...

	def appendRows(
		self,
		cells: List[Union[List[Any], Tuple[Any, ...]]],
		nameOrIndex: Optional[_NameOrIndex] = None,
		sort: Optional[_NameOrIndex] = None
	):
		...

	def appendCols(
		self,
		cells: List[List[Any]],
		nameOrIndex: Optional[_NameOrIndex] = None,
		sort: Optional[_NameOrIndex] = None
	):
		...

	def insertRow(
		self, vals: List[Any], nameOrIndex: _NameOrIndex, sort=None
	) -> int:
		...

	def insertCol(
		self, vals: List[Any], nameOrIndex: _NameOrIndex, sort=None
	) -> int:
		...

	def replaceRow(
		self, nameOrIndex: _NameOrIndex, vals: List[Any], entireRow=True
	) -> int:
		...

	def replaceCol(
		self, nameOrIndex: _NameOrIndex, vals: List[Any], entireCol=True
	) -> int:
		...

	def deleteRow(self, nameOrIndex: _NameOrIndex):
		...

	def deleteCol(self, nameOrIndex: _NameOrIndex):
		...

	def deleteRows(self, vals: _NamesOrIndices):
		...

	def deleteCols(self, vals: _NamesOrIndices):
		...

	def setSize(self, numrows: int, numcols: int):
		...

	def __getitem__(self, rowcol: Tuple[_NameOrIndex, _NameOrIndex]) -> Cell:
		...

	def __setitem__(self, rowcol: Tuple[_NameOrIndex, _NameOrIndex], value):
		...

	def cell(
		self,
		rowNameOrIndex: _NameOrIndex,
		colNameOrIndex: _NameOrIndex,
		caseSensitive=True
	) -> Optional[Cell]:
		...

	def cells(
		self,
		rowNameOrIndex: _NameOrIndex,
		colNameOrIndex: _NameOrIndex,
		caseSensitive=True
	) -> List[Cell]:
		...

	def findCell(
		self,
		pattern: str,
		rows: Optional[_NamesOrIndices] = None,
		cols: Optional[_NamesOrIndices] = None,
		valuePattern=True,
		rowPattern=True,
		colPattern=True,
		caseSensitive=False
	) -> Optional[Cell]:
		...

	def findCells(
		self,
		pattern: str,
		rows: Optional[_NamesOrIndices] = None,
		cols: Optional[_NamesOrIndices] = None,
		valuePattern=True,
		rowPattern=True,
		colPattern=True,
		caseSensitive=False
	) -> List[Cell]:
		...

	def write(self, *args, **kwargs) -> str:
		...

	def run(
		self,
		*args,
		endFrame=False,
		fromOP: Optional[OP] = None,
		asParameter=False,
		group=None,
		delayFrames=0,
		delayMilliSeconds=0,
		delayRef: Optional[OP] = None
	) -> Run:
		...

	def save(
		self,
		filepath: Optional[str] = None,
		append=False,
		createFolders=False
	) -> str:
		...

	module: 'MOD'
	numRows: int
	numCols: int
	text: str
	isTable: bool
	isText: bool
	locals: Dict[str, Any]


class evaluateDAT(DAT):
	exprCell: 'Cell'
	exprCol: int
	exprRow: int
	exprTable: 'DAT'
	inputCell: 'Cell'
	inputCol: int
	inputRow: int
	inputTable: 'DAT'


class oscoutDAT(DAT):

	def sendBytes(self, *messages) -> int:
		...

	def sendOSC(
		self,
		*addressesFollowedByValueLists: Union[str, List[Any]],
		asBundle=True,
		useNonStandardTypes=True,
		use64BitPrecision=False
	) -> int:
		...

	def send(self, *messages: str, terminator='') -> int:
		...


oscinDAT = oscoutDAT


class webclientDAT(DAT):

	def request(
		self,
		url: str,
		method: str,
		header: Optional[dict] = None,
		data=None,
		pars: Optional[dict] = None,
		authType: Optional[str] = None,
		username: Optional[str] = None,
		password: Optional[str] = None,
		appKey: Optional[str] = None,
		appSecret: Optional[str] = None,
		oauth1Token: Optional[str] = None,
		oauth1Secret: Optional[str] = None,
		oauth2Token: Optional[str] = None,
		uploadFile: Optional[str] = None,
	) -> None:
		...


class CHOP(OP):
	numChans: int
	numSamples: int
	start: float
	end: float
	rate: float
	export: bool
	exportChanges: int
	isCHOP: bool
	isTimeSlice: bool

	def __getitem__(self, nameOrIndex: _NameOrIndex) -> 'Channel':
		...

	def chan(self,
										*nameOrIndex: _NameOrIndex,
										caseSensitive=True) -> Optional['Channel']:
		...

	def chans(self,
											*nameOrIndex: _NameOrIndex,
											caseSensitive=True) -> List['Channel']:
		...

	def numpyArray(self) -> 'numpy.recarray':
		...

	def convertToKeyframes(self, tolerance=0.1) -> 'animationCOMP':
		...

	def save(self, filepath) -> str:
		...


class midioutCHOP(CHOP):

	def send(self, *messages: Union[int, str]) -> None:
		...

	def sendExclusive(self, *messages: Union[int, str]) -> None:
		...

	def sendBalance(self, channel: int, value: int) -> None:
		...

	# TODO: figure out what the appropriate type for value is
	def sendControl(self, channel: int, index: int, value: Any) -> None:
		...


class COMP(OP):
	extensions: list
	extensionsReady: bool
	clones: List['COMP']
	componentCloneImmune: bool
	vfs: 'VFS'
	dirty: bool
	externalTimeStamp: int
	currentChild: '_AnyOpT'
	selectedChildren: List['_AnyOpT']
	pickable: bool
	isPrivate: bool
	isPrivacyActive: bool
	isPrivacyLicensed: bool
	privacyFirmCode: int
	privacyProductCode: int
	privacyDeveloperName: str
	privacyDeveloperEmail: str
	inputCOMPs: List['_AnyCompT']
	outputCOMPs: List['_AnyCompT']
	inputCOMPConnectors: List['Connector']
	outputCOMPConnectors: List['Connector']

	def destroyCustomPars(self):
		...

	def sortCustomPages(self, *pages):
		...

	def appendCustomPage(self, name: str) -> 'Page':
		...

	def findChildren(
		self,
		type: Optional[Type] = None,
		name: Optional[str] = None,
		path: Optional[str] = None,
		depth: Optional[int] = None,
		text: Optional[str] = None,
		comment: Optional[str] = None,
		maxDepth: Optional[int] = 1,
		tags: Optional[List[str]] = None,
		allTags: Optional[List[str]] = None,
		parValue: Optional[str] = None,
		parExpr: Optional[str] = None,
		parName: Optional[str] = None,
		onlyNonDefaults: bool = False,
		key: Optional[Callable[['_AnyOpT'], bool]] = None,
	) -> 'List[_AnyOpT]':
		...

	# TODO: should this be generic?
	def copy(
		self, o: '_AnyOpT', name: Optional[str] = None, includeDocked=True
	) -> OP:
		...

	def create(
		self,
		OPtype: Union[str, Type['_AnyOpT']],
		name: Optional[str] = None,
		initialize=True
	) -> '_AnyOpT':
		...

	def collapseSelected(self):
		...

	def copyOPs(self, listOfOPs: List['_AnyOpT']) -> List['_AnyOpT']:
		...

	def initializeExtensions(self, index: Optional[int] = None) -> Any:
		...

	def loadTox(
		self,
		filepath: str,
		unwired=False,
		pattern: Optional[str] = None,
		password: Optional[str] = None
	) -> 'COMP':
		...

	def resetNetworkView(self, recurse: bool = False):
		...

	def save(
		self,
		filepath: str,
		createFolders: bool = False,
		password: Optional[str] = None
	) -> 'str':
		...

	def saveExternalTox(
		self, recruse: bool = False, password: Optional[str] = None
	) -> int:
		...

	def accessPrivateContents(self, key: str) -> bool:
		...

	@overload
	def addPrivacy(self, key: str, developerName: Optional[str] = None):
		...

	@overload
	def addPrivacy(
		self,
		firmCode: int,
		productCode: int,
		developerName: Optional[str] = None,
		developerEmail: Optional[str] = None
	):
		...

	def addPrivacy(self, *args, **kwargs):
		...

	def blockPrivateContents(self, key: str):
		...

	def removePrivacy(self, key: str) -> bool:
		...

	def setVar(self, name: str, value):
		...

	def unsetVar(self, name: str):
		...

	def vars(self, *patterns: str) -> list:
		...


class annotateCOMP(COMP):
	enclosedOPs: List['_AnyOpT']
	height: float
	utility: bool
	width: float
	x: float
	y: float


class textCOMP(COMP):
	editText: str
	selectedText: str
	textHeight: float
	textWidth: float

	def evalTextSize(self) -> Tuple[float, float]:
		...

	def formatText(self, text: str, editing=False) -> str:
		...

	def setCursorPosUV(self, u: float, v: float):
		...

	def setKeyboardFocus(self, selectAll=False):
		...


class PanelValue(SupportsFloat, SupportsInt, _ABC):
	name: str
	owner: OP
	val: Union[float, int, str]
	valid: bool


class Panel:
	owner: OP

	# Container
	select: PanelValue
	lselect: PanelValue
	mselect: PanelValue
	rselect: PanelValue
	reposition: PanelValue
	resize: PanelValue
	dragout: PanelValue
	ldragout: PanelValue
	mdragout: PanelValue
	rdragout: PanelValue
	ctrl: PanelValue
	alt: PanelValue
	shift: PanelValue
	cmd: PanelValue
	u: PanelValue
	v: PanelValue
	trueu: PanelValue
	truev: PanelValue
	rollu: PanelValue
	rollv: PanelValue
	dragrollu: PanelValue
	dragrollv: PanelValue
	dragrollover: PanelValue
	rollover: PanelValue
	inside: PanelValue
	insideu: PanelValue
	insidev: PanelValue
	radio: PanelValue
	lradio: PanelValue
	mradio: PanelValue
	rradio: PanelValue
	radioname: PanelValue
	lradioname: PanelValue
	mradioname: PanelValue
	rradioname: PanelValue
	children: PanelValue
	display: PanelValue
	enable: PanelValue
	key: PanelValue
	character: PanelValue
	focusselect: PanelValue
	click: PanelValue
	winopen: PanelValue
	wheel: PanelValue
	drag: PanelValue
	drop: PanelValue
	screenw: PanelValue
	screenh: PanelValue
	screenwm: PanelValue
	screenhm: PanelValue
	# Button
	state: PanelValue
	lstate: PanelValue
	mstate: PanelValue
	rstate: PanelValue
	picked: PanelValue
	# Field
	field: PanelValue
	fieldediting: PanelValue
	invalidkey: PanelValue
	focus: PanelValue
	# List
	scrollu: PanelValue
	scrollv: PanelValue
	# Slider
	stateu: PanelValue
	statev: PanelValue
	# Table
	celloverid: PanelValue
	cellfocusid: PanelValue
	cellselectid: PanelValue
	celllselectid: PanelValue
	cellmselectid: PanelValue
	cellrselectid: PanelValue
	cellradioid: PanelValue
	celldragid: PanelValue
	celldropid: PanelValue


class PanelCOMP(COMP):
	panel: Panel
	panelRoot: '_AnyOpT'
	panelChildren: List['_AnyCompT']
	x: int
	y: int
	width: int
	height: int
	marginX: int
	marginY: int
	marginWidth: int
	marginHeight: int

	def panelParent(self, n: int = 1) -> Optional['PanelCOMP']:
		...

	def interactMouse(
		self,
		u,
		v,
		leftClick: int = 0,
		middleClick: int = 0,
		rightClick: int = 0,
		left=False,
		middle=False,
		right=False,
		wheel: float = 0,
		pixels=False,
		screen=False,
		quiet=True
	) -> 'PanelCOMP':
		...

	def interactTouch(
		self,
		u,
		v,
		hover='id',
		start='id',
		move='id',
		end='id',
		pixels=False,
		screen=False,
		quiet=True,
		aux='data'
	) -> 'PanelCOMP':
		...

	def interactClear(self):
		...

	def interactStatus(self) -> List[list]:
		...

	def locateMouse(self) -> Tuple[float, float]:
		...

	def locateMouseUV(self) -> Tuple[float, float]:
		...

	def setFocus(self, moveMouse=False):
		...


class fieldCOMP(PanelCOMP):

	def setKeyboardFocus(self, selectAll=False):
		...


class buttonCOMP(PanelCOMP):

	def click(
		self, val, clickCount=1, force=False, left=False, middle=False, right=False
	):
		...


class sliderCOMP(PanelCOMP):

	def click(
		self,
		uOrV,
		v,
		clickCount=1,
		force=False,
		left=False,
		middle=False,
		right=False,
		vOnly=False
	):
		...


class containerCOMP(PanelCOMP):

	def click(
		self,
		u,
		v,
		clickCount=1,
		force=False,
		left=False,
		middle=False,
		right=False,
		group=None
	):
		...

	def clickChild(
		self,
		childIndex,
		clickCount=1,
		force=False,
		left=False,
		middle=False,
		right=False,
		group=None
	):
		...


widgetCOMP = containerCOMP


class listCOMP(PanelCOMP):
	attribs: 'ListAttributes'
	cellAttribs: '_ListAttributesGrid'
	colAttribs: '_ListAttributesList'
	focusCol: int
	focusRow: int
	radioCol: int
	radioRow: int
	rolloverCol: int
	rolloverRow: int
	rowAttribs: '_ListAttributesList'
	selectCol: int
	selectRow: int
	selectionBorderColor: _Color
	selectionColor: _Color
	selections: List[Tuple[int, int, int,
																								int]]  # [(startrow, startcol, endrow, endcol), ...]

	def scroll(self, row, col):
		...

	def setKeyboardFocus(self, row, col, selectAll=False):
		...


# used for listCOMP callbacks
class XYUVTuple(NamedTuple):
	x: float
	y: float
	u: float
	v: float


class opviewerCOMP(PanelCOMP):

	def isViewable(self, path: str) -> bool:
		...


class parameterCOMP(PanelCOMP):
	minWidth: int


class selectCOMP(PanelCOMP):
	...


# noinspection PyShadowingBuiltins
class tableCOMP(PanelCOMP):

	def getRowFromID(self, id) -> int:
		...

	def getColFromID(self, id) -> int:
		...

	def click(
		self,
		row,
		col,
		clickCount=1,
		force=False,
		left=False,
		middle=False,
		right=False
	):
		...

	def clickID(
		self, id, clickCount=1, force=False, left=False, middle=False, right=False
	):
		...

	def getCellID(self, row, col) -> int:
		...

	def setKeyboardFocus(self, row, col, selectAll=False):
		...


class ListAttributes:
	bgColor: _Color
	bottomBorderInColor: _Color
	bottomBorderOutColor: _Color
	colStretch: bool
	colWidth: float
	draggable: bool
	editable: bool
	focus: bool
	fontBold: bool
	fontFace: str
	fontItalic: bool
	fontSizeX: float
	fontSizeY: float
	sizeInPoints: bool
	help: str
	leftBorderInColor: _Color
	leftBorderOutColor: _Color
	radio: bool
	rightBorderInColor: _Color
	rightBorderOutColor: _Color
	rollover: bool
	rowHeight: float
	rowIndent: float
	rowStretch: bool
	select: bool
	text: str
	textColor: _Color
	textJustify: 'JustifyType'
	textOffsetX: float
	textOffsetY: float
	top: 'TOP'

	topBorderInColor: _Color
	topBorderOutColor: _Color
	wordWrap: bool


class _ListAttributesList(Sized, _ABC):

	def __getitem__(self, item: int) -> Optional[ListAttributes]:
		...


class _ListAttributesGrid(Sized, _ABC):

	def __getitem__(self, rowCol: Tuple[int, int]) -> Optional[ListAttributes]:
		...


class windowCOMP(COMP):
	scalingMonitorIndex: int
	isBorders: bool
	isFill: bool
	isOpen: bool
	width: int
	height: int
	x: int
	y: int
	contentX: int
	contentY: int
	contentWidth: int
	contentHeight: int

	def setForeground(self) -> bool:
		...


class timeCOMP(COMP):
	frame: float
	seconds: float
	rate: float
	play: bool
	timecode: str
	start: float
	end: float
	rangeStart: float
	rangeEnd: float
	loop: bool
	independent: bool
	tempo: float
	signature1: int
	signature2: int


_AnyPanelCompT = Union[PanelCOMP, fieldCOMP, buttonCOMP, sliderCOMP,
																							containerCOMP, widgetCOMP, listCOMP, opviewerCOMP,
																							parameterCOMP, selectCOMP, tableCOMP]

_AnyCompT = Union[COMP, _AnyPanelCompT, windowCOMP, timeCOMP]


class VFSFile:
	name: str
	size: int
	date: _DT.datetime
	virtualPath: str
	originalFilePath: str
	owner: OP
	byteArray: bytearray

	def destroy(self):
		...

	def export(self, folder: str) -> str:
		...


class VFS:
	owner: OP

	def __getitem__(self, item: str) -> VFSFile:
		...

	def addByteArray(self, byteArray: bytearray, name: str) -> VFSFile:
		...

	def addFile(self, filePath: str, overrideName=None) -> VFSFile:
		...

	def export(self, folder: str, pattern='*', overwrite=False) -> List[str]:
		...

	def find(self, pattern='*') -> List[VFSFile]:
		...


class Connector:
	index: int
	isInput: bool
	isOutput: bool
	inOP: '_AnyOpT'
	outOP: '_AnyOpT'
	owner: '_AnyOpT'
	connections: List['Connector']

	def connect(self, target: Union['_AnyOpT', 'Connector']):
		...

	def disconnect(self):
		...


_AttributeDataElementT = Union[float, int, str]
_AttributeDataTupleT = Union[(
	Tuple[_AttributeDataElementT],
	Tuple[_AttributeDataElementT, _AttributeDataElementT],
	Tuple[_AttributeDataElementT, _AttributeDataElementT, _AttributeDataElementT],
	Tuple[(
		_AttributeDataElementT, _AttributeDataElementT, _AttributeDataElementT,
		_AttributeDataElementT
	)],
)]
_AttributeDataT = Union[_AttributeDataElementT, _AttributeDataTupleT, _Vector,
																								_Position]


class Attribute:
	owner: 'SOP'
	name: str
	size: int
	type: type
	default: _AttributeDataT

	def destroy(self):
		...


class Attributes(Collection[Attribute], _ABC):
	owner: 'SOP'

	def create(self, name: str, default: _AttributeDataT = None) -> Attribute:
		...


class AttributeData(_AttributeDataTupleT):
	owner: 'SOP'
	val: _AttributeDataT


class Point:
	index: int
	owner: 'SOP'
	P: 'AttributeData'
	x: float
	y: float
	z: float

	def __getattr__(self, item) -> Any:
		...

	def __setattr__(self, key, value):
		...

	def destroy(self):
		...


class Points(_Sequence[Point], _ABC):
	owner: 'SOP'


class Vertex():
	index: int
	owner: 'SOP'
	point: Point
	prim: 'Prim'


class Prim(Sized, _Sequence[Vertex], _ABC):
	center: _Position
	index: int
	normal: _Vector
	owner: 'SOP'
	weight: float
	direction: _Vector
	min: _Position
	max: _Position
	size: _Position

	def destroy(self, destroyPoints=True):
		...

	def eval(self, u: float, v: float) -> _Position:
		...

	def __getitem__(self, item: Union[int, Tuple[int, int]]) -> Vertex:
		...


class Poly(Prim, _ABC):
	...


class Bezier(Prim, _ABC):
	anchors: List[Vertex]
	basis: List[float]
	closed: bool
	order: float
	segments: List[List[Vertex]]
	tangents: List[Tuple[Vertex, Vertex]]

	def insertAnchor(self, u: float) -> Vertex:
		...

	def updateAnchor(
		self,
		anchorIndex: int,
		targetPosition: _Position,
		tangents=True
	) -> _Position:
		...

	def appendAnchor(
		self, targetPosition: _Position, preserveShape=True
	) -> Vertex:
		...

	def updateTangent(
		self,
		tangentIndex: int,
		targetPosition: _Position,
		rotate=True,
		scale=True,
		rotateLock=True,
		scaleLock=True
	) -> _Position:
		...

	def deleteAnchor(self, anchorIndex: int):
		...


class Mesh(Prim, _ABC):
	closedU: bool
	closedV: bool
	numRows: int
	numCols: int


_AnyPrimT = Union[Prim, Poly, Bezier, Mesh]


class Prims(_Sequence[_AnyPrimT], _ABC):
	owner: 'SOP'


_GroupType = TypeVar('_GroupType', Point, _AnyPrimT)


class Group(Iterable[_GroupType]):
	default: Tuple[_GroupType]
	'''
	"the default values associated with this group"
	'''

	name: str
	owner: OP

	def add(self, item: Union[Point, Prim]):
		...

	def discard(self, item: Union[Point, Prim]):
		...

	def destroy(self):
		...


class SOP(OP):
	compare: bool
	template: bool
	points: Points
	prims: Prims
	numPoints: int
	numPrims: int
	numVertices: int
	pointAttribs: Attributes
	primAttribs: Attributes
	vertexAttribs: Attributes
	pointGroups: Dict[str, Group]
	primGroups: Dict[str, Group]
	center: _Position
	min: _Position
	max: _Position
	size: _Position

	def save(self, filepath: str, createFolders=False) -> str:
		...


class scriptSOP(SOP):

	def destroyCustomPars(self):
		...

	def sortCustomPages(self, *pages):
		...

	def appendCustomPage(self, name: str) -> 'Page':
		...

	def clear(self):
		...

	# noinspection PyMethodOverriding
	def copy(self, chop: CHOP):
		...

	def appendPoint(self) -> Point:
		...

	def appendPoly(self, numVertices: int, closed=True, addPoints=True) -> Poly:
		...

	def appendBezier(
		self, numVertices: int, closed=True, order=4, addPoints=True
	) -> Bezier:
		...

	def appendMesh(
		self,
		numROws: int,
		numCols: int,
		closedU=False,
		closedV=False,
		addPoints=True
	) -> Mesh:
		...


class TOP(OP):
	width: int
	height: int
	aspect: float
	aspectWidth: float
	aspectHeight: float
	depth: int
	gpuMemory: int
	curPass: int

	def sample(
		self,
		x: Optional[int] = None,
		y: Optional[int] = None,
		u: Optional[float] = None,
		v: Optional[float] = None
	) -> _Color:
		...

	def numpyArray(
		self, delayed=False, writable=False, neverNone=False
	) -> 'numpy.recarray':
		...

	def save(self, filepath, asynchronous=False, createFolders=False) -> 'str':
		...

	def saveByteArray(self, filetype) -> bytearray:
		...

	def cudaMemory(self) -> 'CUDAMemory':
		...


class CUDAMemory:
	ptr: Any
	size: int
	shape: 'CUDAMemoryShape'


class CUDAMemoryShape:
	width: int
	height: int
	numComps: int
	dataType: Any  # numpy data type e.g. numpy.uint8, numpy.float32


class glslTOP(TOP):
	compileResult: str


glslmultiTOP = glslTOP


class webrenderTOP(TOP):

	def sendKey(
		self, char: Union[str, int], shift=False, alt=False, ctrl=False, cmd=False
	):
		...

	def interactMouse(
		self,
		u: float,
		v: float,
		leftClick=0,
		middleClick=0,
		rightClick=0,
		left=False,
		middle=False,
		right=False,
		wheel=0,
		pixels=False,
		aux=None,
	):
		"""
		:param u: pos
		:param v:
		:param leftClick: number of left clicks
		:param middleClick: number of middle clicks
		:param rightClick: number of right clicks
		:param left: left button state
		:param middle: middle button state
		:param right: right button state
		:param wheel: mouse wheel
		:param pixels: treat coords as pixel offsets instead of normalized
		:param aux: auxilliary data
		:return:
		"""

	def executeJavaScript(self, script: str):
		...

	def sendString(self, char: str):
		...


class textTOP(TOP):
	curText: str
	cursorEnd: int
	cursorStart: int
	selectedText: str
	textHeight: int
	textWidth: int
	numLines: int
	ascender: float
	descender: float
	capHeight: float
	xHeight: float
	lineGap: float

	def fontSupportsCharts(self, s: str) -> bool:
		...

	def evalTextSize(self, s: str) -> Tuple[float, float]:
		...

	def lines(self) -> List['TextLine']:
		...


class scriptTOP(TOP):

	def copyNumpyArray(self, arr: numpy.recarray) -> None:
		...

	def copyCUDAMemory(self, address, size, shape: CUDAMemoryShape) -> None:
		...

	def loadByteArray(
		self, fileType: str, byteArray: Union[bytes, bytearray]
	) -> bool:
		...

	def destroyCustomPars(self):
		...

	def sortCustomPages(self, *pages):
		...

	def appendCustomPage(self, name: str) -> 'Page':
		...


class textSOP(SOP):
	numLines: int
	ascender: float
	descender: float
	capHeight: float
	xHeight: float
	lineGap: float
	numGlyphs: int

	def fontSupportsCharts(self, s: str) -> bool:
		...

	def lines(self) -> List['TextLine']:
		...


class TextLine:
	text: str
	origin: 'tdu.Position'
	lineWidth: float


class MAT(OP):
	...


_AnyOpT = Union[OP, DAT, COMP, CHOP, SOP, TOP, MAT, '_AnyCompT', '_AnyDatT']

baseCOMP = COMP
panelCOMP = PanelCOMP
mergeDAT = nullDAT = parameterexecuteDAT = parameterDAT = tableDAT = textDAT = scriptDAT = DAT
inDAT = outDAT = infoDAT = substituteDAT = DAT
parameterCHOP = nullCHOP = selectCHOP = inCHOP = outCHOP = CHOP
inTOP = outTOP = nullTOP = TOP
importselectSOP = SOP


class animationCOMP(COMP):

	def setKeyframe(
		self,
		position: float,
		channel='*',
		value=None,
		function: Optional[str] = None
	):
		...

	def deleteKeyframe(
		self,
		position: float,
		channel='*',
		value=None,
		function: Optional[str] = None
	):
		...


class objectCOMP(COMP):
	localTransform: _Matrix
	worldTransform: _Matrix

	def transform(self) -> _Matrix:
		...

	def setTransform(self, matrix: _Matrix):
		...

	def preTransform(self) -> _Matrix:
		...

	def setPreTransform(self, matrix: _Matrix):
		...

	def relativeTransform(self, target: COMP) -> _Matrix:
		...

	def importABC(
		self,
		filepath,
		lights=True,
		cameras=True,
		mergeGeometry=True,
		gpuDeform=True,
		rate=None,
		textureFolder=None,
		geometryFolder=None,
		animationFolder=None
	):
		...

	def importFBX(
		self,
		filepath,
		lights=True,
		cameras=True,
		mergeGeometry=True,
		gpuDeform=True,
		rate=None,
		textureFolder=None,
		geometryFolder=None,
		animationFolder=None
	):
		...


class cameraCOMP(objectCOMP):

	def projectionInverse(self, x, y) -> _Matrix:
		...

	def projection(self, x, y) -> _Matrix:
		...


geotextCOMP = objectCOMP


class scriptCHOP(CHOP):

	def destroyCustomPars(self):
		...

	def sortCustomPages(self, *pages):
		...

	def clear(self):
		...

	def appendCustomPage(self, name: str) -> 'Page':
		...

	# noinspection PyMethodOverriding
	def copy(self, chop: CHOP):
		...

	def appendChan(self, name: str) -> 'Channel':
		...


class timerCHOP(CHOP):
	beginFrame: List[Any]
	beginSample: List[Any]
	beginSeconds: List[Any]
	cycle: float
	fraction: float
	runningFraction: float
	runningFrame: float
	runningLengthFrames: float
	runningLengthSamples: float
	runningLengthSeconds: float
	runningLengthTimecode: str  # format 00:00:00.00
	runningSample: float
	runningSeconds: float
	runningTimecode: str  # format 00:00:00.00
	segment: float

	def goToNextSegment(self):
		...

	def goToCycleEnd(self):
		...

	def goTo(
		self,
		segment: Optional[float] = None,
		cycle: Optional[float] = None,
		endOfCycle=True,
		seconds: Optional[float] = None,
		frame: Optional[float] = None,
		sample: Optional[float] = None,
		fraction: Optional[float] = None
	):
		...

	def goToPrevSegment(self):
		...

	def lastCycle(self):
		...


class Peer:
	owner: OP
	port: int
	address: str
	hostname: str

	def close(self) -> bool:
		...

	def sendBytes(self, *messages) -> int:
		...

	def sendOSC(
		self,
		address: str,
		*values,
		asBundle=False,
		useNonStandardTypes=True,
		use64BitPrecision=False
	) -> int:
		...

	def send(self, *messages: str, terminator='') -> int:
		...


class udpinDAT(DAT):

	def sendBytes(self, *messages) -> int:
		...

	def sendOSC(
		self,
		address: str,
		*values,
		asBundle=False,
		useNonStandardTypes=True,
		use64BitPrecision=False
	) -> int:
		...

	def send(self, *messages: str, terminator='') -> int:
		...


udtinDAT = udpinDAT


class tcpipDAT(DAT):

	def sendBytes(self, *messages) -> int:
		...

	def send(self, *messages: str, terminator='') -> int:
		...


_AnyDatT = Union[DAT, tcpipDAT, udpinDAT, oscoutDAT, oscinDAT, evaluateDAT,
																	webclientDAT]


class App:
	architecture: str
	binFolder: str
	build: str
	compileDate: Tuple[int, int, int]  # year, month, day
	configFolder: str
	desktopFolder: str
	enableOptimizedExprs: bool
	installFolder: str
	launchTime: float  # seconds since launch
	logExtensionCompiles: bool
	osName: str
	osVersion: str
	power: bool
	preferencesFolder: str
	product: str
	recentFiles: List[str]
	samplesFolder: str
	userPaletteFolder: str
	version: str
	windowColorBits: int

	def addNonCommercialLimit(self, password: Optional[str] = None) -> None:
		...

	def removeNonCommercialLimit(self, password: Optional[str] = None) -> bool:
		...

	def addResolutionLimit(
		self, x: int, y: int, password: Optional[str] = None
	) -> None:
		...

	def removeResolutionLimit(self, password: Optional[str] = None) -> bool:
		...


app: App


class RenderPickEvent(tuple):
	u: float
	v: float
	select: bool
	selectStart: bool
	selectEnd: bool
	pickOp: OP
	pos: _Position
	texture: _Position
	color: Tuple[float, float, float, float]
	normal: _Vector
	depth: float
	instanceId: int


class Dongle:
	serialNumber: int

	def applyUpdate(self, update: str) -> None:
		...

	def createUpdateContext(self) -> str:
		...


class DongleList(List[Dongle]):

	def refreshDongles(self) -> None:
		...

	def encrypt(
		self, firmCode, productCode, data: Union[str, bytearray]
	) -> bytearray:
		...

	def productCodeInstalled(self) -> bool:
		...


class License:
	index: int
	isEnabled: bool
	isRemotelyDisabled: bool
	key: str
	remoteDisableDate: Tuple[int, int, int]  # year, month, day
	status: int
	statusMessage: str
	systemCode: str
	type: str
	updateExpiryDate: Tuple[int, int, int]  # year, month, day
	version: int


class Licenses(List[License]):
	disablePro: bool
	dongles: DongleList
	machine: str
	systemCode: str
	type: str

	def install(self, key: str) -> bool:
		...


class Bounds(NamedTuple):
	min: Any
	max: Any
	center: Any
	size: Any


class ArtNetDevice(NamedTuple):
	ip: bytes
	port: int
	version: int
	netswitch: int
	subswitch: int
	oem: int
	ubea: int
	status1: int
	estacode: int
	shortname: int
	longname: int
	report: int
	numports: int
	porttypes: bytes
	goodinputs: bytes
	goodoutputs: bytes
	swin: bytes
	swout: bytes
	swvideo: int
	swmacro: int
	swremote: int
	style: int
	mac: bytes
	bindip: bytes
	bindindex: int
	status2: int


class EtherDreamDevice(NamedTuple):
	ip: Any
	port: Any
	mac_address: Any
	hw_revision: Any
	sw_revision: Any
	buffer_capacity: Any
	max_point_rate: Any
	protocol: Any
	light_engine_state: Any
	playback_state: Any
	source: Any
	light_engine_flags: Any
	playback_flags: Any
	source_flags: Any
	buffer_fullness: Any
	point_rate: Any
	point_count: Any


class NDISource(NamedTuple):
	sourceName: Any
	url: Any
	streaming: Any
	width: Any
	height: Any
	fps: Any
	audioSampleRate: Any
	numAudioChannels: Any


class Body:
	index: int
	owner: OP
	rotate: _Vector
	translate: _Position
	angularVelocity: _Vector
	linearVelocity: _Vector

	def applyImpulseForce(
		self,
		force,
		relPos: Optional[Union[_Position, _Vector, Tuple[float, float,
																																																			float]]] = None
	):
		...

	def applyTorque(self, torque):
		...

	def applyImpulseTorque(self, torque):
		...

	def applyForce(
		self,
		force,
		relPos: Optional[Union[_Position, _Vector, Tuple[float, float,
																																																			float]]] = None
	):
		...


class Bodies(List[Body]):
	...


class actorCOMP(COMP):
	bodies: Bodies


class Actors(List[actorCOMP]):
	...


class bulletsolverCOMP(COMP):
	actors: Actors


# noinspection PyUnusedLocal
def debug(*args):
	...


class AbsTime:
	frame: float
	seconds: float
	step: float
	stepSeconds: float


root = baseCOMP()
absTime = AbsTime()

me = OP()  # type: _AnyOpT
