import logging

from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource

from .log_filter import TdContextOTELFilter


def create_otel_log_handler(
	service_name: str = "tda-app",
	alloy_endpoint: str = "localhost:4317",
	log_level: int = logging.DEBUG,
):
	"""Configure OpenTelemetry logging to send to Alloy."""

	# Create resource with service info
	resource = Resource.create(
		{
			"service.name": service_name,
			"service.version": "1.0.0",  # Update as needed
		}
	)

	# Setup log exporter pointing to Alloy
	log_exporter = OTLPLogExporter(
		endpoint=alloy_endpoint,
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


def register_otel_log_handler(log_level: int = logging.DEBUG):
	root_logger = logging.getLogger()
	root_logger.addHandler(create_otel_log_handler())
	root_logger.setLevel(log_level)
