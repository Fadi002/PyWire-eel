import os
import socket
import threading
import json
import time
import base64
import hashlib
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Dict, Any, Optional, Callable, List
from .utils import SecurityManager, PortManager, Logger, MessageQueue, validate_json_message
from .security import InputValidator, SecurityConfig


class PyWireHTTPRequestHandler(SimpleHTTPRequestHandler):
    """PyWire HTTP request handler with dynamic port injection."""

    def __init__(self, *args, ws_port=None, **kwargs):
        self.ws_port = ws_port
        super().__init__(*args, **kwargs)

    def end_headers(self):
        super().end_headers()

    def do_GET(self):
        if self.path.endswith('/bridge.js'):
            self.serve_bridge_js()
        else:
            super().do_GET()

    def serve_bridge_js(self):
        """Serve bridge.js with dynamic WebSocket port injection."""
        try:
            bridge_path = os.path.join(os.path.dirname(__file__), 'web', 'bridge.js')
            with open(bridge_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if self.ws_port:
                content = content.replace(
                    'const commonPorts = [8001, 8002, 8003, 8004, 8005];',
                    f'const commonPorts = [{self.ws_port}];'
                )

            self.send_response(200)
            self.send_header('Content-Type', 'application/javascript')
            self.send_header('Content-Length', str(len(content.encode('utf-8'))))
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))

        except Exception as e:
            self.send_error(404, f"bridge.js not found: {e}")

    def log_message(self, format, *args):
        """Override to use PyWire logger."""
        logger = Logger("HTTP")
        logger.info(format % args)


class HTTPServerThread(threading.Thread):
    """PyWire HTTP server with dynamic bridge.js injection."""

    def __init__(self, port=8000, folder="web", ws_port=None):
        super().__init__()
        self.port = port
        self.folder = folder
        self.ws_port = ws_port
        self.logger = Logger("HTTP")
        self.server = None

    def run(self):
        """Start the HTTP server."""
        try:
            original_cwd = os.getcwd()
            if os.path.isdir(self.folder):
                os.chdir(self.folder)

            def handler_factory(*args, **kwargs):
                return PyWireHTTPRequestHandler(*args, ws_port=self.ws_port, **kwargs)

            self.server = HTTPServer(("127.0.0.1", self.port), handler_factory)
            self.logger.info(f"Serving on http://127.0.0.1:{self.port}")
            self.server.serve_forever()

        except Exception as e:
            self.logger.error(f"HTTP server error: {e}")
        finally:
            # Restore original working directory
            try:
                os.chdir(original_cwd)
            except:
                pass

    def stop(self):
        """Stop the HTTP server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()

class WSClient:
    """Simple WebSocket client."""

    def __init__(self, conn, addr, client_id=None):
        self.conn = conn
        self.addr = addr
        self.client_id = client_id or f"{addr[0]}:{addr[1]}:{int(time.time())}"

    def send_ws(self, message):
        """Send WebSocket message with proper framing."""
        try:
            if isinstance(message, str):
                payload = message.encode('utf-8')
            else:
                payload = message

            header = bytearray([0x81])
            length = len(payload)

            if length < 126:
                header.append(length)
            elif length < (1 << 16):
                header.append(126)
                header.extend(length.to_bytes(2, "big"))
            else:
                header.append(127)
                header.extend(length.to_bytes(8, "big"))

            self.conn.send(header + payload)
            return True
        except Exception:
            return False

    def send_error(self, error_message: str, call_id: str = None):
        """Send error message to client."""
        error_data = {
            "type": "response",
            "error": error_message
        }
        if call_id:
            error_data["call_id"] = call_id
        self.send_ws(json.dumps(error_data))

    def send_result(self, result: Any, call_id: str = None):
        """Send result message to client."""
        result_data = {
            "type": "response",
            "result": result
        }
        if call_id:
            result_data["call_id"] = call_id
        self.send_ws(json.dumps(result_data))


class WSServerThread(threading.Thread):
    """Simple WebSocket server."""

    def __init__(self, port=8001, bridge=None, security_config=None):
        super().__init__()
        self.port = port
        self.bridge = bridge
        self.logger = Logger("WebSocket")
        self.security_manager = SecurityManager()
        self.input_validator = InputValidator()
        # Use the bridge's message queue instead of creating a new one
        self.message_queue = bridge.message_queue if bridge else MessageQueue()
        self.server_socket = None
        self.running = False

    def run(self):
        """Start the WebSocket server."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(("127.0.0.1", self.port))
            self.server_socket.listen(5)
            self.running = True

            self.logger.info(f"WebSocket server listening on ws://127.0.0.1:{self.port}")

            while self.running:
                try:
                    client_conn, addr = self.server_socket.accept()
                    if self.running:
                        client_thread = threading.Thread(
                            target=self.handle_client,
                            args=(client_conn, addr),
                            daemon=True
                        )
                        client_thread.start()
                except OSError:
                    if self.running:
                        self.logger.error("Socket error in WebSocket server")
                    break

        except Exception as e:
            self.logger.error(f"WebSocket server error: {e}")
        finally:
            self.cleanup()

    def stop(self):
        """Stop the WebSocket server."""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

    def cleanup(self):
        """Clean up server resources."""
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

    def handle_client(self, conn, addr):
        """Handle individual WebSocket client."""
        client = WSClient(conn, addr)

        try:
            if not self.handshake(conn):
                conn.close()
                return

            self.bridge.clients.append(client)
            self.logger.info(f"Client connected: {addr}")

            while self.running:
                try:
                    data = self.recv_ws(conn)
                    if not data:
                        break
                    self.process_message(client, data)
                except Exception as e:
                    self.logger.error(f"Error processing message from {addr}: {e}")
                    client.send_error("Message processing error")

        except Exception as e:
            self.logger.error(f"Client handler error for {addr}: {e}")
        finally:
            if client in self.bridge.clients:
                self.bridge.clients.remove(client)
            try:
                conn.close()
            except:
                pass
            self.logger.info(f"Client disconnected: {addr}")

    def process_message(self, client: WSClient, data: str):
        """Process incoming WebSocket message."""
        msg = validate_json_message(data)
        if not msg:
            client.send_error("Invalid JSON message")
            return

        msg_type = msg.get("type", "call")
        call_id = msg.get("call_id")

        if msg_type == "call":
            self.handle_function_call(client, msg, call_id)
        elif msg_type == "response":
            self.handle_response(client, msg, call_id)
        elif msg_type == "ping":
            client.send_ws(json.dumps({"type": "pong", "call_id": call_id}))
        else:
            client.send_error("Unknown message type", call_id)

    def handle_function_call(self, client: WSClient, msg: Dict[str, Any], call_id: str):
        """Handle function call from client."""
        func_name = msg.get("func")
        args = msg.get("args", [])

        if not func_name or not self.input_validator.validate_function_name(func_name):
            client.send_error("Invalid function name", call_id)
            return

        if func_name not in self.bridge.exposed_funcs:
            client.send_error(f"Function '{func_name}' not found", call_id)
            return

        try:
            func = self.bridge.exposed_funcs[func_name]
            result = func(*args)
            client.send_result(result, call_id)
        except Exception as e:
            client.send_error(f"Function execution error: {str(e)}", call_id)

    def handle_response(self, client: WSClient, msg: Dict[str, Any], call_id: str):
        """Handle response from client (for Python -> JS calls)."""
        if call_id:
            result = msg.get("result")
            error = msg.get("error")
            self.message_queue.resolve_call(call_id, result, error)

    def handshake(self, client_socket) -> bool:
        """Perform WebSocket handshake with security checks."""
        try:
            request = client_socket.recv(4096).decode('utf-8')
            if not request:
                return False

            # Parse headers
            headers = {}
            lines = request.split('\r\n')

            # Validate request line
            if not lines[0].startswith('GET'):
                return False

            # Parse headers
            for line in lines[1:]:
                if ': ' in line:
                    key, value = line.split(': ', 1)
                    headers[key.lower()] = value

            # Validate WebSocket headers
            required_headers = {
                'upgrade': 'websocket',
                'connection': 'upgrade',
                'sec-websocket-version': '13'
            }

            for header, expected_value in required_headers.items():
                if header not in headers or headers[header].lower() != expected_value.lower():
                    return False

            # Get WebSocket key
            ws_key = headers.get('sec-websocket-key')
            if not ws_key:
                return False

            # Generate accept key
            accept_key = base64.b64encode(
                hashlib.sha1((ws_key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()
            ).decode()

            # Send handshake response
            response = (
                'HTTP/1.1 101 Switching Protocols\r\n'
                'Upgrade: websocket\r\n'
                'Connection: Upgrade\r\n'
                f'Sec-WebSocket-Accept: {accept_key}\r\n'
                '\r\n'
            )

            client_socket.send(response.encode())
            return True

        except Exception as e:
            self.logger.error(f"Handshake error: {e}")
            return False

    def recv_ws(self, client_socket, timeout: int = None) -> Optional[str]:
        """Receive WebSocket message with proper frame parsing."""
        try:
            if timeout:
                client_socket.settimeout(timeout)

            # Read frame header
            header = client_socket.recv(2)
            if len(header) < 2:
                return None

            # Parse frame
            fin = (header[0] & 0x80) != 0
            opcode = header[0] & 0x0F
            masked = (header[1] & 0x80) != 0
            payload_length = header[1] & 0x7F

            # Handle different payload lengths
            if payload_length == 126:
                length_data = client_socket.recv(2)
                payload_length = int.from_bytes(length_data, 'big')
            elif payload_length == 127:
                length_data = client_socket.recv(8)
                payload_length = int.from_bytes(length_data, 'big')



            # Read mask if present
            mask = None
            if masked:
                mask = client_socket.recv(4)

            # Read payload
            payload = b''
            remaining = payload_length
            while remaining > 0:
                chunk = client_socket.recv(min(remaining, 4096))
                if not chunk:
                    return None
                payload += chunk
                remaining -= len(chunk)

            # Unmask payload if needed
            if masked and mask:
                payload = bytes(payload[i] ^ mask[i % 4] for i in range(len(payload)))

            # Handle different opcodes
            if opcode == 0x8:  # Close frame
                return None
            elif opcode == 0x9:  # Ping frame
                # Send pong response
                pong_frame = bytearray([0x8A, len(payload)]) + payload
                client_socket.send(pong_frame)
                return self.recv_ws(client_socket, timeout)
            elif opcode == 0xA:  # Pong frame
                return self.recv_ws(client_socket, timeout)
            elif opcode in (0x1, 0x0):  # Text or continuation frame
                return payload.decode('utf-8')
            else:
                return None

        except socket.timeout:
            return None
        except Exception as e:
            self.logger.error(f"WebSocket receive error: {e}")
            return None
        finally:
            if timeout:
                client_socket.settimeout(None)


