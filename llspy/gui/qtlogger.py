from click import get_app_dir
from logging.handlers import RotatingFileHandler
import logging
import os
import traceback
from PyQt5.QtCore import QObject, pyqtSignal


class NoExceptionTracebackFormatter(logging.Formatter):
    """Custom formatter for formatting exceptions without traceback."""

    def format(self, record):
        # Calls to formatException are cached.
        # (see http://bugs.python.org/issue1295)
        orig_exc_text = record.exc_text
        record.exc_text = None
        try:
            return super(NoExceptionTracebackFormatter, self).format(record)
        finally:
            record.exc_text = orig_exc_text

    def formatException(self, exc_info):
        etype, evalue, tb = exc_info
        lines = traceback.format_exception_only(etype, evalue)
        return u''.join(lines)


class NotificationHandler(QObject, logging.Handler):

    emitSignal = pyqtSignal(str)

    def __init__(self):
        super(NotificationHandler, self).__init__()
        self.setLevel(logging.DEBUG)
        self.setFormatter(NoExceptionTracebackFormatter('%(message)s'))

    def emit(self, record):
        level = record.levelno
        message = self.format(record)
        if level >= logging.INFO:
            self.emitSignal.emit(message)


class LogFileHandler(RotatingFileHandler):

    def __init__(self, **kwargs):
        appdir = get_app_dir('LLSpy')
        if not os.path.isdir(appdir):
            os.mkdir(appdir)
        _LOGPATH = os.path.join(appdir, 'llspygui.log')
        super(LogFileHandler, self).__init__(_LOGPATH, **kwargs)

        self.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.setFormatter(self.formatter)

    def filter(self, record):
        permitted = ['llspy', 'spimagine', 'fiducialreg']
        if any(record.name.startswith(l) for l in permitted):
            return True
        return False



