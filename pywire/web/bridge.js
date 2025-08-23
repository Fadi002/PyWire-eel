class PyWireBridge {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.pendingCalls = new Map();
        this.callCounter = 0;
        this.exposedFunctions = new Map();
        this.eventHandlers = new Map();
        this.wsPort = null;
        this.detectAndConnect();
    }

    async detectAndConnect() {
        const commonPorts = [8001, 8002, 8003, 8004, 8005];
        for (const port of commonPorts) {
            try {
                await this.connect(port);
                if (this.connected) {
                    this.wsPort = port;
                    break;
                }
            } catch (error) {
                continue;
            }
        }
        if (!this.connected) {
            this.scheduleReconnect();
        }
    }

    connect(port = 8001) {
        return new Promise((resolve, reject) => {
            try {
                this.socket = new WebSocket(`ws://localhost:${port}`);
                this.socket.onopen = () => {
                    this.connected = true;
                    this.reconnectAttempts = 0;
                    resolve();
                };
                this.socket.onmessage = (event) => {
                    this.handleMessage(event.data);
                };
                this.socket.onclose = () => {
                    this.connected = false;
                    this.scheduleReconnect();
                };
                this.socket.onerror = (error) => {
                    reject(error);
                };
                setTimeout(() => {
                    if (!this.connected) {
                        this.socket.close();
                        reject(new Error('Connection timeout'));
                    }
                }, 5000);
            } catch (error) {
                reject(error);
            }
        });
    }

    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
            setTimeout(() => {
                if (this.wsPort) {
                    this.connect(this.wsPort);
                } else {
                    this.detectAndConnect();
                }
            }, delay);
        }
    }

    handleMessage(data) {
        try {
            const message = JSON.parse(data);
            switch (message.type) {
                case 'call':
                    this.handlePythonCall(message);
                    break;
                case 'response':
                    this.handlePythonResponse(message);
                    break;
                case 'event':
                    this.handlePythonEvent(message);
                    break;
                default:
                    this.handleLegacyMessage(message);
            }
        } catch (error) {
            console.error('Error parsing message:', error);
        }
    }

    handlePythonCall(message) {
        const { func, args, call_id } = message;
        if (this.exposedFunctions.has(func)) {
            try {
                const result = this.exposedFunctions.get(func)(...(args || []));
                if (result instanceof Promise) {
                    result
                        .then(res => this.sendResponse(call_id, res))
                        .catch(err => this.sendError(call_id, err.message));
                } else {
                    this.sendResponse(call_id, result);
                }
            } catch (error) {
                this.sendError(call_id, error.message);
            }
        } else {
            this.sendError(call_id, `Function '${func}' not found`);
        }
    }

    handlePythonResponse(message) {
        const { call_id, result, error } = message;
        if (this.pendingCalls.has(call_id)) {
            const { resolve, reject } = this.pendingCalls.get(call_id);
            this.pendingCalls.delete(call_id);
            if (error) {
                reject(new Error(error));
            } else {
                resolve(result);
            }
        }
    }

    handlePythonEvent(message) {
        const { event, data } = message;
        if (this.eventHandlers.has(event)) {
            const handlers = this.eventHandlers.get(event);
            handlers.forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`Error in event handler for '${event}':`, error);
                }
            });
        }
    }

    handleLegacyMessage(message) {
        if (message.func && message.args !== undefined) {
            this.handlePythonCall({
                func: message.func,
                args: message.args,
                call_id: null
            });
        }
    }

    sendResponse(call_id, result) {
        if (call_id) {
            this.sendMessage({
                type: 'response',
                call_id: call_id,
                result: result
            });
        }
    }

    sendError(call_id, error) {
        if (call_id) {
            this.sendMessage({
                type: 'response',
                call_id: call_id,
                error: error
            });
        }
    }

    sendMessage(message) {
        if (this.connected && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(message));
            return true;
        }
        return false;
    }

    generateCallId() {
        return `js_call_${Date.now()}_${++this.callCounter}`;
    }

    async callPython(func, ...args) {
        if (!this.connected) {
            throw new Error('PyWire not connected');
        }
        return new Promise((resolve, reject) => {
            const call_id = this.generateCallId();
            this.pendingCalls.set(call_id, { resolve, reject });
            setTimeout(() => {
                if (this.pendingCalls.has(call_id)) {
                    this.pendingCalls.delete(call_id);
                    reject(new Error('Python call timeout'));
                }
            }, 30000);
            const success = this.sendMessage({
                type: 'call',
                func: func,
                args: args,
                call_id: call_id
            });
            if (!success) {
                this.pendingCalls.delete(call_id);
                reject(new Error('Failed to send message'));
            }
        });
    }

    expose(func, name = null) {
        if (typeof func === 'string' && typeof name === 'function') {
            const funcName = func;
            this.exposedFunctions.set(funcName, name);
            return name;
        }
        const funcObj = func;
        const funcName = (typeof name === 'string' && name) || (funcObj && funcObj.name);
        if (!funcName) {
            throw new Error('Function must have a name or provide name parameter');
        }
        this.exposedFunctions.set(funcName, funcObj);
        return funcObj;
    }

    emitEvent(eventName, data = null) {
        return this.sendMessage({
            type: 'event',
            event: eventName,
            data: data
        });
    }

    onEvent(eventName, handler) {
        if (!this.eventHandlers.has(eventName)) {
            this.eventHandlers.set(eventName, []);
        }
        this.eventHandlers.get(eventName).push(handler);
    }

    offEvent(eventName, handler = null) {
        if (this.eventHandlers.has(eventName)) {
            if (handler) {
                const handlers = this.eventHandlers.get(eventName);
                const index = handlers.indexOf(handler);
                if (index > -1) {
                    handlers.splice(index, 1);
                }
            } else {
                this.eventHandlers.delete(eventName);
            }
        }
    }

    isConnected() {
        return this.connected;
    }

    getExposedFunctions() {
        return Array.from(this.exposedFunctions.keys());
    }

    reconnect() {
        if (this.socket) {
            this.socket.close();
        }
        this.reconnectAttempts = 0;
        this.detectAndConnect();
    }
}

const PyWire = new PyWireBridge();
window.PyWire = PyWire;
window.callPython = PyWire.callPython.bind(PyWire);
window.exposePyWire = PyWire.expose.bind(PyWire);

PyWire.on = PyWire.onEvent.bind(PyWire);
PyWire.off = PyWire.offEvent.bind(PyWire);
PyWire.emit = PyWire.emitEvent.bind(PyWire);

window.pyWire = {
    call: PyWire.callPython.bind(PyWire),
    expose: PyWire.expose.bind(PyWire),
    emit: PyWire.emitEvent.bind(PyWire),
    on: PyWire.onEvent.bind(PyWire),
    off: PyWire.offEvent.bind(PyWire),
    isConnected: PyWire.isConnected.bind(PyWire),
    reconnect: PyWire.reconnect.bind(PyWire)
};

window.eel = new Proxy({}, {
    get: function(_, prop) {
        if (prop === 'expose') {
            return PyWire.expose.bind(PyWire);
        }
        if (prop === '_call') {
            return PyWire.callPython.bind(PyWire);
        }
        return function(...args) {
            return function() {
                return PyWire.callPython(prop, ...args);
            };
        };
    }
});
