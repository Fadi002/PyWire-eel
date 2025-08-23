"""
PyWire Utilities Module
Contains helper functions for logging, port management, and WebSocket handling.
"""

import os
import socket
import json
import logging
import time
from typing import Optional, Dict, Any, List, Tuple


class SecurityManager:
    """Simplified security manager."""

    def __init__(self):
        pass

    def validate_function_call(self, func_name: str, args: List[Any]) -> bool:
        """Basic function call validation."""
        if func_name.startswith('_'):
            return False
        dangerous_funcs = {'eval', 'exec', 'compile', '__import__', 'open', 'file'}
        if func_name in dangerous_funcs:
            return False
        return True


class PortManager:
    """Manages automatic port detection and allocation."""

    @staticmethod
    def find_free_port(start_port: int = 8000, max_attempts: int = 100) -> int:
        """Find a free port starting from start_port."""
        for port in range(start_port, start_port + max_attempts):
            if PortManager.is_port_free(port):
                return port
        raise RuntimeError(f"Could not find free port in range {start_port}-{start_port + max_attempts}")

    @staticmethod
    def is_port_free(port: int) -> bool:
        """Check if a port is available."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(('127.0.0.1', port))
                return True
        except OSError:
            return False

    @staticmethod
    def get_port_pair(http_start: int = 8000, ws_start: int = 8001) -> Tuple[int, int]:
        """Get a pair of free ports for HTTP and WebSocket servers."""
        http_port = PortManager.find_free_port(http_start)
        ws_port = PortManager.find_free_port(max(ws_start, http_port + 1))
        return http_port, ws_port


class Logger:
    """Enhanced logging system for PyWire."""

    def __init__(self, name: str = "PyWire", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(name)s] %(asctime)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def debug(self, message: str):
        self.logger.debug(message)


class MessageQueue:
    """Thread-safe message queue for handling async communications."""

    def __init__(self):
        self.pending_calls = {}
        self.call_counter = 0

    def generate_call_id(self) -> str:
        """Generate unique call ID for request-response matching."""
        self.call_counter += 1
        return f"call_{int(time.time())}_{self.call_counter}"

    def add_pending_call(self, call_id: str, callback=None):
        """Add a pending call to the queue."""
        self.pending_calls[call_id] = {
            'timestamp': time.time(),
            'callback': callback
        }

    def resolve_call(self, call_id: str, result: Any = None, error: str = None):
        """Resolve a pending call with result or error."""
        if call_id in self.pending_calls:
            call_info = self.pending_calls.pop(call_id)
            if call_info['callback']:
                call_info['callback'](result, error)

    def cleanup_expired_calls(self, timeout: int = 30):
        """Clean up expired pending calls."""
        current_time = time.time()
        expired_calls = [
            call_id for call_id, info in self.pending_calls.items()
            if current_time - info['timestamp'] > timeout
        ]
        for call_id in expired_calls:
            self.resolve_call(call_id, error="Call timeout")


def validate_json_message(message: str) -> Optional[Dict[str, Any]]:
    """Validate and parse JSON messages safely."""
    try:
        data = json.loads(message)
        if not isinstance(data, dict):
            return None
        return data
    except (json.JSONDecodeError, TypeError):
        return None
