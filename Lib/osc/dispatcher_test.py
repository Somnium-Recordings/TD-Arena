import gc
import logging
from unittest.mock import MagicMock

import pytest
from dispatcher import OSCDispatcher
from tdaTesting import MockOP, MockOscinDAT


class TestOSCDispatcher():

	@pytest.fixture()
	def oscIn(self):
		return MockOscinDAT()

	@pytest.fixture()
	def dispatcher(self, ownerComponent: OP):
		return OSCDispatcher(ownerComponent)

	# caplog.set_level(logging.DEBUG)

	def test_Dispatch_basic(self, dispatcher: OSCDispatcher, oscIn: MockOscinDAT):
		mockTarget1 = MockOP('/mock_target_1')
		mockUpdateHandler1 = MagicMock()
		dispatcher.Map(mockTarget1, '/foo', mockUpdateHandler1)

		mockTarget2 = MockOP('/mock_target_2')
		mockUpdateHandler2 = MagicMock()
		dispatcher.Map(mockTarget2, '/foo', mockUpdateHandler2)

		dispatcher.Dispatch(oscIn, '/foo', 1, 2)

		mockUpdateHandler1.assert_called_once_with('/foo', 1, 2)
		mockUpdateHandler2.assert_called_once_with('/foo', 1, 2)

	def test_Dispatch_unknownAddress(
		self, dispatcher: OSCDispatcher, oscIn: MockOscinDAT,
		caplog: pytest.LogCaptureFixture
	):
		dispatcher.Dispatch(oscIn, '/unknown')
		assert 'unmatched OSC address /unknown' in caplog.text

	def test_Dispatch_multipleMatches(
		self, dispatcher: OSCDispatcher, oscIn: MockOscinDAT
	):
		mockTarget1 = MockOP('/mock_target_1')
		mockUpdateHandler1 = MagicMock()
		dispatcher.Map(mockTarget1, '/foo', mockUpdateHandler1)

		mockCatchAll = MockOP('/state')
		mockCatchAllHandler = MagicMock()
		dispatcher.Map(mockCatchAll, '/*', mockCatchAllHandler)

		dispatcher.Dispatch(oscIn, '/foo', 1, 2)
		mockUpdateHandler1.assert_called_once_with('/foo', 1, 2)
		mockCatchAllHandler.assert_called_once_with('/foo', 1, 2)

	def test_Dispatch_excludeSelf(
		self, dispatcher: OSCDispatcher, oscIn: MockOscinDAT
	):
		mockCatchAllHandler = MagicMock()
		dispatcher.Map(oscIn, '/*', mockCatchAllHandler)

		dispatcher.Dispatch(oscIn, '/foo', 1)
		mockCatchAllHandler.assert_not_called()

	def test_MapControl(
		self, dispatcher: OSCDispatcher, oscIn: MockOscinDAT,
		caplog: pytest.LogCaptureFixture
	):
		caplog.set_level(logging.DEBUG)
		mockCatchAllHandler = MagicMock()
		dispatcher.Map(oscIn, '/*', mockCatchAllHandler, handleValueRequests=True)

		# a "non control" target on a separate path
		mockTarget0 = MockOP('/mock_target_0')
		mockUpdateHandler0 = MagicMock()
		dispatcher.Map(mockTarget0, '/f*', mockUpdateHandler0)

		mockTarget1 = MockOP('/mock_target_1')
		mockUpdateHandler1 = MagicMock()
		dispatcher.MapControl(mockTarget1, '/foo', mockUpdateHandler1)

		# ensure we request the current value when a control is registered
		# and we don't have the value tracked
		mockCatchAllHandler.assert_called_once_with('/foo', '?')
		mockUpdateHandler0.assert_not_called()
		mockUpdateHandler1.assert_not_called()

		mockTarget2 = MockOP('/mock_target_2')
		mockUpdateHandler2 = MagicMock()
		dispatcher.MapControl(mockTarget2, '/foo', mockUpdateHandler2)

		# ensure that we only request values once for multiple controls
		# registered on the same path
		assert mockCatchAllHandler.call_count == 1
		mockUpdateHandler1.assert_not_called()
		mockUpdateHandler2.assert_not_called()

		# Simulate receiving value response
		dispatcher.Dispatch(oscIn, '/foo', 5)
		mockUpdateHandler1.assert_called_once_with('/foo', 5)
		mockUpdateHandler2.assert_called_once_with('/foo', 5)

		mockTarget3 = MockOP('/mock_target_3')
		mockUpdateHandler3 = MagicMock()
		dispatcher.MapControl(mockTarget3, '/foo', mockUpdateHandler3)
		# ensure we immediately call handlers when we have a tracked value
		mockUpdateHandler3.assert_called_once_with('/foo', 5)
		# ensure we're not requesting values when we already have them
		assert mockCatchAllHandler.call_count == 1

		# don't bother calling handlers for unchanged values
		dispatcher.Dispatch(mockTarget1, '/foo', 5)
		assert mockUpdateHandler1.call_count == 1
		assert mockUpdateHandler2.call_count == 1
		assert mockUpdateHandler3.call_count == 1

		# Sanity check that dispatching works as expected
		dispatcher.Dispatch(mockTarget1, '/foo', 6)
		mockUpdateHandler0.assert_called_with('/foo', 6)
		assert mockUpdateHandler1.call_count == 1
		mockUpdateHandler2.assert_called_with('/foo', 6)
		mockUpdateHandler3.assert_called_with('/foo', 6)
		mockCatchAllHandler.assert_called_with('/foo', 6)

	def test_MapControl_promotionToTracked(
		self, dispatcher: OSCDispatcher, oscIn: MockOscinDAT
	):
		# a "non control" target creates initial mapping
		mockTarget0 = MockOP('/mock_target_0')
		mockUpdateHandler0 = MagicMock()
		dispatcher.Map(mockTarget0, '/foo', mockUpdateHandler0)

		# a "control" target should "promote" the mapping to a tracked one
		mockTarget1 = MockOP('/mock_target_1')
		mockUpdateHandler1 = MagicMock()
		dispatcher.MapControl(mockTarget1, '/foo', mockUpdateHandler1)

		# Simulate receiving the same response value twice
		dispatcher.Dispatch(oscIn, '/foo', 5)
		dispatcher.Dispatch(oscIn, '/foo', 5)

		# ensure that the handler is being tracked and ignores the second request
		assert mockUpdateHandler1.call_count == 1

	def test_Map_cleanupReferences(
		self, dispatcher: OSCDispatcher, oscIn: MockOscinDAT,
		caplog: pytest.LogCaptureFixture
	):
		# caplog.set_level(logging.DEBUG)
		mockOp = MockOP()
		mockOp.aCallback = MagicMock()

		dispatcher.Map(mockOp, '/foo', mockOp.aCallback)
		dispatcher.Dispatch(oscIn, '/foo', 123)

		mockOp.aCallback.assert_called_once()

		del mockOp
		gc.collect()

		dispatcher.Dispatch(oscIn, '/foo', 456)
		assert 'unmatched OSC address /foo' in caplog.text

	# TODO: watch https://www.youtube.com/watch?v=kEQAsx6Ar_8 -- did we do all this for nothing?
	# TODO: error if mapping control using wildcard
	# TODO: if source is a control and pickup enabled, ignore value unless
	# 		in sync or it has "crossed the current value"
	# TODO: dispatching more than one value when there is a TrackedAddress should error
	#          - or maybe just warn that only the first value will be tracked?
	# TODO: dispatching no values when there is a TrackedAddress should error
