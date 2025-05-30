import logging
import time

from .context import trace_context
from .otel_decorators import trace_span


def sendTestTraces():
	logging.info('[verify_tracing] Telemetry initialized.')

	# Use context manager for tracing
	with trace_context(
		'verify_context_span', attributes={'test': 'context'}
	) as span:
		ctx = span.get_span_context()
		logging.info(
			'[verify_tracing] In context span: span_id=%s, trace_id=%s, is_recording=%s',
			ctx.span_id, ctx.trace_id, span.is_recording()
		)
		time.sleep(0.1)

	# Use decorator for tracing
	@trace_span(attributes={'test': 'decorator'})
	def traced_function(x: int, y: int) -> int:
		logging.info('[verify_tracing] In decorated function: x=%s, y=%s', x, y)
		time.sleep(0.1)
		return x + y

	result = traced_function(2, 3)
	logging.info('[verify_tracing] Decorated function result: %s', result)

	logging.info(
		'[verify_tracing] Tracing verification complete. Check your OpenTelemetry backend for spans.'
	)
