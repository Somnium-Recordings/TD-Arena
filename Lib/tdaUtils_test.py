from tdaUtils import intIfSet


def test_intIfSet():
	assert intIfSet('4') == 4
	assert intIfSet('') == ''
