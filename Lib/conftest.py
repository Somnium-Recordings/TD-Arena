# pylint: disable=redefined-outer-name
from unittest.mock import MagicMock

import pytest

from tdaTesting import MockOP


@pytest.fixture
def uiThemeSectionTemplate():
	return MagicMock()


@pytest.fixture
def uiTheme(uiThemeSectionTemplate):
	uiTheme = MagicMock()
	uiTheme.op = MockOP()
	uiTheme.op.addPath('sectionTemplate', uiThemeSectionTemplate)

	return uiTheme


@pytest.fixture
def op(uiTheme):
	op = MockOP()
	op.uiTheme = uiTheme

	return op


@pytest.fixture
def logger():
	return MagicMock()


@pytest.fixture
def ownerComponent():
	comp = MagicMock()

	comp.op = MockOP()

	return comp
