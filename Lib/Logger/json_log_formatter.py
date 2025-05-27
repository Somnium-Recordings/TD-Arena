import logging
import traceback
from typing import Optional

from pythonjsonlogger.orjson import OrjsonFormatter

from .logger_utils import normalizeSourcePath


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

		if not hasattr(record, 'absframe'):
			log_record['absframe'] = absTime.frame

		component: Optional[OP] = getattr(record, 'component', None)

		if not hasattr(record, 'source'):
			log_record['source'] = normalizeSourcePath(
				component.path if component else f'/{record.name.replace(".", "/")}'
			)

		if not isinstance(log_record['source'], str):
			log_record['source'] = normalizeSourcePath(str(log_record['source']))

		if not hasattr(record, 'type'):
			log_record['type'] = component.type if component else 'UNKNOWN'

		if not hasattr(record, 'frame'):
			log_record['frame'] = component.time.frame if component else me.time.frame

		if (
			hasattr(record, 'exc_info') and record.exc_info is not None
			and not isinstance(record.exc_info, str)
		):
			log_record['exc_info'] = ''.join(
				traceback.format_exception(*record.exc_info)
			)
