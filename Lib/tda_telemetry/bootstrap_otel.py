import logging

from .global_exception_handler import register_global_exception_handler
from .otel_log_handler import register_otel_log_handler
from .setup_tracing import initialize_tracing

logger = logging.getLogger(__name__)

def bootstrap():
	debug('bootstrapping telemetry, check grafana for logs')

	register_otel_log_handler()
	register_global_exception_handler()
	initialize_tracing(log_to_console=True)

	logger.debug('telemetry bootstrapped')
