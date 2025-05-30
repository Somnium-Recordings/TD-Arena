import logging

from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

from .log_filter import TdContextOTELFilter
from .otel_resource import tda_resource

logger = logging.getLogger(__name__)


def create_otel_log_handler(
	*,
	resource: Resource = tda_resource,
	endpoint: str = 'localhost:4317',
	log_level: int = logging.DEBUG,
):
	"""Configure OpenTelemetry logging to send to Alloy."""

	# Setup log exporter pointing to Alloy
	log_exporter = OTLPLogExporter(
		endpoint=endpoint,
		insecure=True,
		timeout=1,
	)

	# Create logger provider
	logger_provider = LoggerProvider(resource=resource)
	set_logger_provider(logger_provider)

	# Add batch processor for performance
	logger_provider.add_log_record_processor(
		BatchLogRecordProcessor(
			log_exporter,
			max_queue_size=2048,
			max_export_batch_size=512,
			schedule_delay_millis=1000,  # Export every second
		)
	)

	# Create handler for Python logging integration
	handler = LoggingHandler(level=log_level, logger_provider=logger_provider)

	handler.addFilter(TdContextOTELFilter())

	return handler


def register_otel_log_handler(
	*,
	endpoint: str = 'localhost:4317',
	log_level: int = logging.DEBUG,
):
	debug('registering OTEL log handler')
	root_logger = logging.getLogger()
	root_logger.addHandler(
		create_otel_log_handler(endpoint=endpoint, log_level=log_level)
	)
	root_logger.setLevel(log_level)

	logger.info(
		'OTEL Log Handler registered for service: %s, endpoint: %s',
		tda_resource.attributes[ResourceAttributes.SERVICE_NAME],
		endpoint,
	)
