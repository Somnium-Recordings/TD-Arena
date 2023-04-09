# pylint: disable=too-many-arguments
from unittest.mock import MagicMock, call

import pytest
from tdaTesting import MockOP, MockTable

from . import ui_state_ext


class TestUIStateExt():

	@pytest.fixture
	def oscControlList(self):
		return MockTable([['path', 'address']])

	@pytest.fixture
	def initializedControlList(self):
		return MockTable([['path', 'address']])

	@pytest.fixture
	def oscIn(self):
		return MagicMock()

	@pytest.fixture()
	def state(
		self, ownerComponent, op, logger, oscIn, oscControlList,
		initializedControlList
	):
		ui_state_ext.op = op

		ownerComponent.op = MockOP()
		ownerComponent.op.addPath('opfind_oscControls', oscControlList)
		ownerComponent.op.addPath('oscin1', oscIn)
		ownerComponent.op.addPath(
			'table_initializedControls', initializedControlList
		)

		return ui_state_ext.UIStateExt(ownerComponent, logger)

	def test_OnCtrlOPListChange(
		self, op, oscControlList, state, oscIn, initializedControlList
	):
		oscControlList.appendRows(
			[
				[
					'/tdArena/ui/clipLauncherUI/layerContainerUI/layer1/sliderVert',
					'/composition/layers/1/Opacity',
				],
				[
					'/tdArena/ui/clipLauncherUI/layerContainerUI/layer2/sliderVert',
					'/composition/layers/2/Opacity',
				],
				[
					'/tdArena/ui/clipLauncherUI/layerContainerUI/layer3/sliderVert',
					'/composition/layers/3/Opacity',
				]
			]
		)

		state.OnCtrlOPListChange()

		assert state.oscControlState == {
			'/composition/layers/1/Opacity': {
				'op': op('/tdArena/ui/clipLauncherUI/layerContainerUI/layer1/sliderVert')
			},
			'/composition/layers/2/Opacity': {
				'op': op('/tdArena/ui/clipLauncherUI/layerContainerUI/layer2/sliderVert')
			},
			'/composition/layers/3/Opacity': {
				'op': op('/tdArena/ui/clipLauncherUI/layerContainerUI/layer3/sliderVert')
			}
		}
		oscIn.sendOSC.assert_has_calls(
			[
				call('/composition/layers/1/Opacity', ('?', )),
				call('/composition/layers/2/Opacity', ('?', )),
				call('/composition/layers/3/Opacity', ('?', )),
			]
		)
		assert oscIn.sendOSC.call_count == 3

		# Should not request current value after first init
		state.OnCtrlOPListChange()
		assert oscIn.sendOSC.call_count == 3

		# Should clear out inactive addresses
		initializedControlList.appendRow(
			['/composition/layers/2/Opacity', '/bar/path/to/chop']
		)
		oscControlList.deleteRow(2)
		oscControlList.deleteRow(2)
		state.OnCtrlOPListChange()

		assert state.oscControlState == {
			'/composition/layers/1/Opacity': {
				'op': op('/tdArena/ui/clipLauncherUI/layerContainerUI/layer1/sliderVert')
			}
		}
		assert oscIn.sendOSC.call_count == 3
		assert len(initializedControlList.rows()) == 0

	def test_onOSCReply(
		self, state, oscControlList, logger, ownerComponent, op,
		initializedControlList
	):
		oscControlList.appendRow(
			[
				'/tdArena/ui/clipLauncherUI/layerContainerUI/layer1/sliderVert',
				'/composition/layers/1/Opacity'
			],
		)
		state.OnCtrlOPListChange()
		state.onOSCReply('/composition/layers/1/Opacity', 123)

		assert op(
			'/tdArena/ui/clipLauncherUI/layerContainerUI/layer1/sliderVert'
		).par.Value0 == 123
		initializedRows = initializedControlList.rows()
		assert len(initializedRows) == 1
		assert initializedRows[0][0].val == '/composition/layers/1/Opacity'
		assert initializedRows[0][1].val == '/tdArena/ui/clipLauncherUI/layerContainerUI/layer1/sliderVert/valueOut' # yapf: disable

		state.onOSCReply('/unknown', 123)
		logger.Warning.assert_called_with(
			ownerComponent, 'received OSC reply for unknown address /unknown'
		)

		state.onOSCReply('/composition/layers/1/Opacity', 456, 789)
		logger.Warning.assert_called_with(
			ownerComponent,
			'expected OSC reply to have exactly 1 arg but got 2, ignoring message'
		)
		assert op(
			'/tdArena/ui/clipLauncherUI/layerContainerUI/layer1/sliderVert'
		).par.Value0 == 123
