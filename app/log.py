import logging
import sys
from datetime import datetime
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['timestamp'] = now
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname


formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(module)s %(funcName)s %(lineno)s %(message)s')
json_handler = logging.StreamHandler(sys.stdout)
json_handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(json_handler)
logger.setLevel(logging.INFO)