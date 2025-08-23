"""
PyWire Full Testing Example
Comprehensive test of all PyWire features including:
- Custom browser path
- Window size and position
- All API functions
- Event system
- Real-time communication
- Error handling
- Performance testing
"""
# Thanks to ChatGPT for the example
import logging
logging.basicConfig(level=logging.DEBUG)
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'PyWire'))

import pywire
import time
import random
import threading
import json
import platform
from datetime import datetime

# Test configuration
TEST_CONFIG = {
    'window_size': (800, 500),
    'window_position': (50, 50),
    'custom_browser_path': None,  # Set to browser path if you want to test custom browser
    'test_port': 8080,
    'enable_monitoring': True,
    'enable_stress_test': True
}

# Global test state
test_state = {
    'counter': 0,
    'users': [],
    'messages': [],
    'test_results': [],
    'is_monitoring': False,
    'stress_test_running': False,
    'start_time': time.time()
}

# === BASIC FUNCTION TESTS ===

@pywire.expose
def test_hello(name="PyWire Tester"):
    """Test basic string return."""
    return f"Hello, {name}! PyWire is working perfectly."

@pywire.expose
def test_math_operations(a, b):
    """Test math operations and type conversion."""
    try:
        a, b = float(a), float(b)
        return {
            'addition': a + b,
            'subtraction': a - b,
            'multiplication': a * b,
            'division': a / b if b != 0 else 'Division by zero',
            'power': a ** b,
            'inputs': {'a': a, 'b': b}
        }
    except (ValueError, TypeError) as e:
        return {'error': f'Invalid input: {e}'}

@pywire.expose
def test_data_types():
    """Test various data types."""
    return {
        'string': 'Hello World',
        'integer': 42,
        'float': 3.14159,
        'boolean': True,
        'null': None,
        'list': [1, 2, 3, 'four', 5.0],
        'dict': {'nested': {'value': 'test'}},
        'timestamp': time.time()
    }

# === STATE MANAGEMENT TESTS ===

@pywire.expose
def test_increment_counter():
    """Test state persistence."""
    test_state['counter'] += 1
    pywire.emit_event('counter_updated', {'value': test_state['counter']})
    return test_state['counter']

@pywire.expose
def test_get_counter():
    """Test state retrieval."""
    return test_state['counter']

@pywire.expose
def test_reset_counter():
    """Test state modification."""
    test_state['counter'] = 0
    pywire.emit_event('counter_updated', {'value': 0})
    return 'Counter reset to 0'

# === USER MANAGEMENT TESTS ===

@pywire.expose
def test_add_user(name, email, age=None):
    """Test complex data handling."""
    if not name or not email:
        return {'success': False, 'error': 'Name and email are required'}
    
    # Validate email format
    if '@' not in email:
        return {'success': False, 'error': 'Invalid email format'}
    
    user = {
        'id': len(test_state['users']) + 1,
        'name': name,
        'email': email,
        'age': int(age) if age else None,
        'created': datetime.now().isoformat(),
        'active': True
    }
    
    test_state['users'].append(user)
    pywire.emit_event('user_added', user)
    
    return {'success': True, 'user': user, 'total_users': len(test_state['users'])}

@pywire.expose
def test_get_users():
    """Test data retrieval."""
    return {
        'users': test_state['users'],
        'count': len(test_state['users']),
        'active_count': len([u for u in test_state['users'] if u.get('active', True)])
    }

@pywire.expose
def test_delete_user(user_id):
    """Test data deletion."""
    try:
        user_id = int(user_id)
        for i, user in enumerate(test_state['users']):
            if user['id'] == user_id:
                deleted_user = test_state['users'].pop(i)
                pywire.emit_event('user_deleted', {'user': deleted_user})
                return {'success': True, 'deleted_user': deleted_user}
        return {'success': False, 'error': 'User not found'}
    except ValueError:
        return {'success': False, 'error': 'Invalid user ID'}

# === REAL-TIME COMMUNICATION TESTS ===

@pywire.expose
def test_send_message(message, sender="Anonymous"):
    """Test real-time messaging."""
    if not message.strip():
        return {'success': False, 'error': 'Message cannot be empty'}
    
    msg = {
        'id': len(test_state['messages']) + 1,
        'text': message,
        'sender': sender,
        'timestamp': datetime.now().isoformat(),
        'type': 'user'
    }
    
    test_state['messages'].append(msg)
    pywire.emit_event('new_message', msg)
    
    return {'success': True, 'message': msg}

@pywire.expose
def test_get_messages(limit=50):
    """Test message retrieval with pagination."""
    try:
        limit = int(limit)
        messages = test_state['messages'][-limit:] if limit > 0 else test_state['messages']
        return {
            'messages': messages,
            'total': len(test_state['messages']),
            'showing': len(messages)
        }
    except ValueError:
        return {'error': 'Invalid limit value'}

@pywire.expose
def test_broadcast_system_message(message):
    """Test system message broadcasting."""
    msg = {
        'id': len(test_state['messages']) + 1,
        'text': message,
        'sender': 'System',
        'timestamp': datetime.now().isoformat(),
        'type': 'system'
    }
    
    test_state['messages'].append(msg)
    pywire.emit_event('system_message', msg)
    
    return {'success': True, 'message': msg}

# === MONITORING TESTS ===

@pywire.expose
def test_start_monitoring():
    """Test real-time monitoring."""
    if test_state['is_monitoring']:
        return {'success': False, 'error': 'Monitoring already active'}
    
    test_state['is_monitoring'] = True
    
    def monitor_loop():
        while test_state['is_monitoring']:
            # Simulate system metrics
            data = {
                'cpu': random.uniform(0, 100),
                'memory': random.uniform(20, 90),
                'disk': random.uniform(10, 80),
                'network_in': random.uniform(0, 1000),
                'network_out': random.uniform(0, 500),
                'timestamp': time.time(),
                'uptime': time.time() - test_state['start_time']
            }
            pywire.emit_event('monitoring_data', data)
            time.sleep(1)
    
    threading.Thread(target=monitor_loop, daemon=True).start()
    return {'success': True, 'message': 'Monitoring started'}

@pywire.expose
def test_stop_monitoring():
    """Test stopping monitoring."""
    test_state['is_monitoring'] = False
    return {'success': True, 'message': 'Monitoring stopped'}

# === PERFORMANCE TESTS ===

@pywire.expose
def test_fibonacci_performance(n):
    """Test CPU-intensive operations."""
    try:
        n = int(n)
        if n < 0:
            return {'error': 'Number must be non-negative'}
        if n > 40:
            return {'error': 'Number too large (max 40 for performance)'}
        
        def fib(x):
            if x <= 1:
                return x
            return fib(x-1) + fib(x-2)
        
        start_time = time.time()
        result = fib(n)
        end_time = time.time()
        
        calculation_time = (end_time - start_time) * 1000
        
        return {
            'input': n,
            'result': result,
            'calculation_time_ms': round(calculation_time, 3),
            'performance_rating': 'Fast' if calculation_time < 100 else 'Slow'
        }
    except ValueError:
        return {'error': 'Invalid input'}

@pywire.expose
def test_stress_test(duration=10):
    """Test system under load."""
    try:
        duration = int(duration)
        if duration > 60:
            return {'error': 'Duration too long (max 60 seconds)'}
        
        if test_state['stress_test_running']:
            return {'error': 'Stress test already running'}
        
        test_state['stress_test_running'] = True
        
        def stress_loop():
            start = time.time()
            operations = 0
            
            while time.time() - start < duration and test_state['stress_test_running']:
                # Perform various operations
                _ = [random.random() for _ in range(1000)]
                operations += 1000
                
                # Send progress updates
                progress = ((time.time() - start) / duration) * 100
                pywire.emit_event('stress_test_progress', {
                    'progress': min(progress, 100),
                    'operations': operations,
                    'elapsed': time.time() - start
                })
                
                time.sleep(0.1)
            
            test_state['stress_test_running'] = False
            pywire.emit_event('stress_test_complete', {
                'total_operations': operations,
                'duration': time.time() - start,
                'ops_per_second': operations / (time.time() - start)
            })
        
        threading.Thread(target=stress_loop, daemon=True).start()
        return {'success': True, 'message': f'Stress test started for {duration} seconds'}
        
    except ValueError:
        return {'error': 'Invalid duration'}

@pywire.expose
def test_stop_stress_test():
    """Stop stress test."""
    test_state['stress_test_running'] = False
    return {'success': True, 'message': 'Stress test stopped'}

# === SYSTEM INFO TESTS ===

@pywire.expose
def test_get_system_info():
    """Test system information gathering."""
    return {
        'platform': {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'architecture': platform.architecture(),
            'python_version': platform.python_version()
        },
        'pywire': {
            'version': pywire.__version__,
            'exposed_functions': len(pywire.get_exposed_functions()),
            'uptime': time.time() - test_state['start_time']
        },
        'test_state': {
            'counter': test_state['counter'],
            'users': len(test_state['users']),
            'messages': len(test_state['messages']),
            'monitoring_active': test_state['is_monitoring'],
            'stress_test_running': test_state['stress_test_running']
        }
    }

# === FILE OPERATION TESTS ===

@pywire.expose
def test_save_test_data():
    """Test file operations."""
    try:
        test_data = {
            'test_results': test_state['test_results'],
            'users': test_state['users'],
            'messages': test_state['messages'],
            'system_info': test_get_system_info(),
            'export_time': datetime.now().isoformat()
        }
        
        filename = f"pywire_test_data_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(test_data, f, indent=2)
        
        return {
            'success': True,
            'filename': filename,
            'size_bytes': os.path.getsize(filename),
            'records': len(test_data)
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

# === JAVASCRIPT INTERACTION TESTS ===

@pywire.expose
def test_call_javascript():
    """Test calling JavaScript from Python."""
    try:
        # Call JavaScript function
        pywire.call_js('showTestNotification', 'Hello from Python!', 'success')
        pywire.call_js('updateTestStatus', 'JavaScript call successful')
        return {'success': True, 'message': 'JavaScript functions called'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# === ERROR HANDLING TESTS ===

@pywire.expose
def test_error_handling(error_type="none"):
    """Test various error conditions."""
    if error_type == "value_error":
        raise ValueError("This is a test ValueError")
    elif error_type == "type_error":
        raise TypeError("This is a test TypeError")
    elif error_type == "runtime_error":
        raise RuntimeError("This is a test RuntimeError")
    elif error_type == "division_by_zero":
        return 1 / 0
    elif error_type == "key_error":
        d = {}
        return d['nonexistent_key']
    else:
        return {'success': True, 'message': 'No error generated'}

def main():
    """Main test application."""
    print("🧪 PyWire Full Testing Suite")
    print("=" * 60)
    
    # Initialize PyWire
    pywire.init('web')
    print("✅ PyWire initialized")
    
    # Show all exposed functions
    functions = pywire.get_exposed_functions()
    print(f"✅ Exposed {len(functions)} test functions:")
    for func in sorted(functions):
        print(f"   - {func}")
    
    print(f"\n🔧 Test Configuration:")
    print(f"   - Window Size: {TEST_CONFIG['window_size']}")
    print(f"   - Window Position: {TEST_CONFIG['window_position']}")
    print(f"   - Test Port: {TEST_CONFIG['test_port']}")
    print(f"   - Custom Browser: {TEST_CONFIG['custom_browser_path'] or 'Auto-detect'}")
    
    print("\n🚀 Starting PyWire Test Suite...")
    print("📱 The test application will open in your browser")
    print("🧪 Run all tests to verify PyWire functionality")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 60)
    
    try:
        # Start with custom configuration
        pywire.start(
            page='test.html',
            port=TEST_CONFIG['test_port'],
            size=TEST_CONFIG['window_size'],
            position=TEST_CONFIG['window_position']
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down test suite...")
        test_state['is_monitoring'] = False
        test_state['stress_test_running'] = False
        pywire.stop()
        print("✅ PyWire test suite stopped successfully!")

if __name__ == '__main__':
    main()
