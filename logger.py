import sys, os
import logging, logging.handlers

__all__ = ['debug', 'info', 'warning', 'error']

# Make the debugging output a bit nicer.
global _thialfi_logger_dir_base
_thialfi_logger_dir_base = ""
def findCaller():
    global _thialfi_logger_dir_base
    if not _thialfi_logger_dir_base:
        _thialfi_logger_dir_base = os.path.dirname(__file__)
    f = sys._getframe(3)
    if f is not None:
        f = f.f_back
    rv = "(unknown file)", 0, "(unknown function)"
    if hasattr(f, "f_code"):
        co = f.f_code
        filename = os.path.normcase(co.co_filename)
        if filename.startswith(_thialfi_logger_dir_base):
            filename = os.path.relpath(filename, _thialfi_logger_dir_base)
        rv = (filename, f.f_lineno, co.co_name)
    return rv

def debug(*args, **kwargs):
    thialfi_logger.debug(*args, **kwargs)

def info(*args, **kwargs):
    thialfi_logger.info(*args, **kwargs)

def warning(*args, **kwargs):
    thialfi_logger.warning(*args, **kwargs)

def error(*args, **kwargs):
    thialfi_logger.error(*args, **kwargs)

thialfi_logger = logging.getLogger('thialfi')
thialfi_logger.setLevel(logging.DEBUG)
thialfi_logger.findCaller = findCaller
if not sys.stdout.isatty():
    syslog_handler = logging.handlers.SysLogHandler(facility=logging.handlers.SysLogHandler.LOG_USER, address='/dev/log')
    syslog_formatter = logging.Formatter('%(name)s: %(levelname)s: %(message)s')
    syslog_handler.setFormatter(syslog_formatter)
    thialfi_logger.addHandler(syslog_handler)
else:
    stderr_handler = logging.StreamHandler()
    stderr_formatter = logging.Formatter('[%(pathname)s:%(lineno)d] %(levelname)s: %(message)s')
    stderr_handler.setFormatter(stderr_formatter)
    thialfi_logger.addHandler(stderr_handler)

debug("Starting up...")

