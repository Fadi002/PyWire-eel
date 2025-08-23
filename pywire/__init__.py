from .bridge import PyWire
from .security import SecurityConfig
from .utils import Logger
import sys
import signal
import atexit
sys.dont_write_bytecode = True
__version__ = "0.1.0"

_pywire_instance = PyWire()

def _cleanup_on_exit():
    """Cleanup function called on script exit."""
    try:
        if _pywire_instance.running:
            _pywire_instance.stop()
    except:
        pass

def _signal_handler(signum, frame):
    """Handle shutdown signals."""
    try:
        _pywire_instance.stop()
    except:
        pass
    import os
    os._exit(0)

# Register cleanup handlers
atexit.register(_cleanup_on_exit)
signal.signal(signal.SIGINT, _signal_handler)  # Ctrl+C
signal.signal(signal.SIGTERM, _signal_handler)  # Termination signal

def init(web_folder, allowed_extensions=None):
    return _pywire_instance.init(web_folder)

def expose(name_or_function=None):
    return _pywire_instance.expose(name_or_function)

def start(page='index.html', mode=None, host='localhost', port=8000,
          block=True, jinja_templates=None, cmdline_args=None, size=None, position=None):
    """Start PyWire application (Eel-compatible)."""
    return _pywire_instance.start(page=page, port=port, block=block, size=size, position=position)

def sleep(seconds):
    """Sleep function (Eel-compatible)."""
    import time
    time.sleep(seconds)

call_js = _pywire_instance.call_js
call_js_async = _pywire_instance.call_js_async
emit_event = _pywire_instance.emit_event
on_event = _pywire_instance.on_event
stop = _pywire_instance.stop
get_exposed_functions = _pywire_instance.get_exposed_functions
set_custom_browser = _pywire_instance.set_custom_browser
get_browser_info = _pywire_instance.get_browser_info

# Enable Eel-style function calling at module level
def __getattr__(name: str):
    """Enable Eel-style function calling: pywire.function_name(*args)"""
    if name.startswith('_'):
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
    return getattr(_pywire_instance, name)

__all__ = [
    'init',
    'expose',
    'start',
    'sleep',
    'call_js',
    'call_js_async',
    'emit_event',
    'on_event',
    'stop',
    'get_exposed_functions',
    'set_custom_browser',
    'get_browser_info',
    'PyWire',
    'SecurityConfig',
    'Logger'
]
