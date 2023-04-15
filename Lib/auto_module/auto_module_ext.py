import math
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union, cast


def getOrCreateTextDAT(targetOp: COMP, datName: str) -> textDAT:
	if (dat := targetOp.op(datName)) is None:
		dat = targetOp.create(textDAT, datName)
		dat.par.language = 3
		dat.viewer = True

	return cast(textDAT, dat)


def layoutChildren(op: COMP, columns=4, xBase=0):
	children = op.findChildren(depth=1)
	for i, comp in enumerate(children):
		comp.nodeX = xBase + (i % columns) * 200
		comp.nodeY = (1 + math.floor(i / columns)) * -200


@dataclass
class Node:
	name: str


@dataclass
class File(Node):
	path: str
	parent: Union['Directory', 'RootDirectory']

	@property
	def shouldHaveTdModule(self) -> bool:
		return self.name != '__init__'

	def sync(self):
		if not self.shouldHaveTdModule:
			return

		assert self.parent, f'could not process file {self.name}, missing parent'
		assert self.parent.containerOp, f'could not process file {self.name}, parent missing containerOp'

		dat = getOrCreateTextDAT(self.parent.containerOp, self.name)

		dat.par.file = self.path
		dat.par.syncfile = 1


@dataclass
class RootDirectory(Node):
	children: Dict[str, Union[File, 'Directory']]
	containerOp: Optional[COMP]

	@property
	def containerOpName(self) -> str:
		return '_' + self.name

	@staticmethod
	def isContainerOpName(opName: str) -> bool:
		return opName.startswith('_')

	@staticmethod
	def containerOpNameToDirName(opName: str) -> str:
		return opName[1:]  # remove the _

	def isActiveModuleOp(self, moduleOp: Any) -> bool:
		opName = moduleOp.name
		childName = (
			self.containerOpNameToDirName(opName)
			if self.isContainerOpName(opName) else opName
		)

		return (
			childName in self.children and self.children[childName].shouldHaveTdModule
		)

	def destroyInactiveModuleOps(self):
		assert self.containerOp, f'cannot destroy inactive modules for {self.name} due to missing containerOp'

		inactiveOps = [
			childOp for childOp in self.containerOp.findChildren(depth=1)
			if not self.isActiveModuleOp(childOp)
		]
		for childOp in inactiveOps:
			childOp.destroy()

	def sync(self):
		assert self.containerOp, f'cannot sync directory {self.name} due to missing containerOp'

		for child in self.children.values():
			child.sync()

		self.destroyInactiveModuleOps()

		layoutChildren(self.containerOp)


@dataclass
class Directory(RootDirectory):
	parent: Union['Directory', 'RootDirectory']

	@property
	def shouldHaveTdModule(self) -> bool:
		return '__init__' in self.children

	def __post_init__(self):
		if self.parent and self.parent.containerOp:
			self.containerOp = cast(
				COMP, self.parent.containerOp.op(self.containerOpName)
			)

	def initializeContainerOp(self):
		assert self.parent.containerOp, (
			f'could not create container op for {self.name}, parent missing containerOp'
		)
		self.containerOp = cast(
			baseCOMP, self.parent.containerOp.create(baseCOMP, self.containerOpName)
		)

	def createAggregateModuleInParent(self):
		assert self.parent.containerOp, (
			f'could not create aggregate module for {self.name}, parent missing containerOp'
		)
		moduleText = '\n'.join(
			[
				f'{child.name}=mod(\'{self.containerOpName}/{child.name}\')'
				for child in self.children.values()
				if child.shouldHaveTdModule
			]
		)
		moduleDAT = getOrCreateTextDAT(self.parent.containerOp, self.name)
		moduleDAT.text = moduleText

	def sync(self):
		# Ignore directories that are not packages,
		# except project root which doesn't have a parent and should always be processed
		if not self.shouldHaveTdModule:
			return

		if self.containerOp is None:
			self.initializeContainerOp()

		super().sync()

		if self.parent:
			self.createAggregateModuleInParent()


# pylint: disable=too-few-public-methods
class AutoModuleExt:

	def __init__(self, ownerComp) -> None:
		self.ownerComp = ownerComp
		self.fileList: DAT = self.ownerComp.op('null_fileList')
		debug('AutoModule Extension initialized')
		# TODO: This causes infinite loop / crashes TD, why?
		# self.Sync()

	def Sync(self):
		basePath = self.ownerComp.par.Moduledirectory.eval()
		ignoredSuffixes = self.ownerComp.par.Ignoredsuffixes.eval().split(' ')

		iAmString: str = 5

		fileTree = RootDirectory(
			'root', children={}, containerOp=self.ownerComp.par.Modulecomp.eval()
		)

		for row in range(1, self.fileList.numRows):
			basename = self.fileList[row, 'basename'].val
			relpath = self.fileList[row, 'relpath'].val

			if any(basename.endswith(suffix) for suffix in ignoredSuffixes):
				continue

			*directoryNames, _ = relpath.split('/')

			root: Union[Directory, RootDirectory] = fileTree
			for d in directoryNames:

				if d not in root.children:
					root.children[d] = Directory(
						d, parent=root, children={}, containerOp=None
					)

				child = root.children[d]

				if isinstance(child, File):
					raise TypeError(
						f'unexpected file instance found at {d} where expecting Directory'
					)

				root = child

			root.children[basename] = File(
				basename, parent=root, path=f'{basePath}/{relpath}'
			)

		fileTree.sync()
