from collections.abc import Generator
from contextlib import contextmanager
from typing import Optional, Union

from opentelemetry import trace
from opentelemetry.trace import Span, Status, StatusCode


@contextmanager
def trace_context(
	name: str,
	attributes: Optional[dict] = None,
	kind: trace.SpanKind = trace.SpanKind.INTERNAL
) -> Generator[Span, None, None]:
	"""
    Context manager for creating and managing spans.

    Args:
        name: Name of the span
        attributes: Optional dictionary of attributes to add to the span
        kind: Span kind (defaults to INTERNAL)

    Yields:
        The created span
    """
	tracer = trace.get_tracer(__name__)
	with tracer.start_as_current_span(
		name, kind=kind, attributes=attributes or {}
	) as span:
		try:
			yield span
			span.set_status(Status(StatusCode.OK))
		except Exception as e:
			span.set_status(Status(StatusCode.ERROR, str(e)))
			span.record_exception(e)
			raise


def get_current_span() -> Optional[Span]:
	"""
    Get the current active span.

    Returns:
        The current span or None if no span is active
    """
	return trace.get_current_span()


def set_span_attribute(key: str, value: Union[str, int, float, bool]) -> None:
	"""
    Set an attribute on the current span.

    Args:
        key: Attribute key
        value: Attribute value
    """
	span = get_current_span()
	if span:
		span.set_attribute(key, value)
