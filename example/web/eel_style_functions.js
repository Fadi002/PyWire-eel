// Eel-Style Function Calling JavaScript Functions
// This file contains JavaScript functions that can be called from Python

console.log('Loading Eel-Style JavaScript functions...');

// Wait for PyWire to be ready before exposing functions
function exposeAllFunctions() {
    console.log('Exposing JavaScript functions to Python...');
    
    if (typeof exposePyWire !== 'function') {
        console.error('exposePyWire function not available');
        setTimeout(exposeAllFunctions, 500); // Retry after 500ms
        return;
    }
    
    try {
        // Basic greeting function
        exposePyWire('js_greet', function(name) {
            console.log(`js_greet called with: ${name}`);
            return `Hello ${name} from JavaScript! 🌐`;
        });

        // Math operations
        exposePyWire('js_add_numbers', function(a, b) {
            console.log(`js_add_numbers called with: ${a}, ${b}`);
            const result = a + b;
            return result;
        });

        // Get current time
        exposePyWire('js_get_current_time', function() {
            console.log('js_get_current_time called');
            return new Date().toISOString();
        });

        // Calculate factorial
        exposePyWire('js_calculate_factorial', function(n) {
            console.log(`js_calculate_factorial called with: ${n}`);
            if (n <= 1) return 1;
            let result = 1;
            for (let i = 2; i <= n; i++) {
                result *= i;
            }
            return result;
        });

        // Process array
        exposePyWire('js_process_array', function(arr) {
            console.log(`js_process_array called with:`, arr);
            if (!Array.isArray(arr)) {
                throw new Error('Input must be an array');
            }
            
            const sum = arr.reduce((a, b) => a + b, 0);
            return {
                original: arr,
                length: arr.length,
                sum: sum,
                average: sum / arr.length,
                max: Math.max(...arr),
                min: Math.min(...arr)
            };
        });

        // Get browser info
        exposePyWire('js_get_browser_info', function() {
            console.log('js_get_browser_info called');
            return {
                userAgent: navigator.userAgent,
                language: navigator.language,
                platform: navigator.platform || 'Unknown',
                cookieEnabled: navigator.cookieEnabled,
                onLine: navigator.onLine,
                screenWidth: screen.width,
                screenHeight: screen.height,
                windowWidth: window.innerWidth,
                windowHeight: window.innerHeight,
                timestamp: new Date().toISOString()
            };
        });

        // DOM manipulation
        exposePyWire('js_manipulate_dom', function(elementId, text, color) {
            console.log(`js_manipulate_dom called with: ${elementId}, ${text}, ${color}`);
            const element = document.getElementById(elementId);
            if (element) {
                element.textContent = text;
                if (color) {
                    element.style.color = color;
                }
                return `Updated element ${elementId} with text: ${text}`;
            } else {
                // Create the element if it doesn't exist
                const newElement = document.createElement('div');
                newElement.id = elementId;
                newElement.textContent = text;
                if (color) {
                    newElement.style.color = color;
                }
                document.body.appendChild(newElement);
                return `Created and updated element ${elementId} with text: ${text}`;
            }
        });

        // Show alert/notification
        exposePyWire('js_show_alert', function(message, type = 'info') {
            console.log(`js_show_alert called with: ${message}, ${type}`);
            
            // Try to use showNotification if available, otherwise use console
            if (typeof showNotification === 'function') {
                showNotification(message, type);
            } else {
                console.log(`Alert (${type}): ${message}`);
            }
            
            return `Alert shown: ${message} (${type})`;
        });

        // Async operation
        exposePyWire('js_async_operation', async function(delay = 1000) {
            console.log(`js_async_operation called with delay: ${delay}ms`);
            await new Promise(resolve => setTimeout(resolve, delay));
            return `Async operation completed after ${delay}ms`;
        });

        // Test error throwing
        exposePyWire('js_throw_error', function(message) {
            console.log(`js_throw_error called with: ${message}`);
            throw new Error(message || 'Test error from JavaScript');
        });

        // Auto test function that calls Python functions
        exposePyWire('js_auto_test_python_calls', async function() {
            console.log('js_auto_test_python_calls: Starting automatic test of Python functions...');
            
            const results = [];
            
            try {
                // Test 1: Call python_greet
                console.log('Testing python_greet...');
                const greetResult = await callPython('python_greet', 'JavaScript');
                console.log('python_greet result:', greetResult);
                results.push({test: 'python_greet', success: true, result: greetResult});
                
                // Test 2: Call python_calculate
                console.log('Testing python_calculate...');
                const calcResult = await callPython('python_calculate', 'multiply', 6, 7);
                console.log('python_calculate result:', calcResult);
                results.push({test: 'python_calculate', success: true, result: calcResult});
                
                // Test 3: Call python_get_system_info
                console.log('Testing python_get_system_info...');
                const sysResult = await callPython('python_get_system_info');
                console.log('python_get_system_info result:', sysResult);
                results.push({test: 'python_get_system_info', success: true, result: sysResult});
                
                // Test 4: Call python_process_data
                console.log('Testing python_process_data...');
                const dataResult = await callPython('python_process_data', {
                    numbers: [10, 20, 30, 40, 50],
                    operation: 'average'
                });
                console.log('python_process_data result:', dataResult);
                results.push({test: 'python_process_data', success: true, result: dataResult});
                
                const passed = results.filter(r => r.success).length;
                const total = results.length;
                
                console.log(`JavaScript auto-test completed: ${passed}/${total} tests passed`);
                
                return {
                    success: passed === total,
                    passed: passed,
                    total: total,
                    results: results,
                    message: `JavaScript to Python auto-test: ${passed}/${total} passed`
                };
                
            } catch (error) {
                console.error('Error in js_auto_test_python_calls:', error);
                return {
                    success: false,
                    error: error.message,
                    results: results,
                    message: 'JavaScript to Python auto-test failed'
                };
            }
        });
        
        console.log('✅ All JavaScript functions exposed successfully!');
        
        // Show a notification that functions are ready
        if (typeof showNotification === 'function') {
            showNotification('JavaScript functions ready for Python calls!', 'success');
        }
        
    } catch (error) {
        console.error('Error exposing JavaScript functions:', error);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, waiting for PyWire...');
    // Wait a bit for PyWire to be ready, then expose functions
    setTimeout(exposeAllFunctions, 1000);
});

// Also try to expose functions immediately if PyWire is already available
if (typeof exposePyWire === 'function') {
    exposeAllFunctions();
}
