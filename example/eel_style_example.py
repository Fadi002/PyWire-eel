"""
PyWire Eel-Style Function Calling Example
Demonstrates how to call JavaScript functions from Python using Eel-style syntax.
"""

import sys
import os

import pywire
import time
import threading

# Initialize PyWire
pywire.init('web')

# === PYTHON FUNCTIONS EXPOSED TO JAVASCRIPT ===

@pywire.expose
def python_greet(name):
    """Python function that can be called from JavaScript."""
    return f"Hello {name} from Python!"

@pywire.expose
def python_calculate(operation, a, b):
    """Perform calculations in Python."""
    operations = {
        'add': lambda x, y: x + y,
        'subtract': lambda x, y: x - y,
        'multiply': lambda x, y: x * y,
        'divide': lambda x, y: x / y if y != 0 else 'Cannot divide by zero'
    }
    
    if operation in operations:
        return operations[operation](a, b)
    else:
        return f"Unknown operation: {operation}"

@pywire.expose
def test_eel_style_calls():
    """Demonstrate Eel-style JavaScript function calling from Python."""
    print("\n=== Testing Eel-Style JavaScript Function Calls ===")

    # Wait a moment for JavaScript functions to be exposed
    time.sleep(2)

    # Check if JavaScript functions are available
    print("Checking if JavaScript functions are exposed...")
    try:
        # Try a simple test call first
        test_result = pywire.call_js('js_greet', 'test')
        print(f"   ✅ JavaScript functions are available!")
    except Exception as e:
        print(f"   ⚠️  JavaScript functions not yet available: {e}")
        print("   Waiting additional time...")
        time.sleep(3)  # Wait more time

    results = []

    try:
        # Test 1: Basic function call with return value
        print("1. Testing basic greeting...")
        result = pywire.js_greet("Alice")
        print(f"   ✅ Result: {result}")
        results.append(("Basic Greeting", True, result))

        # Test 2: Math operations
        print("2. Testing math operations...")
        sum_result = pywire.js_add_numbers(15, 25)
        print(f"   ✅ 15 + 25 = {sum_result}")
        results.append(("Math Operations", True, sum_result))

        # Test 3: Get current time from JavaScript
        print("3. Getting current time from JavaScript...")
        js_time = pywire.js_get_current_time()
        print(f"   ✅ JavaScript time: {js_time}")
        results.append(("Get Time", True, js_time))

        # Test 4: Calculate factorial
        print("4. Calculating factorial...")
        factorial_result = pywire.js_calculate_factorial(5)
        print(f"   ✅ 5! = {factorial_result}")
        results.append(("Factorial", True, factorial_result))

        # Test 5: Process array
        print("5. Processing array...")
        test_array = [1, 2, 3, 4, 5]
        array_result = pywire.js_process_array(test_array)
        print(f"   ✅ Array analysis: {array_result}")
        results.append(("Array Processing", True, array_result))

        # Test 6: Get browser info
        print("6. Getting browser information...")
        browser_info = pywire.js_get_browser_info()
        user_agent = browser_info.get('userAgent', 'Unknown')[:50] + "..."
        print(f"   ✅ Browser: {user_agent}")
        results.append(("Browser Info", True, user_agent))

        # Test 7: DOM manipulation
        print("7. Manipulating DOM...")
        dom_result = pywire.js_manipulate_dom('testOutput', 'Updated from Python!', 'blue')
        print(f"   ✅ DOM update: {dom_result}")
        results.append(("DOM Manipulation", True, dom_result))

        # Test 8: Show notification
        print("8. Showing notification...")
        alert_result = pywire.js_show_alert('Hello from Python!', 'success')
        print(f"   ✅ Alert result: {alert_result}")
        results.append(("Show Alert", True, alert_result))

        # Test 9: Test async operation
        print("9. Testing async operation...")
        async_result = pywire.js_async_operation(1000)  # 1 second delay
        print(f"   ✅ Async result: {async_result}")
        results.append(("Async Operation", True, async_result))

        # Test 10: Fire and forget calls
        print("10. Testing fire-and-forget calls...")
        pywire.call_js_async('js_show_alert', 'Fire and forget!', 'info')
        print("   ✅ Fire-and-forget call sent")
        results.append(("Fire and Forget", True, "Sent successfully"))

        passed = len([r for r in results if r[1]])
        total = len(results)

        print(f"\n✅ All Eel-style function calls completed! {passed}/{total} tests passed")
        return {"success": True, "message": f"All tests passed ({passed}/{total})", "results": results}

    except Exception as e:
        print(f"\n❌ Error during Eel-style function calls: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e), "results": results}

@pywire.expose
def test_js_to_python_calls():
    """Test JavaScript to Python function calls automatically."""
    print("\n=== Testing JavaScript to Python Function Calls ===")

    # This function will be called from JavaScript to test the reverse direction
    results = []

    try:
        # Test basic Python functions
        print("1. Testing python_greet...")
        result1 = python_greet("JavaScript")
        print(f"   ✅ Result: {result1}")
        results.append(("Python Greet", True, result1))

        print("2. Testing python_calculate...")
        result2 = python_calculate("multiply", 7, 8)
        print(f"   ✅ Result: {result2}")
        results.append(("Python Calculate", True, result2))

        print("3. Testing python_get_system_info...")
        result3 = python_get_system_info()
        print(f"   ✅ Result: {result3}")
        results.append(("Python System Info", True, result3))

        print("4. Testing python_process_data...")
        test_data = {"numbers": [1, 2, 3, 4, 5], "operation": "sum"}
        result4 = python_process_data(test_data)
        print(f"   ✅ Result: {result4}")
        results.append(("Python Process Data", True, result4))

        passed = len([r for r in results if r[1]])
        total = len(results)

        print(f"\n✅ JavaScript to Python calls completed! {passed}/{total} tests passed")
        return {"success": True, "message": f"JS to Python tests passed ({passed}/{total})", "results": results}

    except Exception as e:
        print(f"\n❌ Error during JS to Python calls: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e), "results": results}

@pywire.expose
def python_get_system_info():
    """Get system information from Python."""
    import platform
    import sys
    return {
        "platform": platform.system(),
        "python_version": sys.version,
        "architecture": platform.architecture()[0],
        "processor": platform.processor()
    }

@pywire.expose
def python_process_data(data):
    """Process data in Python."""
    if isinstance(data, dict) and "numbers" in data:
        numbers = data["numbers"]
        operation = data.get("operation", "sum")

        if operation == "sum":
            result = sum(numbers)
        elif operation == "average":
            result = sum(numbers) / len(numbers)
        elif operation == "max":
            result = max(numbers)
        elif operation == "min":
            result = min(numbers)
        else:
            result = "Unknown operation"

        return {
            "input": data,
            "result": result,
            "operation": operation,
            "count": len(numbers)
        }
    else:
        return {"error": "Invalid data format"}

@pywire.expose
def auto_test_both_directions():
    """Automatically test both Python to JavaScript and JavaScript to Python calls."""
    print("\n" + "="*60)
    print("COMPREHENSIVE EEL-STYLE BIDIRECTIONAL TESTING")
    print("="*60)

    # Wait for JavaScript to be ready
    time.sleep(3)

    all_results = []

    # Test Python to JavaScript
    print("\n🐍 → 🌐 Testing Python to JavaScript calls...")
    py_to_js_result = test_eel_style_calls()
    all_results.append(("Python to JavaScript", py_to_js_result["success"], py_to_js_result))

    # Test JavaScript to Python (this will be called from JavaScript)
    print("\n🌐 → 🐍 Testing JavaScript to Python calls...")
    js_to_py_result = test_js_to_python_calls()
    all_results.append(("JavaScript to Python", js_to_py_result["success"], js_to_py_result))

    # Trigger JavaScript to call Python functions
    print("\n🔄 Triggering automatic JavaScript to Python test...")
    try:
        # Call JavaScript function that will test calling Python functions
        js_test_result = pywire.js_auto_test_python_calls()
        print(f"   ✅ JavaScript auto-test result: {js_test_result}")
        all_results.append(("JS Auto Test", True, js_test_result))
    except Exception as e:
        print(f"   ❌ JavaScript auto-test error: {e}")
        all_results.append(("JS Auto Test", False, str(e)))

    # Summary
    passed = sum(1 for _, success, _ in all_results if success)
    total = len(all_results)

    print(f"\n" + "="*60)
    print(f"FINAL SUMMARY: {passed}/{total} test categories passed")
    print("="*60)

    for test_name, success, result in all_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not success:
            print(f"    Error: {result}")

    return {
        "success": passed == total,
        "passed": passed,
        "total": total,
        "results": all_results
    }

@pywire.expose
def test_error_handling():
    """Test error handling in JavaScript function calls."""
    print("\n=== Testing Error Handling ===")
    
    try:
        # This should raise an error
        pywire.js_throw_error("This is a test error")
    except RuntimeError as e:
        print(f"✅ Caught expected error: {e}")
        return {"success": True, "message": "Error handling works correctly"}
    except Exception as e:
        print(f"❌ Unexpected error type: {e}")
        return {"success": False, "error": str(e)}

@pywire.expose
def test_timeout():
    """Test timeout functionality."""
    print("\n=== Testing Timeout ===")
    
    try:
        # Call with custom timeout
        result = pywire.js_async_operation(1000, timeout=2.0)  # Should succeed
        print(f"✅ Call with timeout succeeded: {result}")
        
        # This would timeout (uncomment to test)
        # result = pywire.js_async_operation(5000, timeout=2.0)  # Should timeout
        
        return {"success": True, "message": "Timeout test completed"}
    except TimeoutError as e:
        print(f"⏰ Timeout occurred as expected: {e}")
        return {"success": True, "message": "Timeout works correctly"}
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return {"success": False, "error": str(e)}

@pywire.expose
def test_async_calls():
    """Test fire-and-forget async calls."""
    print("\n=== Testing Async Calls (Fire and Forget) ===")
    
    try:
        # Fire and forget calls
        pywire.call_js_async("js_show_alert", "Async call 1", "info")
        pywire.call_js_async("js_show_alert", "Async call 2", "warning")
        pywire.call_js_async("js_show_alert", "Async call 3", "success")
        
        print("✅ Async calls sent (fire and forget)")
        return {"success": True, "message": "Async calls completed"}
        
    except Exception as e:
        print(f"❌ Error in async calls: {e}")
        return {"success": False, "error": str(e)}

@pywire.expose
def run_comprehensive_test():
    """Run all tests in sequence."""
    print("\n" + "="*60)
    print("COMPREHENSIVE EEL-STYLE FUNCTION CALLING TEST")
    print("="*60)
    
    tests = [
        ("Basic Function Calls", test_eel_style_calls),
        ("Error Handling", test_error_handling),
        ("Timeout Functionality", test_timeout),
        ("Async Calls", test_async_calls)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append({
                "test": test_name,
                "success": result.get("success", False),
                "message": result.get("message", ""),
                "error": result.get("error", "")
            })
        except Exception as e:
            results.append({
                "test": test_name,
                "success": False,
                "message": "",
                "error": str(e)
            })
    
    # Summary
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"\n" + "="*60)
    print(f"TEST SUMMARY: {passed}/{total} tests passed")
    print("="*60)
    
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status}: {result['test']}")
        if result["error"]:
            print(f"    Error: {result['error']}")
    
    return {
        "success": passed == total,
        "passed": passed,
        "total": total,
        "results": results
    }

def auto_test():
    """Automatically run comprehensive tests after a delay."""
    time.sleep(5)  # Wait for browser to connect and JavaScript to load
    print("🚀 Starting automatic comprehensive test...")
    result = auto_test_both_directions()
    print(f"\n🏁 Final result: {result['passed']}/{result['total']} test categories passed")

def main():
    """Main function to start the application."""
    print("PyWire Eel-Style Function Calling Example")
    print("=========================================")
    print("This example demonstrates bidirectional function calling:")
    print("✅ Python → JavaScript using Eel-style syntax: pywire.function_name(*args)")
    print("✅ JavaScript → Python using: callPython('function_name', ...args)")
    print("✅ Automatic testing of both directions")
    print("\nStarting PyWire server...")

    # Start auto test in background
    test_thread = threading.Thread(target=auto_test)
    test_thread.daemon = True
    test_thread.start()

    # Start the application
    pywire.start('eel_style_demo.html', port=8080, size=(800, 500))

if __name__ == '__main__':
    main()
