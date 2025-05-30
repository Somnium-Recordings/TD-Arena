import logging

from .global_exception_handler import register_global_exception_handler
from .otel_log_handler import register_otel_log_handler
from .setup_tracing import initialize_tracing
from .verify_tracing import sendTestTraces


def bootstrap():
	debug('bootstrapping telemetry')

	register_otel_log_handler()
	register_global_exception_handler()
	initialize_tracing(log_to_console=True)

	sendTestTraces()
	# TODO: create initial span to track application startup

	logger = logging.getLogger(__name__)
	logger.info('telemetry bootstrapped')
