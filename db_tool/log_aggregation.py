import os
import logging

class AggregatingFileHandler(logging.FileHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._message_counts = {}
        self._level_counts = {}
    def emit(self, record):
        super().emit(record)
        if record.levelname not in self._level_counts:
            self._level_counts[record.levelname] = 0
        self._level_counts[record.levelname] += 1
        message = self.format(record)
        if message not in self._message_counts:
            self._message_counts[message] = 0
        self._message_counts[message] += 1

    def close(self):
        super().close()
        fname, ext = os.path.splitext(self.baseFilename)
        with open(f"{fname}_aggregated{ext}", self.mode, encoding=self.encoding) as fh:
            level_message_parts = [f"{level}: {count}" for level, count in self._level_counts.items()]
            level_message = ", ".join(level_message_parts)
            fh.write(f"{level_message} is the by type breakdown, the aggregation follows.\n")
            for message, count in self._message_counts.items():
                fh.write(f"{message}\n")
                if count > 1:
                    fh.write(f"Appears {count} times.\n")