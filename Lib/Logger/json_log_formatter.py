#
# Leaving commented out because the orjson dependency blows
# up our logic that ensures loggers are setup on start
#
# import logging
# from typing import Any, Callable, Optional

# import orjson
# from pythonjsonlogger import jsonlogger

# def serializeJson(
# 	obj: Any,
# 	default: Optional[Callable[[Any], Any]],
# 	cls: Any,
# 	indent: Any,
# 	ensure_ascii: Any
# ):
# 	"""
# 	Provide compatibility between the expected call signature of
# 	json.dumps() and orjson.dumps()
# 	"""
# 	return orjson.dumps(obj, default).decode('utf-8')

# class TdContextJsonFormatter(jsonlogger.JsonFormatter):

# 	def __init__(self, *args, **kwargs):
# 		super().__init__(*args, **kwargs, json_serializer=serializeJson)

# 	def parse(self) -> list[str]:
# 		return [
# 			'message',
# 			'asctime',
# 			'absframe',
# 			'frame',
# 			'source',
# 			'severity',
# 			'type',
# 		]

# 	def add_fields(
# 		self, log_record: dict[str, Any], record: logging.LogRecord,
# 		message_dict: dict[str, Any]
# 	) -> None:
# 		super().add_fields(log_record, record, message_dict)

# 		log_record['absframe'] = absTime.frame
# 		log_record['source'] = f'/{record.name.replace(".", "/")}'
# 		log_record['severity'] = record.levelname  # TODO: do we need to map these?

# 		component = log_record.get('component', None)
# 		if component:
# 			log_record['type'] = component.type
# 			log_record['frame'] = component.time.frame
# 			del log_record['component']
# 		else:
# 			log_record['type'] = 'UNKNOWN'
# 			log_record['frame'] = me.time.frame
