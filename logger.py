import sys, os
import logging, logging.handlers
import unicodedata

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
        elif filename.startswith("./"):
            filename = filename[2:]
        rv = (filename, f.f_lineno, co.co_name)
    return rv

def deunicode(msg):
    if type(msg) == str:
        return unicodedata.normalize('NFKD', msg).encode('ascii','ignore')
    else:
        return str(msg)

def debug(msg, *args, **kwargs):
    thialfi_logger.debug(deunicode(msg), *args, **kwargs)

def info(msg, *args, **kwargs):
    thialfi_logger.info(deunicode(msg), *args, **kwargs)

def warning(msg, *args, **kwargs):
    thialfi_logger.warning(deunicode(msg), *args, **kwargs)

def error(msg, *args, **kwargs):
    thialfi_logger.error(deunicode(msg), *args, **kwargs)

# Configure logger only once
thialfi_logger = logging.getLogger('thialfi')
if not thialfi_logger.handlers:
    thialfi_logger.setLevel(logging.DEBUG)
    thialfi_logger.findCaller = findCaller

    stderr_handler = logging.StreamHandler()
    stderr_formatter = logging.Formatter('%(asctime)s [%(pathname)s:%(lineno)d] %(levelname)s: %(message)s',
                                         '%Y-%m-%d %H:%M:%S')
    stderr_handler.setFormatter(stderr_formatter)

    thialfi_logger.addHandler(stderr_handler)
