import os
import webbrowser
import json
import time
import sys
from typing import Dict, Any, Callable, Optional, List
from .server import HTTPServerThread, WSServerThread
from .utils import PortManager, Logger, MessageQueue
from .browser import BrowserDetector, BrowserLauncher


class PyWire:
    """Simple PyWire bridge"""

    def __init__(self):
        self.exposed_funcs: Dict[str, Callable] = {}
        self.http_port: Optional[int] = None
        self.ws_port: Optional[int] = None
        self.web_folder: Optional[str] = None
        self.clients: List[Any] = []
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.logger = Logger("PyWire")
        self.message_queue = MessageQueue()
        self.http_server: Optional[HTTPServerThread] = None
        self.ws_server: Optional[WSServerThread] = None
        self.browser_detector: Optional[BrowserDetector] = None
        self.browser_launcher: Optional[BrowserLauncher] = None
        self.running = False
        self.auto_shutdown = True  # Auto-shutdown when browser closes
        self.browser_process = None  # Track browser process
        self._shutdown_monitor_thread = None
        self._last_client_count = 0
        self._no_clients_start_time = None

    def expose(self, func: Callable = None, *, name: str = None):
        """
        Decorator to expose Python functions to JavaScript.
        """
        def decorator(f: Callable) -> Callable:
            func_name = name or f.__name__
            self.exposed_funcs[func_name] = f
            return f

        if func is None:
            return decorator
        else:
            return decorator(func)

    def init(self, web_folder: str):
        """
        Initialize PyWire with web folder.
        """
        self.web_folder = web_folder
        if not os.path.isdir(web_folder):
            raise ValueError(f"Web folder not found: {web_folder}")
        self.logger.info(f"Initialized with web folder: {web_folder}")

    def start(self, page: str = "index.html", mode=None, host='localhost', port: int = 8000,
              block: bool = True, size=None, position=None):
        """Start PyWire application."""
        if not self.web_folder:
            raise ValueError("Web folder not found. Call init() first.")

        # Initialize browser detection
        if not self.browser_detector:
            self.browser_detector = BrowserDetector()
            self.browser_launcher = BrowserLauncher(self.browser_detector)

        self.http_port = PortManager.find_free_port(port)
        self.ws_port = PortManager.find_free_port(self.http_port + 1)

        self.logger.info(f"Starting on http://127.0.0.1:{self.http_port}")

        self._start_servers()
        self._open_browser(page, mode, size, position)
        self.running = True

        # Start browser connection monitoring for auto-shutdown
        self._start_shutdown_monitor()

        if block:
            self._keep_alive()

    def _start_servers(self):
        """Start HTTP and WebSocket servers."""
        self.http_server = HTTPServerThread(
            port=self.http_port,
            folder=self.web_folder,
            ws_port=self.ws_port
        )
        self.http_server.daemon = True
        self.http_server.start()

        self.ws_server = WSServerThread(
            port=self.ws_port,
            bridge=self
        )
        self.ws_server.daemon = True
        self.ws_server.start()

        time.sleep(0.5)

    def _open_browser(self, page: str, mode=None, size=None, position=None):
        url = f"http://127.0.0.1:{self.http_port}/{page}"

        try:
            # Get the best available browser
            best_browser = self.browser_detector.get_best_browser()

            if best_browser:
                self.logger.info(f"Launching {best_browser} browser")

                # Determine if we should use app mode
                app_mode = mode in ['app', 'chrome-app'] if mode else True
                kiosk_mode = mode in ['kiosk', 'chrome-kiosk'] if mode else False

                # Launch with enhanced browser launcher
                if not self.browser_launcher:
                    self.browser_launcher = BrowserLauncher(self.browser_detector)

                launch_params = {
                    'url': url,
                    'browser': best_browser,
                    'app_mode': app_mode,
                    'kiosk': kiosk_mode
                }

                if size:
                    launch_params['size'] = size
                if position:
                    launch_params['position'] = position

                success, process = self.browser_launcher.launch_browser(**launch_params)

                if success:
                    self.browser_process = process  # Track browser process
                    browser_info = self.browser_detector.get_browser_info(best_browser)
                    self.logger.info(f"Successfully launched {browser_info['name']}")
                    return
                else:
                    self.logger.warning(f"Failed to launch {best_browser}, falling back to default")

            # Fallback to default browser
            self.logger.info("Using default browser")
            webbrowser.open(url)

        except Exception as e:
            self.logger.error(f"Error launching browser: {e}")
            # Final fallback
            webbrowser.open(url)
    def _keep_alive(self):
        """Keep the main thread alive."""
        try:
            while self.running:
                time.sleep(1)
                self.message_queue.cleanup_expired_calls()
        except KeyboardInterrupt:
            self.stop()

    def set_custom_browser(self, browser_path: str, browser_type: str = "custom"):
        """Set a custom browser path."""
        if not self.browser_detector:
            self.browser_detector = BrowserDetector()

        success = self.browser_detector.set_custom_browser_path(browser_path, browser_type)
        if success:
            self.logger.info(f"Custom browser set: {browser_path}")
        else:
            self.logger.error(f"Failed to set custom browser: {browser_path}")
        return success

    def get_browser_info(self):
        """Get information about detected browsers."""
        if not self.browser_detector:
            self.browser_detector = BrowserDetector()

        return {
            'detected_browsers': list(self.browser_detector.detected_browsers.keys()),
            'best_browser': self.browser_detector.get_best_browser(),
            'browser_details': self.browser_detector.detected_browsers
        }

    def _start_shutdown_monitor(self):
        """Start monitoring browser connections for auto-shutdown."""
        if not self.auto_shutdown or self._shutdown_monitor_thread:
            return

        import threading
        self._shutdown_monitor_thread = threading.Thread(target=self._monitor_browser_connection, daemon=True)
        self._shutdown_monitor_thread.start()
        self.logger.info("Browser connection monitor started")

    def _monitor_browser_connection(self):
        """Monitor browser connection and auto-shutdown when browser closes."""
        import time
        shutdown_delay = 3  # seconds to wait after all clients disconnect

        while self.running:
            try:
                current_clients = len(self.clients)

                if current_clients > 0:
                    self._last_client_count = current_clients
                    self._no_clients_start_time = None
                else:
                    if self._last_client_count > 0 and self._no_clients_start_time is None:
                        self._no_clients_start_time = time.time()
                        self.logger.info(f"All browser clients disconnected. Auto-shutdown in {shutdown_delay}s...")

                    if (self._no_clients_start_time and
                        (time.time() - self._no_clients_start_time) > shutdown_delay):
                        self.logger.info("Browser closed - initiating auto-shutdown")
                        self._force_shutdown()
                        break

                time.sleep(1)  # Check every second

            except Exception as e:
                self.logger.error(f"Error in browser monitor: {e}")
                time.sleep(2)

    def _force_shutdown(self):
        """Force shutdown of the application."""
        try:
            self.running = False
            self._close_browser()
            if self.http_server:
                self.http_server.stop()
            if self.ws_server:
                self.ws_server.stop()

            # Force exit the process
            import os
            self.logger.info("PyWire shutdown complete")
            os._exit(0)
        except Exception as e:
            self.logger.error(f"Error during force shutdown: {e}")
            import os
            os._exit(1)

    def _close_browser(self):
        """Close the browser process if we launched it."""
        try:
            if self.browser_process:
                self.browser_process.terminate()
                self.logger.info("Browser process terminated")
        except Exception as e:
            self.logger.debug(f"Could not terminate browser process: {e}")

    def stop(self):
        """Stop PyWire application."""
        self.running = False
        self._close_browser()
        if self.http_server:
            self.http_server.stop()
        if self.ws_server:
            self.ws_server.stop()

    def call_js(self, func: str, *args, timeout: float = 30.0):
        """Call JavaScript function from Python and wait for response."""
        if not self.clients:
            raise RuntimeError("No JavaScript clients connected")

        call_id = self.message_queue.generate_call_id()
        msg = {
            "type": "call",
            "func": func,
            "args": list(args),
            "call_id": call_id
        }

        # Add pending call to message queue
        import threading
        result_event = threading.Event()
        result_container = {'result': None, 'error': None}

        def callback(result, error):
            result_container['result'] = result
            result_container['error'] = error
            result_event.set()

        self.message_queue.add_pending_call(call_id, callback)

        message_json = json.dumps(msg)
        sent = False
        for client in self.clients[:]:
            try:
                if client.send_ws(message_json):
                    sent = True
                    break
                else:
                    self.clients.remove(client)
            except Exception:
                if client in self.clients:
                    self.clients.remove(client)

        if not sent:
            raise RuntimeError("Failed to send message to any client")

        # Wait for response
        if result_event.wait(timeout):
            if result_container['error']:
                raise RuntimeError(f"JavaScript error: {result_container['error']}")
            return result_container['result']
        else:
            raise TimeoutError(f"JavaScript function '{func}' call timed out after {timeout} seconds")

    def call_js_async(self, func: str, *args):
        """Call JavaScript function from Python without waiting for response."""
        if not self.clients:
            return None

        call_id = self.message_queue.generate_call_id()
        msg = {
            "type": "call",
            "func": func,
            "args": list(args),
            "call_id": call_id
        }

        message_json = json.dumps(msg)
        for client in self.clients[:]:
            try:
                if not client.send_ws(message_json):
                    self.clients.remove(client)
            except Exception:
                if client in self.clients:
                    self.clients.remove(client)

    def __getattr__(self, name: str):
        """Enable Eel-style function calling: pywire.function_name(*args)"""
        if name.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        def js_function_caller(*args, **kwargs):
            timeout = kwargs.pop('timeout', 30.0)
            fire_and_forget = kwargs.pop('fire_and_forget', False)

            if kwargs:  # If there are remaining kwargs, it's an error
                raise TypeError(f"Unexpected keyword arguments: {list(kwargs.keys())}")

            if fire_and_forget:
                return self.call_js_async(name, *args)
            else:
                return self.call_js(name, *args, timeout=timeout)

        return js_function_caller

    def emit_event(self, event_name: str, data: Any = None):
        """Emit event to all connected JavaScript clients."""
        msg = {
            "type": "event",
            "event": event_name,
            "data": data
        }

        message_json = json.dumps(msg)
        for client in self.clients[:]:
            try:
                if not client.send_ws(message_json):
                    self.clients.remove(client)
            except Exception:
                if client in self.clients:
                    self.clients.remove(client)

    def on_event(self, event_name: str, handler: Callable):
        """Register event handler for events from JavaScript."""
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)

    def handle_js_event(self, event_name: str, data: Any):
        """Handle event received from JavaScript."""
        if event_name in self.event_handlers:
            for handler in self.event_handlers[event_name]:
                try:
                    handler(data)
                except Exception as e:
                    self.logger.error(f"Error in event handler: {e}")

    def get_exposed_functions(self) -> List[str]:
        """Get list of exposed function names."""
        return list(self.exposed_funcs.keys())
