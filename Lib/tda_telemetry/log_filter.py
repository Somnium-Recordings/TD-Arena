import logging
import traceback
from typing import Any, Optional, cast


class TdContextOTELFilter(logging.Filter):
	"""
    Filter that adds custom TDA context to log records.
    """

	def filter(self, record: logging.LogRecord) -> bool:
		component: Optional[OP] = getattr(record, 'component', None)

		# Add source field
		if not hasattr(record, 'source'):
			record.source = component.path if component else record.name

		if not isinstance(cast(Any, record).source, str):
			cast(Any, record).source = str(cast(Any, record).source)

		# Add type field
		if not hasattr(record, 'type'):
			record.type = component.type if component else 'UNKNOWN'

		# Add frame field
		if not hasattr(record, 'frame') and component:
			record.frame = component.time.frame

		# only access absFrame when we know we have a component, without this check
		# the error logger gets into a weird infinite loop on startup that I haven't
		# been able to track down
		if not hasattr(record, 'absframe') and component:
			record.absframe = getattr(absTime, 'frame', 0)

		return True
