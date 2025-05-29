import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import StatusCode

from .context import set_span_attribute, trace_context
from .otel_decorators import trace_span

# Set up a test tracer provider and memory exporter
exporter = InMemorySpanExporter()
provider = TracerProvider()
processor = SimpleSpanProcessor(exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)


@pytest.fixture(autouse=True)
def _clear_exporter() -> None:
	exporter.clear()


def test_trace_context_basic():
	with trace_context('test_span') as span:
		assert span is not None
		assert span.is_recording()
	spans = exporter.get_finished_spans()
	assert len(spans) == 1
	span = spans[0]
	assert span.name == 'test_span'
	assert span.status.status_code == StatusCode.OK


def test_trace_context_with_attributes():
	with trace_context(
		'test_span', attributes={'test_key': 'test_value'}
	) as span:
		assert span.is_recording()
	spans = exporter.get_finished_spans()
	assert len(spans) == 1
	span = spans[0]
	assert span.name == 'test_span'
	assert span.status.status_code == StatusCode.OK
	assert span.attributes is not None
	assert span.attributes.get('test_key') == 'test_value'


def test_trace_context_with_error():
	with pytest.raises(ValueError,
																				match='test error'), trace_context('test_span') as span:
		raise ValueError('test error')
	spans = exporter.get_finished_spans()
	assert len(spans) == 1
	span = spans[0]
	assert span.name == 'test_span'
	assert span.status.status_code == StatusCode.ERROR


def test_set_span_attribute():
	with trace_context('test_span') as span:
		set_span_attribute('test_key', 'test_value')
		assert span.is_recording()
	spans = exporter.get_finished_spans()
	assert len(spans) == 1
	span = spans[0]
	assert span.name == 'test_span'
	assert span.status.status_code == StatusCode.OK
	assert span.attributes is not None
	assert span.attributes.get('test_key') == 'test_value'


def test_trace_span_basic():

	@trace_span()
	def test_func() -> str:
		return 'test'

	result = test_func()
	assert result == 'test'

	spans = exporter.get_finished_spans()
	assert len(spans) == 1
	span = spans[0]
	assert span.name == 'test_func'
	assert span.status.status_code == StatusCode.OK


def test_trace_span_with_attributes():

	@trace_span(attributes={'test_key': 'test_value'})
	def test_func() -> str:
		return 'test'

	result = test_func()
	assert result == 'test'

	spans = exporter.get_finished_spans()
	assert len(spans) == 1
	span = spans[0]
	assert span.name == 'test_func'
	assert span.status.status_code == StatusCode.OK
	assert span.attributes is not None
	assert span.attributes.get('test_key') == 'test_value'


def test_trace_span_with_error():

	@trace_span()
	def test_func() -> None:
		raise ValueError('test error')

	with pytest.raises(ValueError, match='test error'):
		test_func()

	spans = exporter.get_finished_spans()
	assert len(spans) == 1
	span = spans[0]
	assert span.name == 'test_func'
	assert span.status.status_code == StatusCode.ERROR
