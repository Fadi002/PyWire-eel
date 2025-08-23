<!-- thanks to ChatGPT for the markdown xD -->
# PyWire API Usage Guide 📚

This document provides a detailed guide on how to use the PyWire API to build interactive desktop applications with Python and web technologies. PyWire aims for Eel-compatibility, making it easy for developers familiar with Eel to transition. 🚀

## Core Concepts ✨

PyWire facilitates communication between your Python backend and your web-based frontend (HTML, CSS, JavaScript). It allows you to:

- **Expose Python functions to JavaScript**: Call Python functions directly from your frontend JavaScript code.
- **Call JavaScript functions from Python**: Execute JavaScript functions from your Python backend.
- **Manage application lifecycle**: Initialize, start, and stop your PyWire application.

## API Reference 📖

### `pywire.init(web_folder)`

Initializes the PyWire application, specifying the folder where your web assets (HTML, CSS, JavaScript) are located.

- `web_folder` (str): The path to the directory containing your web files. This path is relative to where your Python script is run.

**Example:**

```python
import pywire

pywire.init("web") # Assuming your web files are in a folder named 'web'
```

### `pywire.expose(name_or_function=None)`

Decorator or function to expose a Python function to the JavaScript frontend. Once exposed, the function can be called from JavaScript using `pywire.function_name(...)`.

- `name_or_function` (callable or str, optional): The Python function to expose, or a string representing the name to expose the function as in JavaScript. If `None`, it's used as a decorator.

**Examples:**

**As a decorator:**

```python
import pywire

@pywire.expose
def greet(name):
    return f"Hello, {name}!"
```

**As a function:**

```python
import pywire

def add_numbers(a, b):
    return a + b

pywire.expose(add_numbers) # Exposes as 'add_numbers' in JavaScript

def subtract_numbers(a, b):
    return a - b

pywire.expose(name="subtract", function=subtract_numbers) # Exposes as 'subtract' in JavaScript
```

### `pywire.start(page='index.html', mode=None, host='localhost', port=8000, size=None, position=None)`

Starts the PyWire application, launching the web frontend in a browser or a desktop window.

- `page` (str, optional): The initial HTML page to load. Defaults to `index.html`.
- `mode` (str, optional): The browser mode to use (e.g., `'chrome'`, `'edge'`, `'electron'`). If `None`, PyWire tries to find an available browser.
- `host` (str, optional): The host address for the web server. Defaults to `localhost`.
- `port` (int, optional): The port for the web server. Defaults to `8000`.
- `size` (tuple, optional): A tuple `(width, height)` to set the initial window size.
- `position` (tuple, optional): A tuple `(x, y)` to set the initial window position.

**Example:**

```python
import pywire

pywire.init("web")
pywire.start(page="main.html", size=(800, 600), port=8080)
```

### `pywire.sleep(seconds)`

Pauses the execution of the Python script for a specified number of seconds. This is a utility function often used in examples.

- `seconds` (int or float): The number of seconds to sleep.

**Example:**

```python
import pywire
import time

print("Waiting for 5 seconds...")
pywire.sleep(5)
print("Done waiting!")
```

### `pywire.call_js(function_name, *args)`

Calls a JavaScript function from Python. The JavaScript function must be defined in the global scope of your web page.

- `function_name` (str): The name of the JavaScript function to call.
- `*args`: Arguments to pass to the JavaScript function.

**Example (Python):**

```python
import pywire

# Assuming 'displayMessage' is a JavaScript function in your frontend
pywire.call_js("displayMessage", "Message from Python!")
```

**Example (JavaScript - in `index.html` or linked JS file):**

```javascript
function displayMessage(message) {
    alert(message);
}
```

### `pywire.call_js_async(function_name, *args)`

Asynchronously calls a JavaScript function from Python. This is useful for non-blocking calls where you don't need an immediate return value.

- `function_name` (str): The name of the JavaScript function to call.
- `*args`: Arguments to pass to the JavaScript function.

**Example (Python):**

```python
import pywire

pywire.call_js_async("updateUI", {"status": "loading", "progress": 50})
```

### `pywire.emit_event(event_name, *args)`

Emits a custom event that can be listened to by JavaScript or Python functions.

- `event_name` (str): The name of the event to emit.
- `*args`: Data to pass along with the event.

**Example (Python):**

```python
import pywire

pywire.emit_event("data_updated", {"new_value": 123})
```

**Example (JavaScript):**

```javascript
pywire.on_event("data_updated", (data) => {
    console.log("Data updated event received:", data);
});
```

### `pywire.on_event(event_name, handler_function)`

Registers a handler function to be called when a specific event is emitted.

- `event_name` (str): The name of the event to listen for.
- `handler_function` (callable): The Python function to call when the event is emitted.

**Example (Python):**

```python
import pywire

def handle_custom_event(data):
    print(f"Custom event received with data: {data}")

pywire.on_event("custom_event", handle_custom_event)

# Later, in your application logic or from JavaScript:
pywire.emit_event("custom_event", {"status": "completed"})
```

### `pywire.stop()`

Stops the running PyWire application.

**Example:**

```python
import pywire
import time

pywire.init("web")
pywire.start(block=False) # Start non-blocking
time.sleep(10) # Run for 10 seconds
pywire.stop()
```

### `pywire.get_exposed_functions()`

Returns a list of names of all Python functions currently exposed to the JavaScript frontend.

**Example:**

```python
import pywire

@pywire.expose
def func1(): pass

@pywire.expose
def func2(): pass

print(pywire.get_exposed_functions())
# Expected output: ['func1', 'func2'] (order may vary)
```

### `pywire.set_custom_browser(browser_path)`

Sets a custom path to a browser executable to be used by PyWire.

- `browser_path` (str): The absolute path to the browser executable.

**Example:**

```python
import pywire

pywire.set_custom_browser("/usr/bin/google-chrome")
```

### `pywire.get_browser_info()`

Returns information about the browser currently being used by PyWire.

**Example:**

```python
import pywire

info = pywire.get_browser_info()
print(f"Browser Name: {info.get("name")}")
print(f"Browser Version: {info.get("version")}")
```

## JavaScript Integration 🌐

PyWire injects a `pywire.js` bridge file into your web pages. You **must** include this script in your HTML files for communication to work:

```html
<script type="text/javascript" src="/pywire.js"></script>
```

After including `pywire.js`, you can call exposed Python functions directly:

```javascript
// Call an exposed Python function 'my_python_function'
async function callMyPythonFunction() {
    let result = await pywire.my_python_function("some_argument");
    console.log("Result from Python:", result);
}

// Listen for events emitted from Python
pywire.on_event("python_event", (data) => {
    console.log("Event from Python received:", data);
});
```

This guide covers the primary functionalities of PyWire. For more advanced use cases and examples, please refer to the `example/` directory in the PyWire project. 💡


