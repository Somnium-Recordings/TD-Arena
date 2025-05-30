"""OpenTelemetry configuration for TD-Arena."""

import logging
from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.semconv.resource import ResourceAttributes

from .verify_tracing import sendTestTraces

logger = logging.getLogger(__name__)

_initialized = False


def initialize_telemetry(
	*,
	service_name: str = 'td-arena',
	endpoint: str = 'http://localhost:4317',
	log_level: Optional[str] = None,
	log_to_console: bool = False,
) -> None:
	"""
    Initialize OpenTelemetry tracing. Can only be called once per process.
    Raises RuntimeError if called more than once.

    Args:
        service_name: Name of the service for tracing
        endpoint: OTLP endpoint for trace export
        log_level: Optional log level override
        log_to_console: If True, also log spans to the console
    """
	global _initialized  # noqa: PLW0603
	if _initialized:
		raise RuntimeError(
			'OpenTelemetry has already been initialized in this process. Only one initialization is allowed.'
		)

	if log_level:
		logging.getLogger(__name__).setLevel(log_level)

	# Create a resource with service information
	resource = Resource.create(
		{
			ResourceAttributes.SERVICE_NAME: service_name,
			ResourceAttributes.SERVICE_VERSION: '0.1.0',
		}
	)

	# Create and set the tracer provider
	provider = TracerProvider(resource=resource)
	trace.set_tracer_provider(provider)

	# Create and add the OTLP exporter
	exporter = OTLPSpanExporter(endpoint=endpoint)
	provider.add_span_processor(BatchSpanProcessor(exporter))

	# Optionally add the console exporter
	if log_to_console:
		provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

	logger.info(
		'OpenTelemetry initialized with service name: %s, endpoint: %s',
		service_name,
		endpoint,
	)
	_initialized = True


def bootstrap():
	debug('bootstrapping telemetry')
	initialize_telemetry(log_to_console=True)
	# TODO: create initial span to track application startup
	sendTestTraces()
