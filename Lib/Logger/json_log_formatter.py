import logging
import traceback
from typing import Optional

from opentelemetry import trace
from pythonjsonlogger.orjson import OrjsonFormatter


class TdContextJsonFormatter(OrjsonFormatter):

	def __init__(self):
		super().__init__(
			# fmt=
			style='{',
			reserved_attrs=[
				'component', 'args', 'created', 'relativeCreated', 'thread', 'threadName',
				'processName', 'process', 'msg', 'msecs'
			],
			timestamp=True,
		)

	def add_fields(
		self, log_record: dict, record: logging.LogRecord, message_dict: dict
	) -> None:
		super().add_fields(log_record, record, message_dict)

		component: Optional[OP] = getattr(record, 'component', None)

		if not hasattr(record, 'source'):
			log_record['source'] = component.path if component else record.name

		if not isinstance(log_record['source'], str):
			log_record['source'] = str(log_record['source'])

		if not hasattr(record, 'type'):
			log_record['type'] = component.type if component else 'UNKNOWN'

		if not hasattr(record, 'frame') and component:
			log_record['frame'] = component.time.frame

		# only access absFrame when we know we have a component, without this check
		# the error logger gets into a weird infinite loop on startup that I haven't
		# been able to track down
		if not hasattr(record, 'absframe') and component:
			log_record['absframe'] = getattr(absTime, 'frame', 0)

		if (
			hasattr(record, 'exc_info') and record.exc_info is not None
			and not isinstance(record.exc_info, str)
		):
			log_record['exc_info'] = ''.join(
				traceback.format_exception(*record.exc_info)
			)

		# Inject OpenTelemetry trace context if available
		span = trace.get_current_span()
		if span is not None and hasattr(span, 'get_span_context'):
			ctx = span.get_span_context()
			if ctx is not None:
				log_record['trace_id'] = (
					format(ctx.trace_id, '032x') if hasattr(ctx, 'trace_id') else None
				)
				log_record['span_id'] = (
					format(ctx.span_id, '016x') if hasattr(ctx, 'span_id') else None
				)
