# pylint: disable=redefined-outer-name
import builtins
from unittest.mock import MagicMock

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from tdaTesting import MockOP, MockOPFinder

# Globals that TD creates that crash our tests when not present
builtins.midioutCHOP = MagicMock()  # type: ignore
builtins.OP = MagicMock()  # type: ignore
builtins.oscinDAT = MagicMock()  # type: ignore
builtins.debug = print  # type: ignore


@pytest.fixture(scope="session", autouse=True)
def setup_tracer_provider():
	exporter = InMemorySpanExporter()
	provider = TracerProvider()
	processor = SimpleSpanProcessor(exporter)
	provider.add_span_processor(processor)
	provider._test_exporter = exporter
	trace.set_tracer_provider(provider)


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
