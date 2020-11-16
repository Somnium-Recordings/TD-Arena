import pytest

from tdaUtils import (addressToValueLocation, getDeckID, getLayerID, intIfSet,
                      mapAddressToClipLocation, parameterPathToAddress)


def test_intIfSet():
	assert intIfSet('4') == 4
	assert intIfSet('') is None
	assert intIfSet(0) == 0


def test_mapAddressToClipLocation():
	assert mapAddressToClipLocation('/composition/layers/5/clips/4') == (5, 4)
	assert mapAddressToClipLocation('/composition/layers/5/clips/4/bar') == (5, 4)
	with pytest.raises(AssertionError):
		mapAddressToClipLocation('/foo')


def test_getLayerID():
	assert getLayerID('/composition/layers/5/clips/4') == 5
	assert getLayerID('/composition/layers/6') == 6
	with pytest.raises(AssertionError):
		getLayerID('/foo')


def test_getDeckID():
	assert getDeckID('/composition/decks/5') == 5
	assert getDeckID('/composition/decks/6/connect') == 6
	with pytest.raises(AssertionError):
		getDeckID('/foo')


def test_addressToValueLocation():
	# yapf: disable
	assert addressToValueLocation(
		'/composition/layers/5/Opacity', '/composition'
	) == ('/composition/layers/layer5', 'Opacity')

	assert addressToValueLocation(
		'/composition/clips/5/Active', '/tdArena/render/composition'
	) == ('/tdArena/render/composition/clips/clip5', 'Active')
	assert addressToValueLocation(
		'/composition/decks/1/Deckname', '/tdArena/render/composition'
	) == ('/tdArena/render/composition/decks/deck1', 'Deckname')
	# yapf: enable


def test_parameterPathToAddress():
	assert parameterPathToAddress(
		'/tdArena/render/composition/decks/deck0', 'foo'
	) == '/composition/decks/0/foo'
	assert parameterPathToAddress(
		'/render/composition/decks/deck0', 'foo'
	) == '/composition/decks/0/foo'
