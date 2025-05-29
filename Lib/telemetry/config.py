"""OpenTelemetry configuration for TD-Arena."""

import logging
from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes

logger = logging.getLogger(__name__)


def initialize_telemetry(
	service_name: str = 'td-arena',
	endpoint: str = 'http://localhost:4317',
	log_level: Optional[str] = None,
) -> None:
	"""Initialize OpenTelemetry tracing.

    Args:
        service_name: Name of the service for tracing
        endpoint: OTLP endpoint for trace export
        log_level: Optional log level override
    """
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

	logger.info(
		'OpenTelemetry initialized with service name: %s, endpoint: %s',
		service_name,
		endpoint,
	)
