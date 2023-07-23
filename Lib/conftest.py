# pylint: disable=redefined-outer-name
import builtins
from unittest.mock import MagicMock

import pytest
from tdaTesting import MockOP, MockOPFinder

# Globals that TD creates that crash our tests when not present
builtins.midioutCHOP = MagicMock()  # type: ignore
builtins.OP = MagicMock()  # type: ignore
builtins.oscinDAT = MagicMock()  # type: ignore
builtins.debug = print  # type: ignore


@pytest.fixture()
def uiThemeSectionTemplate():
	return MagicMock()


@pytest.fixture()
def uiTheme(uiThemeSectionTemplate):  # noqa: ANN001
	uiTheme = MockOP('/uitheme')
	uiTheme.op.addPath('sectionTemplate', uiThemeSectionTemplate)

	return uiTheme


@pytest.fixture()
def op(uiTheme):  # noqa: ANN001
	op = MockOPFinder()
	op.uiTheme = uiTheme

	return op


@pytest.fixture()
def logger():
	return MagicMock()


@pytest.fixture()
def ownerComponent(op: MockOPFinder):
	return MockOP(path='/test/ownerComponent/path', op=op)
