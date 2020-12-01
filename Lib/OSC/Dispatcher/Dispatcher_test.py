# pylint: disable=no-self-use
from unittest.mock import MagicMock

import pytest

from OSC.Dispatcher.Dispatcher import OSCDispatcher


class TestDispatcher():
	@pytest.fixture
	def oscIn(self):
		return MagicMock()

	@pytest.fixture
	def ownerComponent(self, oscIn):
		comp = MagicMock()

		op = lambda path: oscIn if path == './oscin1' else None
		comp.op.side_effect = op

		return comp

	@pytest.fixture
	def dispatcher(self, ownerComponent):
		return OSCDispatcher(
			ownerComponent, MagicMock(), MagicMock(), MagicMock(), MagicMock(),
			MagicMock(), MagicMock(), MagicMock()
		)

	def test_Map(self, dispatcher):
		handler = MagicMock()
		dispatcher.Map('/foo', {'handler': handler})
		dispatcher.Dispatch('/foo')
		handler.assert_called_with('/foo')

	def test_MapMultiple(self, dispatcher):
		fooHandler = MagicMock()
		barHandler = MagicMock()
		mappedHandler = MagicMock()
		currentValueHandler = MagicMock()

		dispatcher.MapMultiple(
			{
				'?': {
					'handler': currentValueHandler
				},
				'/foo': {
					'handler': fooHandler,
					'sendAddress': False
				},
				'/bar': {
					'handler': barHandler
				},
				'/mappedAddress': {
					'handler': mappedHandler,
					'mapAddress': lambda address: 'mapped-address'
				}
			}
		)

		dispatcher.Dispatch('/bar', 'arg1', 'arg2')
		barHandler.assert_called_with('/bar', 'arg1', 'arg2')
		fooHandler.assert_not_called()

		dispatcher.Dispatch('/foo', 'arg1')
		fooHandler.assert_called_with('arg1')

		dispatcher.Dispatch('/mappedAddress')
		mappedHandler.assert_called_with('mapped-address')

		dispatcher.Dispatch('/foo', '?')
		fooHandler.assert_called_once()  # should not have been called again
		currentValueHandler.assert_called_with('/foo', '?')

	def test_Reply(self, dispatcher, oscIn):
		dispatcher.Reply('/foo/bar', 123)
		oscIn.sendOSC.assert_called_with('/foo/bar', (123, ))
