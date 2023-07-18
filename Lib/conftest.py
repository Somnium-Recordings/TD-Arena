# pylint: disable=redefined-outer-name
import builtins
from unittest.mock import MagicMock

import pytest
from tdaTesting import MockOP

# Globals that TD creates that crash our tests when not present
builtins.midioutCHOP = MagicMock()  # type: ignore
builtins.OP = MagicMock()  # type: ignore


@pytest.fixture()
def uiThemeSectionTemplate():
	return MagicMock()


@pytest.fixture()
def uiTheme(uiThemeSectionTemplate):  # noqa: ANN001
	uiTheme = MagicMock()
	uiTheme.op = MockOP()
	uiTheme.op.addPath('sectionTemplate', uiThemeSectionTemplate)

	return uiTheme


@pytest.fixture()
def op(uiTheme):  # noqa: ANN001
	op = MockOP()
	op.uiTheme = uiTheme

	return op


@pytest.fixture()
def logger():
	return MagicMock()


@pytest.fixture()
def ownerComponent():
	comp = MagicMock()

	comp.op = MockOP()
	comp.path = '/test/component/path'

	return comp
