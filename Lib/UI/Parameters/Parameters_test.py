# pylint: disable=no-self-use,too-many-arguments,line-too-long,bad-whitespace
from unittest.mock import MagicMock, call

import pytest

from tdaTesting import MockOP, MockTable
from UI.Parameters import Parameters


def test_matchEffectAddress():
	assert Parameters.matchEffectAddress(
		'/composition/clips/4/video/effects/0/tox'
	) == '/composition/clips/4/video/effects/0'
	assert Parameters.matchEffectAddress('/composition/clips/4/video') is None


def test_getSectionCloseScript():
	assert Parameters.getSectionCloseScript(
		'/composition/clips/4/video/effects/0'
	) == 'op.uiState.SendMessage(\'/composition/clips/4/video/effects/0/clear\')'


class TestParameters():
	@pytest.fixture
	def parameterList(self):
		return MockTable(
			[ # yapf: disable
				['address',                       'label',   'style', 'normmin', 'normmax', 'menulabels', 'order'],
				['/composition/layers/0/Opacity', 'Opacity', 'Float', '0',       '1',       '',           '1'],
				['/composition/layers/1/Opacity', 'Opacity', 'Float', '0',       '1',       '',           '2'],
				['/composition/layers/2/Opacity', 'Opacity', 'Float', '0',       '1',       '',           '3'],
				['/composition/layers/3/Opacity', 'Opacity', 'Float', '0',       '1',       '',           '4']
			]
		)

	@pytest.fixture
	def containerList(self):
		return MockTable(
			[ # yapf: disable
				['address',                'path'                                                                        ],
				['/composition/layers/1',  '/tdArena/ui/parametersUI/leftControlContainer/layerControlsContainer/layer1'],
				['/composition/layers/3',  '/tdArena/ui/parametersUI/leftControlContainer/layerControlsContainer/layer3']
			]
		)

	@pytest.fixture
	def mockContainerOP1(self):
		return MagicMock()

	@pytest.fixture
	def mockContainerOP3(self):
		return MagicMock()

	@pytest.fixture
	def parameters(
		self, ownerComponent, op: MockOP, logger, parameterList, containerList,
		mockContainerOP1, mockContainerOP3
	):
		# yapf: disable
		op.addPath('/tdArena/ui/parametersUI/leftControlContainer/layerControlsContainer/layer1', mockContainerOP1)
		op.addPath('/tdArena/ui/parametersUI/leftControlContainer/layerControlsContainer/layer3', mockContainerOP3)
		# yapf: enable
		Parameters.op = op

		ownerComponent.op = MockOP()
		ownerComponent.op.addPath('null_parameterList', parameterList)
		ownerComponent.op.addPath('null_containerList', containerList)

		return Parameters.Parameters(ownerComponent, logger)

	def test_OnParameterChange(
		self, parameters: Parameters, containerList: MockTable,
		mockContainerOP1: MagicMock, mockContainerOP3: MagicMock
	):
		# NOTE: OnParameterChange called in init, so testing state here
		assert len(parameters.containerState) == 2
		mockContainerOP1.Init.assert_called_once()
		mockContainerOP1.SyncParameter.assert_has_calls(
			[
				call(
					'/composition/layers/1/Opacity',
					label='Opacity',
					style='Float',
					normMin='0',
					normMax='1',
					menuLabels='',
					order='2'
				)
			]
		)

		mockContainerOP3.Init.assert_called_once()
		mockContainerOP3.SyncParameter.assert_has_calls(
			[
				call(
					'/composition/layers/3/Opacity',
					label='Opacity',
					style='Float',
					normMin='0',
					normMax='1',
					menuLabels='',
					order='4'
				)
			]
		)

		containerList.deleteRow(2)
		parameters.OnParameterChange()
		assert len(parameters.containerState) == 1


# Unit testing was a nice idea, but there's just too much to mock to
# make it worthwhile in touch :'(
#
# class TestParameterContainer:
# 	@pytest.fixture
# 	def sections(self):
# 		return MagicMock()

# 	@pytest.fixture
# 	def parameterContainer(self, op, sections, logger, ownerComponent):
# 		Parameters.op = op

# 		ownerComponent.op.addPath('sections', sections)
# 		ownerComponent.par = MockParameterBag(
# 			{'Address': MockParameter('/composition/layers/1')}
# 		)

# 		return Parameters.ParameterContainer(ownerComponent, logger)

# 	def test_Init(
# 		self, parameterContainer, uiThemeSectionTemplate, sections: MagicMock
# 	):
# 		assert parameterContainer
# 		sections.copy.assert_called_once_with(call(uiThemeSectionTemplate, name='Layer'))
