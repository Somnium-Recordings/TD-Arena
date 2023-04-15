import pytest
from tdaUtils import (
	addressToToxPath,
	addressToValueLocation,
	exportToAddress,
	filePathToName,
	getClipID,
	getDeckID,
	getLayerID,
	intIfSet,
	mapAddressToDeckLocation,
	mapAddressToEffectContainer,
	mapAddressToEffectLocation,
	parameterPathToAddress,
)


def test_intIfSet():
	assert intIfSet('4') == 4
	assert intIfSet('') is None
	assert intIfSet(0) == 0


def test_mapAddressToDeckLocation():
	# yapf: disable
	assert mapAddressToDeckLocation('/selecteddeck/layers/5/clips/4') == (5, 4)
	assert mapAddressToDeckLocation('/selecteddeck/layers/5/clips/4/bar') == (5, 4)
	with pytest.raises(AssertionError):
		mapAddressToDeckLocation('/foo')
	# yapf: enable


def test_mapAddressToEffectLocation():
	location = mapAddressToEffectLocation('/composition/clips/4/video/effects/5')
	assert location.containerAddress == '/composition/clips/4/video/effects'
	assert location.effectID == 5

	location2 = mapAddressToEffectLocation(
		'/composition/clips/4/video/effects/1/clear'
	)
	assert location2.containerAddress == '/composition/clips/4/video/effects'
	assert location2.effectID == 1

	with pytest.raises(AssertionError):
		mapAddressToEffectLocation('/foo')


def test_mapAddressToEffectContainer():
	assert mapAddressToEffectContainer(
		'/composition/clips/4/video/effects/5'
	) == '/composition/clips/4/video/effects'

	assert mapAddressToEffectContainer(
		'/composition/clips/4/video/effects/5/move'
	) == '/composition/clips/4/video/effects'

	assert mapAddressToEffectContainer(
		'/composition/clips/4/video/effects/add'
	) == '/composition/clips/4/video/effects'

	assert mapAddressToEffectContainer(
		'/composition/clips/4/video/effects'
	) == '/composition/clips/4/video/effects'

	with pytest.raises(AssertionError):
		mapAddressToEffectContainer('/foo')


def test_getLayerID():
	assert getLayerID('/composition/layers/5/clear') == 5
	assert getLayerID('/composition/layers/5/clips/4') == 5
	assert getLayerID('/composition/layers/6') == 6
	assert getLayerID('/selecteddeck/layers/9/insert') == 9
	with pytest.raises(AssertionError):
		getLayerID('/foo')


def test_getClipID():
	assert getClipID('/composition/clips/4') == 4
	assert getClipID('/composition/clips/6/source/foo') == 6
	with pytest.raises(AssertionError):
		getClipID('/foo')


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
		'/composition/clips/5/video/effects/4/tox/Sectionopacity', '/tdArena/render/composition'
	) == ('/tdArena/render/composition/clips/clip5/video/effects/effect4/tox', 'Sectionopacity')
	assert addressToValueLocation(
		'/composition/decks/1/Deckname', '/tdArena/render/composition'
	) == ('/tdArena/render/composition/decks/deck1', 'Deckname')
	# yapf: enable


def test_addressToToxPath():
	assert addressToToxPath(
		'/composition/clips/5/video/effects/4', '/tdArena/render/composition'
	) == '/tdArena/render/composition/clips/clip5/video/effects/effect4/tox'
	assert addressToToxPath(
		'/composition/clips/28/video/source/tox', '/tdArena/render/composition'
	) == '/tdArena/render/composition/clips/clip28/video/source/tox'


def test_exportToAddress():
	# yapf: disable
	assert exportToAddress(
		'clips/clip5/video/source/tox:Sectionopacity'
	) == ('/composition/clips/5/video/source/tox/Sectionopacity')
	assert exportToAddress(
		'clips/clip5/video/effects/effect4/tox:Sectionorder'
	) == ('/composition/clips/5/video/effects/4/tox/Sectionorder')
	assert exportToAddress(
		'layers/clip5/video/source/tox:Sectionopacity'
	) == ('/composition/layers/5/video/source/tox/Sectionopacity')
	assert exportToAddress(
		'layers/clip5/video/effects/effect4/tox:Sectionorder'
	) == ('/composition/layers/5/video/effects/4/tox/Sectionorder')
	# yapf: enable


def test_parameterPathToAddress():
	assert parameterPathToAddress(
		'/tdArena/render/composition/decks/deck0', 'foo'
	) == '/composition/decks/0:foo'
	assert parameterPathToAddress(
		'/render/composition/decks/deck0', 'foo'
	) == '/composition/decks/0:foo'
	assert parameterPathToAddress(
		'/render/composition/clips/clip14', 'foo'
	) == '/composition/clips/14:foo'
	assert parameterPathToAddress(
		'/render/composition/clips/clip4/video/effects/effect0/tox', 'foo'
	) == '/composition/clips/4/video/effects/0/tox:foo'


def test_filePathToName():
	assert filePathToName('C:\\my\\file.txt') == 'File'
	assert filePathToName('/my/file.txt') == 'File'
	assert filePathToName('file.txt') == 'File'
	assert filePathToName('file') == 'File'
	assert filePathToName('/my/multi-Word-file') == 'Multi Word File'
	assert filePathToName('/my/multi_word_File') == 'Multi Word File'
	assert filePathToName('/my/multiWordFile') == 'Multi Word File'
