"""
Simplified security configuration for PyWire.
"""

import re
from typing import Dict, Any, List


class InputValidator:
    """Basic input validation."""

    def __init__(self):
        pass

    def validate_function_name(self, func_name: str) -> bool:
        """Validate function name to prevent malicious calls."""
        if not isinstance(func_name, str):
            return False

        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', func_name):
            return False

        if func_name.startswith('_'):
            return False

        dangerous_funcs = {
            'eval', 'exec', 'compile', '__import__', 'open', 'file'
        }

        if func_name in dangerous_funcs:
            return False

        return True

    def validate_args(self, args: List[Any]) -> List[Any]:
        """Basic argument validation."""
        return args


class SecurityConfig:
    """Simplified security configuration."""

    def __init__(self):
        self.enable_input_validation = True
        self.max_message_size = 1024 * 1024  # 1MB
        self.allowed_origins = ['http://localhost', 'http://127.0.0.1']

    def update(self, **kwargs):
        """Update security configuration."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
