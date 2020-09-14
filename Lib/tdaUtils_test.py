import pytest

from tdaUtils import (addressToValueLocation, getLayerId, intIfSet,
                      mapAddressToClipLocation)


def test_intIfSet():
	assert intIfSet('4') == 4
	assert intIfSet('') is None


def test_mapAddressToClipLocation():
	assert mapAddressToClipLocation('/composition/layers/5/clips/4') == (5, 4)
	assert mapAddressToClipLocation('/composition/layers/5/clips/4/bar') == (5, 4)
	with pytest.raises(AssertionError):
		mapAddressToClipLocation('/foo')


def test_getLayerId():
	assert getLayerId('/composition/layers/5/clips/4') == 5
	assert getLayerId('/composition/layers/6') == 6
	with pytest.raises(AssertionError):
		getLayerId('/foo')


def test_addressToValueLocation():
	# yapf: disable
	assert addressToValueLocation(
		'/composition/layers/5/Opacity', '/composition'
	) == ('/composition/layers/layer5', 'Opacity')

	assert addressToValueLocation(
		'/composition/clips/5/Active', '/tdArena/render/composition'
	) == ('/tdArena/render/composition/clips/clip5', 'Active')
	# yapf: enable
