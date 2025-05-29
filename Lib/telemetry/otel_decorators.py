import logging
from functools import wraps
from typing import Any, Callable, Optional

from opentelemetry import trace
from opentelemetry.trace import Span, Status, StatusCode


def trace_span(
	name: Optional[str] = None,
	attributes: Optional[dict] = None,
	kind: trace.SpanKind = trace.SpanKind.INTERNAL
) -> Callable:
	"""
    Decorator that creates a span for the decorated function.
    
    Args:
        name: Optional name for the span. If not provided, uses the function name.
        attributes: Optional dictionary of attributes to add to the span.
        kind: Optional span kind (defaults to INTERNAL)
    
    Returns:
        Decorated function that creates a span for its execution.
    """

	def decorator(func: Callable) -> Callable:

		@wraps(func)
		def wrapper(*args: Any, **kwargs: Any) -> Any:
			tracer = trace.get_tracer(__name__)
			span_name = name or func.__name__

			with tracer.start_as_current_span(
				span_name, kind=kind, attributes=attributes or {}
			) as span:
				try:
					result = func(*args, **kwargs)
					span.set_status(Status(StatusCode.OK))
					return result
				except Exception as e:
					span.set_status(Status(StatusCode.ERROR, str(e)))
					span.record_exception(e)
					raise

		return wrapper

	return decorator
