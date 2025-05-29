import pytest
from opentelemetry import trace
from opentelemetry.trace import StatusCode

from .context import get_current_span, set_span_attribute, trace_context


def get_inmemory_exporter():
	return trace.get_tracer_provider(
	)._test_exporter  # type: ignore[attr-defined]


@pytest.fixture(autouse=True)
def clear_exporter():
	exporter = get_inmemory_exporter()
	exporter.clear()
	yield


def test_trace_context_basic():
	with trace_context("test_span") as span:
		assert span is not None
		assert span.is_recording()
	spans = get_inmemory_exporter().get_finished_spans()
	assert len(spans) == 1
	span = spans[0]
	assert span.name == "test_span"
	assert span.status.status_code == StatusCode.OK


def test_trace_context_with_attributes():
	with trace_context(
		"test_span", attributes={"test_key": "test_value"}
	) as span:
		assert span.is_recording()
	spans = get_inmemory_exporter().get_finished_spans()
	assert len(spans) == 1
	span = spans[0]
	assert span.name == "test_span"
	assert span.status.status_code == StatusCode.OK
	assert span.attributes is not None
	assert span.attributes.get("test_key") == "test_value"


def test_trace_context_with_error():
	with pytest.raises(ValueError):
		with trace_context("test_span") as span:
			raise ValueError("test error")
	spans = get_inmemory_exporter().get_finished_spans()
	assert len(spans) == 1
	span = spans[0]
	assert span.name == "test_span"
	assert span.status.status_code == StatusCode.ERROR


def test_set_span_attribute():
	with trace_context("test_span") as span:
		set_span_attribute("test_key", "test_value")
		assert span.is_recording()
	spans = get_inmemory_exporter().get_finished_spans()
	assert len(spans) == 1
	span = spans[0]
	assert span.name == "test_span"
	assert span.status.status_code == StatusCode.OK
	assert span.attributes is not None
	assert span.attributes.get("test_key") == "test_value"
