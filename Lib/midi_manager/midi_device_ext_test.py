import pytest

from .midi_device_ext import MappableControl, MidiMap, toMidiAddress


def test_toMidiAddress():
	testControl = MappableControl(name='testControl', address='/foo')

	assert toMidiAddress(
		MidiMap(control=testControl, channel=2, note=9)
	) == 'ch2n9'

	assert toMidiAddress(
		MidiMap(control=testControl, channel=4, index=6)
	) == 'ch4ctrl6'

	with pytest.raises(NotImplementedError):
		toMidiAddress(MidiMap(control=testControl, channel=3))
