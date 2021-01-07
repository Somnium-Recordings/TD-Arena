import re

from tda import BaseExt
from tdaUtils import clearChildren, layoutChildren, layoutComps

SECTION_EFFECT_RE = re.compile(
	r'(/composition/clips/\d+/video/effects/\d+)/.*'
)


def getSectionCloseScript(address: str):
	m = SECTION_EFFECT_RE.match(address)
	if m:
		return f'op.uiState.SendMessage(\'{m.group(1)}/clear\')'

	return None


class ParameterContainer(BaseExt):
	@property
	def address(self):
		return self.ownerComponent.par.Address.eval()

	def __init__(self, ownerComponent, logger):
		super().__init__(ownerComponent, logger)
		self.sectionTemplate = op.uiTheme.op('parameterSectionTemplate')
		self.parameterTemplates = {
			'Float': op.uiTheme.op('sliderHorzTemplate'),
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
		clearChildren(self.sectionContainer)

		self.logInfo('initialized')

	def SyncSection(self, address):
		if address in self.sections:
			return

		self.logDebug(f'creating section for {address}')
		section = self.sectionContainer.copy(self.sectionTemplate, name='section')

		section.par.Onclosescript = getSectionCloseScript(address)

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
			if parameter.valid:  # If parent section destroys the containing par this will be fals
				parameter.destroy()

	def getParameterSection(self, sectionAddress: str):
		if sectionAddress not in self.sections:
			self.logDebug(f'section not found for {sectionAddress}, initializing')
			self.SyncSection(sectionAddress)

		return self.sections[sectionAddress]

	def createSectionParameter(self, section, style, name):
		# These are hard-coded into the section template comp
		if name == 'Section Expanded':
			return section.op('section')
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

	def SyncParameter(
		self, address, label, style, normMin, normMax, menuLabels, order
	):  # pylint: disable=too-many-arguments
		sectionAddress, _ = address.rsplit('/', 1)  # The last value is the parameter
		self.activeParameters.add(address)
		self.activeSections.add(sectionAddress)

		if address in self.parameters:
			# if parameter in self.paths, do we need to do anything?
			#    will parameters change over time? Or only values?
			return

		if style == 'WH':
			self.logDebug(f'TODO: figure out what to do with WH parameters: {address}')
			return

		self.logDebug(f'creating parameter {address}')

		section = self.getParameterSection(sectionAddress)
		parameter = self.createSectionParameter(section, style, label)
		self.parameters[address] = parameter

		if style != 'Header':
			# NOTE: Setting Valname0 triggers UIState to initialize the parameter binding
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
		elif style == 'Float':
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
			self.logDebug('clearing parameter container state for {}'.format(address))
			del self.containerState[address]

	def syncContainerState(self, address: str, opPath: str) -> ParameterContainer:
		if address not in self.containerState:
			self.logDebug(
				'initializing parameter container state for {}'.format(address)
			)
			containerOP = op(opPath)
			containerOP.Init()
			self.containerState[address] = containerOP

		return self.containerState[address]
