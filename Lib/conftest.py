from unittest.mock import MagicMock

import pytest

from tdaTesting import mockOp


@pytest.fixture
def op():
	return mockOp()


@pytest.fixture
def logger():
	return MagicMock()


@pytest.fixture
def ownerComponent():
	comp = MagicMock()

	comp.op = mockOp()

	return comp
