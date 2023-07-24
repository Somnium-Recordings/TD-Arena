from unittest.mock import MagicMock

import pytest
from oscDispatcher import OSCDispatcher


class TestDispatcher():

	@pytest.fixture()
	def dispatcher(self, ownerComponent):  # noqa: ANN001
		return OSCDispatcher(
			ownerComponent,
			MagicMock()  # logger
		)

	def test_Map(self, dispatcher):  # noqa: ANN001
		handler = MagicMock()
		dispatcher.Map('/foo', {'handler': handler})
		dispatcher.Dispatch('/foo')
		handler.assert_called_with('/foo')

	def test_MapMultiple(self, dispatcher):  # noqa: ANN001
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
					'mapAddress': lambda address: 'mapped-address'  # noqa: ARG005
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
