// PyWire Test Application JavaScript

// Test tracking
let testStats = {
    run: 0,
    passed: 0,
    failed: 0
};

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    updateConnectionStatus();
    // Only call setupEventListeners if it exists
    if (typeof setupEventListeners === 'function') {
        setupEventListeners();
    }
    // Only call showSection if the elements exist
    if (document.getElementById('basic')) {
        showSection('basic');
    }
});

// Connection status management
function updateConnectionStatus() {
    const statusElement = document.getElementById('connectionStatus');
    
    if (window.PyWire && PyWire.isConnected()) {
        statusElement.textContent = '✅ Connected to PyWire';
        statusElement.className = 'status connected';
    } else {
        statusElement.textContent = '❌ Disconnected';
        statusElement.className = 'status disconnected';
        
        // Try to reconnect
        setTimeout(updateConnectionStatus, 1000);
    }
}

// Section navigation
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.test-section').forEach(section => {
        section.classList.remove('active');
    });

    // Remove active class from all nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
    }

    // Activate corresponding nav button (only if event is available)
    if (typeof event !== 'undefined' && event.target) {
        event.target.classList.add('active');
    }
}

// Test result helpers
function logTest(testName, success, result) {
    testStats.run++;
    if (success) {
        testStats.passed++;
    } else {
        testStats.failed++;
    }
    
    updateTestSummary();
    console.log(`Test: ${testName}, Success: ${success}, Result:`, result);
}

function updateTestSummary() {
    document.getElementById('testsRun').textContent = testStats.run;
    document.getElementById('testsPassed').textContent = testStats.passed;
    document.getElementById('testsFailed').textContent = testStats.failed;
    
    const successRate = testStats.run > 0 ? Math.round((testStats.passed / testStats.run) * 100) : 0;
    document.getElementById('successRate').textContent = successRate + '%';
}

function showResult(elementId, result, success = true) {
    const element = document.getElementById(elementId);
    element.textContent = typeof result === 'object' ? JSON.stringify(result, null, 2) : result;
    element.style.background = success ? '#f0fff4' : '#fed7d7';
    element.style.borderLeft = success ? '4px solid #48bb78' : '4px solid #f56565';
}

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.getElementById('notifications').appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Exposed functions for Python to call
function showTestNotification(message, type) {
    showNotification(message, type);
}

function updateTestStatus(status) {
    showNotification(status, 'info');
}

// Event listeners setup
function setupEventListeners() {
    // Counter updates
    PyWire.on('counter_updated', function(data) {
        document.getElementById('counterValue').textContent = data.value;
        showNotification(`Counter updated to ${data.value}`, 'success');
    });
    
    // User events
    PyWire.on('user_added', function(user) {
        showNotification(`User added: ${user.name}`, 'success');
        testGetUsers(); // Refresh user list
    });
    
    PyWire.on('user_deleted', function(data) {
        showNotification(`User deleted: ${data.user.name}`, 'info');
        testGetUsers(); // Refresh user list
    });
    
    // Message events
    PyWire.on('new_message', function(message) {
        addMessageToList(message);
        showNotification(`New message from ${message.sender}`, 'info');
    });
    
    PyWire.on('system_message', function(message) {
        addMessageToList(message);
        showNotification('System message received', 'info');
    });
    
    // Monitoring events
    PyWire.on('monitoring_data', function(data) {
        updateMonitoringDisplay(data);
    });
    
    // Stress test events
    PyWire.on('stress_test_progress', function(data) {
        updateStressProgress(data);
    });
    
    PyWire.on('stress_test_complete', function(data) {
        showResult('stressResult', `Stress test completed!\nOperations: ${data.total_operations}\nDuration: ${data.duration.toFixed(2)}s\nOps/sec: ${data.ops_per_second.toFixed(0)}`, true);
        showNotification('Stress test completed!', 'success');
    });
}

// === BASIC TESTS ===

async function testHello() {
    try {
        const name = document.getElementById('helloName').value;
        const result = await eel.test_hello(name)();
        showResult('helloResult', result, true);
        logTest('Hello', true, result);
    } catch (error) {
        showResult('helloResult', `Error: ${error.message}`, false);
        logTest('Hello', false, error);
    }
}

async function testMath() {
    try {
        const a = document.getElementById('mathA').value;
        const b = document.getElementById('mathB').value;
        const result = await eel.test_math_operations(a, b)();
        showResult('mathResult', result, !result.error);
        logTest('Math Operations', !result.error, result);
    } catch (error) {
        showResult('mathResult', `Error: ${error.message}`, false);
        logTest('Math Operations', false, error);
    }
}

async function testDataTypes() {
    try {
        const result = await eel.test_data_types()();
        showResult('dataTypesResult', result, true);
        logTest('Data Types', true, result);
    } catch (error) {
        showResult('dataTypesResult', `Error: ${error.message}`, false);
        logTest('Data Types', false, error);
    }
}

// === STATE MANAGEMENT TESTS ===

async function testIncrement() {
    try {
        const result = await eel.test_increment_counter()();
        showResult('counterResult', `Counter incremented to: ${result}`, true);
        logTest('Increment Counter', true, result);
    } catch (error) {
        showResult('counterResult', `Error: ${error.message}`, false);
        logTest('Increment Counter', false, error);
    }
}

async function testGetCounter() {
    try {
        const result = await eel.test_get_counter()();
        showResult('counterResult', `Current counter value: ${result}`, true);
        document.getElementById('counterValue').textContent = result;
        logTest('Get Counter', true, result);
    } catch (error) {
        showResult('counterResult', `Error: ${error.message}`, false);
        logTest('Get Counter', false, error);
    }
}

async function testResetCounter() {
    try {
        const result = await eel.test_reset_counter()();
        showResult('counterResult', result, true);
        logTest('Reset Counter', true, result);
    } catch (error) {
        showResult('counterResult', `Error: ${error.message}`, false);
        logTest('Reset Counter', false, error);
    }
}

// === USER MANAGEMENT TESTS ===

async function testAddUser() {
    try {
        const name = document.getElementById('userName').value;
        const email = document.getElementById('userEmail').value;
        const age = document.getElementById('userAge').value;
        
        const result = await eel.test_add_user(name, email, age)();
        showResult('userResult', result, result.success);
        logTest('Add User', result.success, result);
        
        if (result.success) {
            // Clear form
            document.getElementById('userName').value = '';
            document.getElementById('userEmail').value = '';
            document.getElementById('userAge').value = '';
        }
    } catch (error) {
        showResult('userResult', `Error: ${error.message}`, false);
        logTest('Add User', false, error);
    }
}

async function testGetUsers() {
    try {
        const result = await eel.test_get_users()();
        showResult('userResult', `Loaded ${result.count} users`, true);
        
        // Display users in list
        const userList = document.getElementById('userList');
        userList.innerHTML = '';
        
        result.users.forEach(user => {
            const userDiv = document.createElement('div');
            userDiv.className = 'user-item';
            userDiv.innerHTML = `
                <strong>${user.name}</strong> (${user.email})
                ${user.age ? `, Age: ${user.age}` : ''}
                <button onclick="deleteUser(${user.id})" style="margin-left: 10px; background: #f56565;">Delete</button>
            `;
            userList.appendChild(userDiv);
        });
        
        logTest('Get Users', true, result);
    } catch (error) {
        showResult('userResult', `Error: ${error.message}`, false);
        logTest('Get Users', false, error);
    }
}

async function deleteUser(userId) {
    try {
        const result = await eel.test_delete_user(userId)();
        showResult('userResult', result.success ? 'User deleted successfully' : result.error, result.success);
        logTest('Delete User', result.success, result);
    } catch (error) {
        showResult('userResult', `Error: ${error.message}`, false);
        logTest('Delete User', false, error);
    }
}

function clearUserList() {
    document.getElementById('userList').innerHTML = '';
    showResult('userResult', 'User list cleared', true);
}

// === REAL-TIME TESTS ===

async function testSendMessage() {
    try {
        const message = document.getElementById('messageText').value;
        const sender = document.getElementById('messageSender').value;
        
        if (!message.trim()) {
            showResult('messageResult', 'Please enter a message', false);
            return;
        }
        
        const result = await eel.test_send_message(message, sender)();
        showResult('messageResult', result, result.success);
        logTest('Send Message', result.success, result);
        
        if (result.success) {
            document.getElementById('messageText').value = '';
        }
    } catch (error) {
        showResult('messageResult', `Error: ${error.message}`, false);
        logTest('Send Message', false, error);
    }
}

async function testGetMessages() {
    try {
        const result = await eel.test_get_messages()();
        showResult('messageResult', `Loaded ${result.showing} of ${result.total} messages`, true);
        
        // Display messages
        const messageList = document.getElementById('messageList');
        messageList.innerHTML = '';
        
        result.messages.forEach(msg => {
            addMessageToList(msg);
        });
        
        logTest('Get Messages', true, result);
    } catch (error) {
        showResult('messageResult', `Error: ${error.message}`, false);
        logTest('Get Messages', false, error);
    }
}

async function testSystemMessage() {
    try {
        const result = await eel.test_broadcast_system_message('This is a system test message')();
        showResult('messageResult', result, result.success);
        logTest('System Message', result.success, result);
    } catch (error) {
        showResult('messageResult', `Error: ${error.message}`, false);
        logTest('System Message', false, error);
    }
}

function addMessageToList(message) {
    const messageList = document.getElementById('messageList');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${message.type}`;
    msgDiv.innerHTML = `
        <strong>${message.sender}:</strong> ${message.text}
        <small>(${new Date(message.timestamp).toLocaleTimeString()})</small>
    `;
    messageList.appendChild(msgDiv);
    messageList.scrollTop = messageList.scrollHeight;
}

// === MONITORING TESTS ===

async function testStartMonitoring() {
    try {
        const result = await eel.test_start_monitoring()();
        showResult('monitoringResult', result, result.success);
        logTest('Start Monitoring', result.success, result);
    } catch (error) {
        showResult('monitoringResult', `Error: ${error.message}`, false);
        logTest('Start Monitoring', false, error);
    }
}

async function testStopMonitoring() {
    try {
        const result = await eel.test_stop_monitoring()();
        showResult('monitoringResult', result, result.success);
        logTest('Stop Monitoring', result.success, result);
    } catch (error) {
        showResult('monitoringResult', `Error: ${error.message}`, false);
        logTest('Stop Monitoring', false, error);
    }
}

function updateMonitoringDisplay(data) {
    // Update progress bars
    document.getElementById('cpuBar').style.width = data.cpu + '%';
    document.getElementById('cpuValue').textContent = data.cpu.toFixed(1) + '%';
    
    document.getElementById('memoryBar').style.width = data.memory + '%';
    document.getElementById('memoryValue').textContent = data.memory.toFixed(1) + '%';
    
    document.getElementById('diskBar').style.width = data.disk + '%';
    document.getElementById('diskValue').textContent = data.disk.toFixed(1) + '%';
}

// === PERFORMANCE TESTS ===

async function testFibonacci() {
    try {
        const n = document.getElementById('fibNumber').value;
        const result = await eel.test_fibonacci_performance(n)();
        showResult('fibResult', result, !result.error);
        logTest('Fibonacci Performance', !result.error, result);
    } catch (error) {
        showResult('fibResult', `Error: ${error.message}`, false);
        logTest('Fibonacci Performance', false, error);
    }
}

async function testStressTest() {
    try {
        const duration = document.getElementById('stressDuration').value;
        const result = await eel.test_stress_test(duration)();
        showResult('stressResult', result, result.success);
        logTest('Stress Test', result.success, result);
    } catch (error) {
        showResult('stressResult', `Error: ${error.message}`, false);
        logTest('Stress Test', false, error);
    }
}

async function testStopStressTest() {
    try {
        const result = await eel.test_stop_stress_test()();
        showResult('stressResult', result, result.success);
        logTest('Stop Stress Test', result.success, result);
    } catch (error) {
        showResult('stressResult', `Error: ${error.message}`, false);
        logTest('Stop Stress Test', false, error);
    }
}

function updateStressProgress(data) {
    document.getElementById('stressProgressBar').style.width = data.progress + '%';
    document.getElementById('stressStats').innerHTML = `
        Progress: ${data.progress.toFixed(1)}%<br>
        Operations: ${data.operations}<br>
        Elapsed: ${data.elapsed.toFixed(1)}s
    `;
}

// === SYSTEM INFO TESTS ===

async function testSystemInfo() {
    try {
        const result = await eel.test_get_system_info()();
        showResult('systemResult', result, true);
        logTest('System Info', true, result);
    } catch (error) {
        showResult('systemResult', `Error: ${error.message}`, false);
        logTest('System Info', false, error);
    }
}

async function testSaveData() {
    try {
        const result = await eel.test_save_test_data()();
        showResult('systemResult', result, result.success);
        logTest('Save Data', result.success, result);
    } catch (error) {
        showResult('systemResult', `Error: ${error.message}`, false);
        logTest('Save Data', false, error);
    }
}

async function testCallJavaScript() {
    try {
        const result = await eel.test_call_javascript()();
        showResult('systemResult', result, result.success);
        logTest('Call JavaScript', result.success, result);
    } catch (error) {
        showResult('systemResult', `Error: ${error.message}`, false);
        logTest('Call JavaScript', false, error);
    }
}

// === ERROR HANDLING TESTS ===

async function testError(errorType) {
    try {
        const result = await eel.test_error_handling(errorType)();
        showResult('errorResult', result, result.success !== false);
        logTest(`Error Test (${errorType})`, result.success !== false, result);
    } catch (error) {
        showResult('errorResult', `Caught error: ${error.message}`, true);
        logTest(`Error Test (${errorType})`, true, error.message);
    }
}

// === RUN ALL TESTS ===

async function runAllTests() {
    showNotification('Running all tests...', 'info');
    
    // Reset stats
    testStats = { run: 0, passed: 0, failed: 0 };
    updateTestSummary();
    
    // Run all tests with delays
    const tests = [
        () => testHello(),
        () => testMath(),
        () => testDataTypes(),
        () => testIncrement(),
        () => testGetCounter(),
        () => testAddUser(),
        () => testGetUsers(),
        () => testSendMessage(),
        () => testSystemInfo(),
        () => testError('none'),
        () => testFibonacci()
    ];
    
    for (let i = 0; i < tests.length; i++) {
        await tests[i]();
        await new Promise(resolve => setTimeout(resolve, 500)); // Wait between tests
    }
    
    showNotification(`All tests completed! ${testStats.passed}/${testStats.run} passed`, 'success');
}

// === JAVASCRIPT FUNCTIONS THAT CAN BE CALLED FROM PYTHON ===

// Function to expose all JavaScript functions to Python
function exposeJavaScriptFunctions() {
    console.log('Exposing JavaScript functions to Python...');

    // Check if exposePyWire is available
    if (typeof exposePyWire !== 'function') {
        console.error('exposePyWire function not available');
        return;
    }

    try {
        exposePyWire('js_greet', function(name) {
            return `Hello ${name} from JavaScript!`;
        });

        exposePyWire('js_add_numbers', function(a, b) {
            return a + b;
        });

        exposePyWire('js_get_current_time', function() {
            return new Date().toISOString();
        });

        exposePyWire('js_calculate_factorial', function(n) {
            if (n <= 1) return 1;
            return n * arguments.callee(n - 1);
        });

        exposePyWire('js_process_array', function(arr) {
            return {
                original: arr,
                length: arr.length,
                sum: arr.reduce((a, b) => a + b, 0),
                average: arr.reduce((a, b) => a + b, 0) / arr.length,
                max: Math.max(...arr),
                min: Math.min(...arr)
            };
        });

        exposePyWire('js_get_browser_info', function() {
            return {
                userAgent: navigator.userAgent,
                language: navigator.language,
                platform: navigator.platform,
                cookieEnabled: navigator.cookieEnabled,
                onLine: navigator.onLine,
                screenWidth: screen.width,
                screenHeight: screen.height,
                windowWidth: window.innerWidth,
                windowHeight: window.innerHeight
            };
        });

        exposePyWire('js_manipulate_dom', function(elementId, text, color) {
            const element = document.getElementById(elementId);
            if (element) {
                element.textContent = text;
                if (color) {
                    element.style.color = color;
                }
                return `Updated element ${elementId} with text: ${text}`;
            } else {
                throw new Error(`Element with id '${elementId}' not found`);
            }
        });

        exposePyWire('js_show_alert', function(message, type = 'info') {
            if (typeof showNotification === 'function') {
                showNotification(message, type);
            } else {
                console.log(`Alert: ${message} (${type})`);
            }
            return `Alert shown: ${message}`;
        });

        exposePyWire('js_async_operation', async function(delay = 1000) {
            await new Promise(resolve => setTimeout(resolve, delay));
            return `Async operation completed after ${delay}ms`;
        });

        exposePyWire('js_throw_error', function(message) {
            throw new Error(message || 'Test error from JavaScript');
        });

        console.log('✅ All JavaScript functions exposed successfully');

    } catch (error) {
        console.error('Error exposing JavaScript functions:', error);
    }
}

// Call the function when the page loads and PyWire is ready
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit for PyWire to be ready, then expose functions
    setTimeout(exposeJavaScriptFunctions, 500);
});
