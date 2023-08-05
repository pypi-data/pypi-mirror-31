import os
from ml_logger.serdes import serialize
from ml_logger.server import LogEntry, LoggingServer, ALLOWED_TYPES

class LogClient:
    local_server = None
    prefix = None

    def __init__(self, url: str = None, prefix=None):
        if url.startswith("file://"):
            self.local_server = LoggingServer(data_dir=url[6:])
        elif os.path.isabs(url):
            self.local_server = LoggingServer(data_dir=url)
        elif url.startswith('http://'):
            self.url = url
        else:
            # todo: add https, and s3://
            raise TypeError('log url need to begin with file:// or http://.')
        if prefix:
            assert not os.path.isabs(prefix), "prefix can not have leading slash`/`"
            self.prefix = prefix

    def _send(self, key, data, dtype):
        # todo: make this asynchronous
        if self.local_server:
            entry = LogEntry(key, data, dtype)._asdict()
            self.local_server.log(entry)
        else:
            import requests
            data = LogEntry(key, data, dtype)._asdict()
            requests.post(self.url, json=data)

    # appends data
    def log(self, key, data):
        self._send(key, data, dtype="log")

    # appends text
    def log_text(self, key, text):
        self._send(key, text, dtype="text")

    # sends out images
    def send_image(self, key, data):
        assert data.dtype in ALLOWED_TYPES, f"image data must be one of {ALLOWED_TYPES}"
        data = serialize(data)
        self._send(key, data, dtype="image")
