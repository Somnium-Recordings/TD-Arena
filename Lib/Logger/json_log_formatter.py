import logging
from typing import Any, Callable, Optional

import orjson
from pythonjsonlogger import jsonlogger


def serializeJson(
	obj: Any,  # noqa: ANN401
	default: Optional[Callable[[Any], Any]],
	cls: Any,  # noqa: ARG001, ANN401
	indent: Any,  # noqa: ARG001, ANN401
	ensure_ascii: Any  # noqa: ARG001, ANN401
):
	"""
	Provide compatibility between the expected call signature of
	json.dumps() and orjson.dumps()
	"""
	return orjson.dumps(obj, default).decode('utf-8')  # pylint: disable=no-member


class TdContextJsonFormatter(jsonlogger.JsonFormatter):

	def __init__(self, *args, **kwargs):  # noqa: ANN002, ANN003
		super().__init__(*args, **kwargs, json_serializer=serializeJson)

	def parse(self) -> list[str]:
		return [
			'message',
			'asctime',
			'absframe',
			'frame',
			'source',
			'levelname',
			'levelno',
			'type',
			# TODO: see if we can add these through the logging_mixins
			'module',
			'filename',
			'lineno',
			'funcName',
			'exc_info',
			'exc_text',
			'stack_info',
		]

	def add_fields(
		self, log_record: dict[str, Any], record: logging.LogRecord,
		message_dict: dict[str, Any]
	) -> None:
		super().add_fields(log_record, record, message_dict)

		log_record['absframe'] = absTime.frame
		log_record['source'] = f'/{record.name.replace(".", "/")}'

		component = log_record.get('component', None)
		if component:
			log_record['type'] = component.type
			log_record['frame'] = component.time.frame
			del log_record['component']
		else:
			log_record['type'] = 'UNKNOWN'
			log_record['frame'] = me.time.frame
