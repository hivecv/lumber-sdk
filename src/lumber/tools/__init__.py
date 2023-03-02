from lumber.hub import LumberHubClient
import requests

import logging
import sys


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, original, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''
        self.original = original

    def write(self, buf):
        self.original.write(buf)
        temp_linebuf = self.linebuf + buf
        self.linebuf = ''
        for line in temp_linebuf.splitlines(True):
            if line[-1] == '\n':
                self.logger.log(self.log_level, line.rstrip())
            else:
                self.linebuf += line

    def flush(self):
        self.original.flush()
        if self.linebuf != '':
            self.logger.log(self.log_level, self.linebuf.rstrip())
        self.linebuf = ''


class LumberLogHandler(logging.Handler):
    def __init__(self, client: LumberHubClient):
        """
        Initialize the instance with the host, the request URL, and the method
        ("GET" or "POST")
        """
        logging.Handler.__init__(self)
        self.client = client

    def enable(self):
        root = logging.getLogger('')
        root.setLevel(logging.INFO)
        root.addHandler(self)
        sys.stdout = StreamToLogger(logging.getLogger('STDOUT'), sys.stdout, logging.INFO)
        sys.stderr = StreamToLogger(logging.getLogger('STDERR'), sys.stderr, logging.ERROR)

    def emit(self, record):
        try:
            requests.post(self.client.routes.device_logs, json=record.__dict__, headers=self.client.auth_headers)
        except Exception:
            pass
