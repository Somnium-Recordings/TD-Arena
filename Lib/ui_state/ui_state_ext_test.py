import logging
from unittest.mock import MagicMock

import pytest
from tdaTesting import MockOPFinder, MockOscinDAT

from .ui_state_ext import UIStateExt


class TestUIStateExt():

	@pytest.fixture()
	def oscinDat(self):
		return MockOscinDAT()

	@pytest.fixture()
	def uiStateExt(
		self, oscinDat: MockOscinDAT, ownerComponent: OP, op: MockOPFinder
	):
		op.addPath('oscin1', oscinDat)

		return UIStateExt(ownerComponent)

	def test_UpdateCtrlValue(
		self, uiStateExt: UIStateExt, oscinDat: MockOscinDAT,
		caplog: pytest.LogCaptureFixture
	):
		caplog.set_level(logging.DEBUG)
		ctrlUpdateHandler = MagicMock()
		uiStateExt.RegisterCtrl('/foo', 'test', ctrlUpdateHandler)
		oscinDat.sendOSC.assert_called_once_with('/foo', ('?', ))

		ctrlUpdateHandler.assert_not_called()
		uiStateExt.Dispatch('/foo', .1)

		# ctrlUpdateHandler.assert_called_once_with('/foo', .2)

		# uiStateExt.UpdateCtrlValue('/foo', .5, 'test')
		# oscinDat.sendOSC.assert_called_with('/foo', (.5, ))
