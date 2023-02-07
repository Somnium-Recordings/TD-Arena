import re

from tda import BaseExt, DroppedItem
from tdaUtils import clearChildren, layoutChildren, layoutComps

CTRL_SRC_NAME = 'ui:parameters'
'The name of source used when registering and updating state controllers'

SECTION_EFFECT_RE = re.compile(
	r'(/composition/(layer|clip)s/\d+/video/effects/\d+)/.*'
)

SECTION_GENERATOR_RE = re.compile(
	r'(/composition/(layer|clip)s/\d+/video/source/tox).*'
)


def matchEffectAddress(address: str):
	m = SECTION_EFFECT_RE.match(address)
	return m.group(1) if m else None


def matchGeneratorAddress(address: str):
	m = SECTION_GENERATOR_RE.match(address)
	return m.group(1) if m else None


def getSectionCloseScript(address: str):
	return f'op.uiState.SendMessage(\'{address}/clear\')'


def getSectionEditScript(address: str):
	return f'op.toxManager.EditCompositionAddress(\'{address}\')'


def getSectionSaveScript():
	return 'op.toxManager.Display()'


class ParameterContainer(BaseExt):

	@property
	def address(self):
		return self.ownerComponent.par.Address.eval()

	def __init__(self, ownerComponent, logger, state, effectBrowser):
		super().__init__(ownerComponent, logger)
		self.state = state
		self.effectBrowser = effectBrowser
		self.sectionTemplate = op.parametersUI.op('parameterSectionTemplate')
		self.parameterTemplates = {
			'Float': op.uiTheme.op('sliderHorzTemplate'),
			'Int': op.uiTheme.op('sliderHorzIntTemplate'),
			'Header': op.uiTheme.op('labelTemplate'),
			'StrMenu': op.uiTheme.op('dropDownMenuTemplate'),
			'Menu': op.uiTheme.op('dropDownMenuTemplate'),
			'Toggle': op.uiTheme.op('buttonRockerTemplate')
		}

		assert hasattr(
			ownerComponent.par, 'Address'
		), 'parameter containers must have an Address par'

		self.sectionContainer = self.ownerComponent.op('sections')
		assert self.sectionContainer, 'parameter containers must container a "sections" comp'

	def Init(self):
		self.sections = {}
		self.parameters = {}
		self.ResetActiveElementState()
		clearChildren(
			self.sectionContainer,
			exclude=[
				self.sectionContainer.op('dropControls').path,
				self.sectionContainer.op('parameterSpacer').path
			]
		)

		self.logInfo('initialized')

	def SyncSection(self, address):
		if address in self.sections:
			return

		self.logDebug(f'creating section for {address}')
		section = self.sectionContainer.copy(self.sectionTemplate, name='section')

		# TODO(#7): clean up this script business
		effectAddress = matchEffectAddress(address)
		if effectAddress:
			section.par.Onclosescript = getSectionCloseScript(effectAddress)
			section.par.Oneditscript = getSectionEditScript(effectAddress)
			section.par.Onsavescript = getSectionSaveScript()
			section.par.Address = effectAddress

		generatorAddress = matchGeneratorAddress(
			address
		) if not effectAddress else None
		if generatorAddress:
			# TODO(#7): add close script that clears the tox
			section.par.Oneditscript = getSectionEditScript(generatorAddress)
			section.par.Onsavescript = getSectionSaveScript()

		self.sections[address] = section
		self.updateSectionNetowrkPositions()

	def ResetActiveElementState(self):
		self.activeParameters = set()
		self.activeSections = set()

	def ClearInactiveElements(self):
		# NOTE: we clear inactive sections first to avoid choking on parameter deletion
		inactiveSections = set(self.sections.keys()) - self.activeSections
		for address in inactiveSections:
			self.logDebug(f'clearing inactive section at {address}')
			section = self.sections.pop(address)
			section.destroy()

		self.updateSectionNetowrkPositions()

		inactiveParameters = set(self.parameters.keys()) - self.activeParameters
		for address in inactiveParameters:
			self.logDebug(f'clearing inactive parameter at {address}')
			parameter = self.parameters.pop(address)
			self.state.DeregisterCtrl(address, CTRL_SRC_NAME)
			if parameter.valid:  # If parent section destroys the containing par this will be false
				parameter.destroy()

	def OnBeforeDestroy(self):
		for address in self.parameters:
			self.state.DeregisterCtrl(address, CTRL_SRC_NAME)

	def OnDrop(
		self, droppedItem: DroppedItem, targetSection=None, direction: str = None
	):
		# TODO: lookup targetSection & validate here once everything supports it

		if droppedItem.dropName.startswith('section'):
			self.onSectionDrop(droppedItem, targetSection, direction)
		elif droppedItem.dropName.startswith('effect'):
			self.onEffectDrop(droppedItem, targetSection, direction)
		else:
			raise NotImplementedError(
				f'unsupported item dropped: {droppedItem.dropName}'
			)

	def onEffectDrop(
		self, droppedItem: DroppedItem, targetSection=None, _direction: str = None
	):
		if targetSection is not None:
			self.logDebug('dropping onto targets not implemented yet, adding to end')

		(_, filePath) = self.effectBrowser.GetPath(droppedItem.dropName)
		self.state.SendMessage(f'{self.address}/video/effects/add', filePath)

	def onSectionDrop(
		self, droppedItem: DroppedItem, targetSection=None, direction: str = None
	):
		if targetSection is None:
			raise NotImplementedError(
				'dropping section onto parameter background not implemented yet'
			)

		droppedSection = op(droppedItem.itemPath).parent.section
		if droppedSection == targetSection:
			self.logDebug(f'{droppedSection} dropped on self, doing nothing')
			return

		# Set section order
		self.logDebug(f'dropped: ${droppedSection} on {direction}:{targetSection}')

		if direction == 't':
			targetPosition = 'above'
			alignOrderDelta = -0.5
		elif direction == 'b':
			targetPosition = 'below'
			alignOrderDelta = +0.5
		else:
			raise NotImplementedError(f'unsupported drop direction: {direction}')

		# Optimistically set the align order so UI updates while
		# we wait for reorder update from render
		droppedSection.par.alignorder = targetSection.par.alignorder.eval(
		) + alignOrderDelta

		self.state.SendMessage(
			f'{droppedSection.par.Address}/move', targetPosition,
			targetSection.par.Address
		)

	def getParameterSection(self, sectionAddress: str):
		if sectionAddress not in self.sections:
			self.logDebug(f'section not found for {sectionAddress}, initializing')
			self.SyncSection(sectionAddress)

		return self.sections[sectionAddress]

	def createSectionParameter(self, section, style, name):
		# These are hard-coded into the section template comp
		if name == 'Section Expanded':
			return section.op('sectionHeading')
		if name == 'Section Order':
			return section.op('sectionOrder')
		if name == 'Section Name':
			return section.op('sectionName')

		sectionContents = section.op('sectionContents')

		assert style in self.parameterTemplates, f'no template defined for "{style}" parameters'
		parameter = sectionContents.copy(
			self.parameterTemplates[style], name=name.replace('/', ' ')
		)
		layoutChildren(sectionContents, columns=1)

		return parameter

	def SetCtrlValue(self, address: str, newValue):
		if address not in self.parameters:
			self.logWarning(f'received value change for unknown parameter: f{address}')

		self.logDebug(f'setting control for {address} to {newValue}')
		self.parameters[address].par.Value0 = newValue

	def SyncParameter(
		self, address, label, style, normMin, normMax, menuLabels, order
	):  # pylint: disable=too-many-arguments
		sectionAddress, _ = address.rsplit(':', 1)  # The last value is the parameter
		self.activeParameters.add(address)
		self.activeSections.add(sectionAddress)

		if address in self.parameters:
			# if parameter in self.paths, do we need to do anything?
			#    will parameters change over time? Or only values?
			return

		if style == 'WH':
			self.logWarning(
				f'TODO: figure out what to do with WH parameters: {address}'
			)
			return

		self.logDebug(f'creating parameter {address}')

		section = self.getParameterSection(sectionAddress)
		parameter = self.createSectionParameter(section, style, label)
		self.parameters[address] = parameter
		self.state.RegisterCtrl(address, CTRL_SRC_NAME, self.SetCtrlValue)

		# Setting Valname0 to something that starts with /composition
		# triggers the OpFind -> Parameter Dat -> State.UpdateCtrlValue flow
		parameter.par.Valname0 = address

		# The section parameters are hard-coded, all we need is to set Valname0 to trigger binding
		if label.startswith('Section'):
			return

		parameter.par.alignorder = order
		parameter.par.Widgetlabel = label

		if style == 'Header':
			return  # don't try and set parameters that don't exist

		if style in ('StrMenu', 'Menu'):
			parameter.par.Menunames.expr = menuLabels
		elif style in ('Float', 'Int'):
			# TODO: propagate clamp values
			parameter.par.Value0.normMax = normMax
			parameter.par.Value0.max = normMax
			parameter.par.Value0.normMin = normMin
			parameter.par.Value0.min = normMin

	def updateSectionNetowrkPositions(self):
		layoutComps(self.sections.values(), columns=1)


class Parameters(BaseExt):

	def __init__(self, ownerComponent, logger):
		super().__init__(ownerComponent, logger)
		self.parameterList = ownerComponent.op('null_parameterList')
		self.containerList = ownerComponent.op('null_containerList')
		self.containerState = {}

		self.OnParameterChange()
		self.logInfo('ParamatersUI initialized')

	def OnParameterChange(self):
		self.logDebug('parameter change detected')

		activeAddresses = set()
		lastMatchedParameter = 0
		for i in range(1, self.containerList.numRows):
			containerPath = str(self.containerList[i, 'path'])
			containerAddress = str(self.containerList[i, 'address'])
			nextAddress = str(self.containerList[i + 1, 'address'])

			container = self.syncContainerState(containerAddress, containerPath)
			container.ResetActiveElementState()

			activeAddresses.add(containerAddress)

			# group parameters into "containers" if par address starts
			# with the container address
			# NOTE: this assumes both lists are sorted by OSC address
			hasMatched = False
			for j in range(lastMatchedParameter + 1, self.parameterList.numRows):
				parAddress = str(self.parameterList[j, 'address'])
				if parAddress.startswith(containerAddress):
					container.SyncParameter(
						parAddress,
						label=str(self.parameterList[j, 'label']),
						style=str(self.parameterList[j, 'style']),
						normMin=str(self.parameterList[j, 'normmin']),
						normMax=str(self.parameterList[j, 'normmax']),
						menuLabels=str(self.parameterList[j, 'menulabels']),
						order=str(self.parameterList[j, 'order']),
					)
					lastMatchedParameter = j
					hasMatched = True
				elif parAddress.startswith(nextAddress):
					# prevent re-checking unmatched pars on next iteration if we know there is a match
					lastMatchedParameter = j - 1
					break
				elif hasMatched:
					# We know that the rest won't since the lists are sorted
					break

			container.ClearInactiveElements()

		inactiveAddresses = set(self.containerState.keys()) - activeAddresses
		for address in inactiveAddresses:
			self.logDebug(f'clearing parameter container state for {address}')
			del self.containerState[address]

	def syncContainerState(self, address: str, opPath: str) -> ParameterContainer:
		if address not in self.containerState:
			self.logDebug(f'initializing parameter container state for {address}')
			containerOP = op(opPath)
			containerOP.Init()
			self.containerState[address] = containerOP

		return self.containerState[address]
