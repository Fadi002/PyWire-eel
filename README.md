<!-- thanks to ChatGPT for the markdown xD -->
# PyWire 🚀

PyWire is a lightweight Python library that allows you to create simple desktop GUI applications using HTML, CSS, and JavaScript, while giving full access to Python’s functionality and libraries. It's designed to make cross-platform desktop app development with web technologies a breeze! ✨

## 💡 Inspiration

PyWire is heavily inspired by and aims to be compatible with the excellent [Eel project](https://github.com/python-eel/Eel). We've taken the core ideas and built upon them to provide a robust and easy-to-use solution for integrating Python with web frontends. Our goal is to offer a similar developer experience with additional features and optimizations. 🐍🌐

## 📦 Installation

You can install PyWire directly from PyPI:

```bash
pip install pywire-eel
```

Or from github
```bash
pip install git+https://github.com/Fadi002/PyWire
```

## 🌟 Features

- **Seamless Python-JavaScript Interoperability**: Call Python functions from JavaScript and vice-versa with ease. 🔄
- **Cross-Platform Compatibility**: Build apps that run on Windows, macOS, and Linux. 💻
- **Web Technologies**: Leverage your existing knowledge of HTML, CSS, and JavaScript to build beautiful UIs. 🎨
- **Lightweight & Fast**: Designed for performance and minimal overhead. ⚡
- **Eel-compatible API**: Familiar API for developers coming from the Eel ecosystem. 🤝

## 🚀 Getting Started

Here's a quick example to get you started:

```python
import pywire

@pywire.expose
def say_hello(name):
    print(f"Hello from Python: {name}!")
    return f"Hello, {name}! This is from Python."

pywire.init('web') # 'web' is the folder containing your HTML, CSS, JS files
pywire.start('index.html') # 'index.html' is your main HTML file
```

And in your `web/index.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <script src="bridge.js"></script> <!-- This must be included in your html -->
    <title>PyWire App</title>
    <script type="text/javascript" src="/pywire.js"></script>
    <script type="text/javascript">
        async function callPython() {
            let result = await pywire.say_hello("World");
            document.getElementById('output').innerText = result;
        }
    </script>
</head>
<body>
    <h1>Welcome to PyWire!</h1>
    <button onclick="callPython()">Call Python Function</button>
    <p id="output"></p>
</body>
</html>
```

## 🤝 Contributing

We welcome contributions! If you'd like to contribute, please fork the repository and create a pull request. For major changes, please open an issue first to discuss what you would like to change. 💖

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. ©️


