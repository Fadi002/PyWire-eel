"""
PyWire Browser Control and Management
Handles controlled browser launching with app mode, temporary profiles, and lifecycle management.
Similar to Python Eel's browser control.
"""

import os
import sys
import subprocess
import platform
import webbrowser
import tempfile
import shutil
import atexit
import signal
import threading
import time
from typing import Optional, Dict, Any, List
from .utils import Logger


class BrowserDetector:
    """Detects available browsers and their capabilities."""

    def __init__(self):
        self.logger = Logger("Browser")
        self.system = platform.system().lower()
        self.detected_browsers = {}
        self.custom_browser_path = None
        self._detect_browsers()

    def set_custom_browser_path(self, path: str, browser_type: str = "custom"):
        """Set a custom browser path."""
        if os.path.isfile(path):
            self.custom_browser_path = path
            self.detected_browsers[browser_type] = {
                'path': path,
                'name': browser_type.title(),
                'supports_app_mode': True,
                'supports_kiosk': True
            }
            self.logger.info(f"Custom browser set: {path}")
            return True
        else:
            self.logger.error(f"Custom browser path not found: {path}")
            return False

    def _detect_browsers(self):
        """Detect available browsers on the system."""
        self.detected_browsers = {
            'chrome': self._detect_chrome(),
            'chromium': self._detect_chromium(),
            'brave': self._detect_brave(),
            'edge': self._detect_edge(),
            'firefox': self._detect_firefox(),
            'safari': self._detect_safari() if self.system == 'darwin' else None
        }

        # Filter out None values
        self.detected_browsers = {k: v for k, v in self.detected_browsers.items() if v}

        self.logger.info(f"Detected browsers: {list(self.detected_browsers.keys())}")
    
    def _detect_chrome(self) -> Optional[Dict[str, Any]]:
        """Detect Google Chrome."""
        chrome_paths = {
            'windows': [
                r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
                os.path.expanduser(r'~\AppData\Local\Google\Chrome\Application\chrome.exe')
            ],
            'darwin': [
                '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
            ],
            'linux': [
                '/usr/bin/google-chrome',
                '/usr/bin/google-chrome-stable',
                '/usr/bin/chromium-browser',
                '/snap/bin/chromium'
            ]
        }
        
        paths = chrome_paths.get(self.system, [])
        for path in paths:
            if os.path.exists(path):
                return {
                    'name': 'Google Chrome',
                    'path': path,
                    'supports_app_mode': True,
                    'supports_kiosk': True,
                    'browser_type': 'chrome'
                }
        
        # Try to find via webbrowser module
        try:
            chrome = webbrowser.get('chrome')
            return {
                'name': 'Google Chrome',
                'path': None,
                'browser_obj': chrome,
                'supports_app_mode': True,
                'supports_kiosk': True,
                'browser_type': 'chrome'
            }
        except webbrowser.Error:
            pass
        
        return None

    def _detect_chromium(self) -> Optional[Dict[str, Any]]:
        """Detect Chromium browser."""
        chromium_paths = {
            'windows': [
                r'C:\Program Files\Chromium\Application\chrome.exe',
                r'C:\Program Files (x86)\Chromium\Application\chrome.exe',
                os.path.expanduser(r'~\AppData\Local\Chromium\Application\chrome.exe'),
                os.path.expanduser(r'~\AppData\Local\Chromium\chrome.exe'),
                r'C:\Users\Public\Desktop\Chromium.lnk'
            ],
            'darwin': [
                '/Applications/Chromium.app/Contents/MacOS/Chromium',
                '/usr/local/bin/chromium',
                '/opt/homebrew/bin/chromium'
            ],
            'linux': [
                '/usr/bin/chromium',
                '/usr/bin/chromium-browser',
                '/snap/bin/chromium',
                '/usr/local/bin/chromium',
                '/opt/chromium/chromium',
                '/usr/bin/chromium-dev'
            ]
        }

        paths = chromium_paths.get(self.system, [])
        for path in paths:
            if os.path.exists(path):
                return {
                    'name': 'Chromium',
                    'path': path,
                    'supports_app_mode': True,
                    'supports_kiosk': True,
                    'browser_type': 'chromium'
                }

        # Try to find via which command on Unix systems
        if self.system in ['linux', 'darwin']:
            try:
                import subprocess
                result = subprocess.run(['which', 'chromium'], capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    return {
                        'name': 'Chromium',
                        'path': result.stdout.strip(),
                        'supports_app_mode': True,
                        'supports_kiosk': True,
                        'browser_type': 'chromium'
                    }
            except:
                pass

        return None

    def _detect_brave(self) -> Optional[Dict[str, Any]]:
        """Detect Brave browser."""
        brave_paths = {
            'windows': [
                r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe',
                r'C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe',
                os.path.expanduser(r'~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe'),
                r'C:\Program Files\BraveSoftware\Brave-Browser-Beta\Application\brave.exe',
                r'C:\Program Files\BraveSoftware\Brave-Browser-Dev\Application\brave.exe',
                r'C:\Program Files\BraveSoftware\Brave-Browser-Nightly\Application\brave.exe'
            ],
            'darwin': [
                '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
                '/Applications/Brave Browser Beta.app/Contents/MacOS/Brave Browser Beta',
                '/Applications/Brave Browser Dev.app/Contents/MacOS/Brave Browser Dev',
                '/Applications/Brave Browser Nightly.app/Contents/MacOS/Brave Browser Nightly'
            ],
            'linux': [
                '/usr/bin/brave',
                '/usr/bin/brave-browser',
                '/usr/bin/brave-browser-stable',
                '/usr/bin/brave-browser-beta',
                '/usr/bin/brave-browser-dev',
                '/snap/bin/brave',
                '/usr/local/bin/brave',
                '/opt/brave.com/brave/brave-browser',
                '/flatpak/app/com.brave.Browser'
            ]
        }

        paths = brave_paths.get(self.system, [])
        for path in paths:
            if os.path.exists(path):
                return {
                    'name': 'Brave Browser',
                    'path': path,
                    'supports_app_mode': True,
                    'supports_kiosk': True,
                    'browser_type': 'brave'
                }

        # Try to find via which command on Unix systems
        if self.system in ['linux', 'darwin']:
            try:
                import subprocess
                for cmd in ['brave', 'brave-browser']:
                    result = subprocess.run(['which', cmd], capture_output=True, text=True)
                    if result.returncode == 0 and result.stdout.strip():
                        return {
                            'name': 'Brave Browser',
                            'path': result.stdout.strip(),
                            'supports_app_mode': True,
                            'supports_kiosk': True,
                            'browser_type': 'brave'
                        }
            except:
                pass

        return None

    def _detect_edge(self) -> Optional[Dict[str, Any]]:
        """Detect Microsoft Edge."""
        edge_paths = {
            'windows': [
                r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
                r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'
            ],
            'darwin': [
                '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'
            ],
            'linux': [
                '/usr/bin/microsoft-edge',
                '/usr/bin/microsoft-edge-stable'
            ]
        }
        
        paths = edge_paths.get(self.system, [])
        for path in paths:
            if os.path.exists(path):
                return {
                    'name': 'Microsoft Edge',
                    'path': path,
                    'supports_app_mode': True,
                    'supports_kiosk': True
                }
        
        return None
    
    def _detect_firefox(self) -> Optional[Dict[str, Any]]:
        """Detect Mozilla Firefox."""
        firefox_paths = {
            'windows': [
                r'C:\Program Files\Mozilla Firefox\firefox.exe',
                r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe'
            ],
            'darwin': [
                '/Applications/Firefox.app/Contents/MacOS/firefox'
            ],
            'linux': [
                '/usr/bin/firefox',
                '/usr/bin/firefox-esr',
                '/snap/bin/firefox'
            ]
        }
        
        paths = firefox_paths.get(self.system, [])
        for path in paths:
            if os.path.exists(path):
                return {
                    'name': 'Mozilla Firefox',
                    'path': path,
                    'supports_app_mode': False,
                    'supports_kiosk': True
                }
        
        return None
    
    def _detect_safari(self) -> Optional[Dict[str, Any]]:
        """Detect Safari (macOS only)."""
        safari_path = '/Applications/Safari.app/Contents/MacOS/Safari'
        if os.path.exists(safari_path):
            return {
                'name': 'Safari',
                'path': safari_path,
                'supports_app_mode': False,
                'supports_kiosk': False
            }
        return None
    

    
    def get_best_browser(self) -> Optional[str]:
        """Get the best available browser."""
        # Preference order: Chrome-based browsers first, then others
        preference_order = ['chrome', 'chromium', 'brave', 'edge', 'firefox', 'safari']

        # Check for custom browser first
        if 'custom' in self.detected_browsers:
            return 'custom'

        for browser in preference_order:
            if browser in self.detected_browsers:
                return browser

        return None
    
    def get_browser_info(self, browser_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific browser."""
        return self.detected_browsers.get(browser_name)


class BrowserLauncher:
    """Launches applications in browsers."""
    
    def __init__(self, detector: BrowserDetector = None):
        self.detector = detector or BrowserDetector()
        self.logger = Logger("Launcher")
    

    
    def launch_browser(self, url: str, browser: str = "auto",
                      app_mode: bool = True, kiosk: bool = False,
                      size: tuple = None, position: tuple = None) -> tuple:
        try:
            if browser == "auto":
                browser = self.detector.get_best_browser()

            if not browser:
                self.logger.warning("No suitable browser found")
                return False, None

            browser_info = self.detector.get_browser_info(browser)
            if not browser_info:
                self.logger.warning(f"Browser {browser} not available")
                return False, None

            # Launch based on browser type
            if browser in ['chrome', 'chromium', 'brave']:
                return self._launch_chromium_based(url, browser_info, app_mode, kiosk, size, position)
            elif browser == 'edge':
                return self._launch_edge(url, browser_info, app_mode, kiosk, size, position)
            elif browser == 'firefox':
                return self._launch_firefox(url, browser_info, kiosk, size, position)
            else:
                # Fallback to default browser
                webbrowser.open(url)
                return True, None

        except Exception as e:
            self.logger.error(f"Browser launch failed: {e}")
            return False, None
    
    def _launch_chromium_based(self, url: str, browser_info: Dict[str, Any],
                              app_mode: bool, kiosk: bool, size: tuple = None, position: tuple = None) -> tuple:
        """Launch Chromium-based browser (Chrome, Chromium, Brave) with specific options."""
        if not browser_info['path']:
            # Fallback to webbrowser module
            if browser_info.get('browser_obj'):
                browser_info['browser_obj'].open(url)
                return True, None
            else:
                webbrowser.open(url)
                return True, None
        
        args = [browser_info['path']]

        if app_mode and browser_info['supports_app_mode']:
            args.extend([
                '--app=' + url,
                '--disable-web-security',
                '--disable-features=TranslateUI',
                '--no-first-run',
                '--no-default-browser-check'
            ])
        elif kiosk and browser_info['supports_kiosk']:
            args.extend([
                '--kiosk',
                '--disable-web-security',
                '--no-first-run'
            ])
            args.append(url)
        else:
            args.append(url)

        # Add window size if specified
        if size and len(size) == 2:
            args.append(f'--window-size={size[0]},{size[1]}')

        # Add window position if specified
        if position and len(position) == 2:
            args.append(f'--window-position={position[0]},{position[1]}')

        process = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, process
    
    def _launch_edge(self, url: str, browser_info: Dict[str, Any],
                    app_mode: bool, kiosk: bool, size: tuple = None, position: tuple = None) -> tuple:
        """Launch Edge with specific options."""
        args = [browser_info['path']]
        
        if app_mode and browser_info['supports_app_mode']:
            args.extend([
                '--app=' + url,
                '--disable-web-security',
                '--no-first-run'
            ])
        elif kiosk and browser_info['supports_kiosk']:
            args.extend([
                '--kiosk',
                '--disable-web-security'
            ])
            args.append(url)
        else:
            args.append(url)

        # Add window size if specified
        if size and len(size) == 2:
            args.append(f'--window-size={size[0]},{size[1]}')

        # Add window position if specified
        if position and len(position) == 2:
            args.append(f'--window-position={position[0]},{position[1]}')

        process = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, process
    
    def _launch_firefox(self, url: str, browser_info: Dict[str, Any], kiosk: bool,
                       size: tuple = None, position: tuple = None) -> tuple:
        """Launch Firefox with specific options."""
        args = [browser_info['path']]

        if kiosk and browser_info['supports_kiosk']:
            args.extend(['-kiosk', url])
        else:
            args.append(url)

        # Add window size if specified (Firefox uses different syntax)
        if size and len(size) == 2:
            args.extend(['-width', str(size[0]), '-height', str(size[1])])

        # Firefox doesn't have a direct position argument, but we can try with window geometry
        # Note: Firefox position control is limited compared to Chromium browsers

        process = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, process


class ControlledBrowser:
    """
    Controlled browser instance with lifecycle management.
    Provides Eel-like browser control with temporary profiles and app mode.
    """

    def __init__(self, app_name="PyWire App"):
        self.app_name = app_name
        self.logger = Logger("ControlledBrowser")
        self.detector = BrowserDetector()
        self.process = None
        self.temp_dir = None
        self.url = None
        self.browser_type = None
        self.shutdown_callback = None
        self._cleanup_registered = False

        # Register cleanup on exit
        if not self._cleanup_registered:
            atexit.register(self.cleanup)
            self._cleanup_registered = True

    def launch(self, url: str, mode='app', size=(1024, 768), position=None,
               browser='auto', block=True, close_callback=None):
        """
        Launch controlled browser instance.

        Args:
            url: URL to open
            mode: 'app', 'kiosk', or 'normal'
            size: (width, height) tuple
            position: (x, y) tuple for window position
            browser: Browser to use ('auto', 'chrome', 'edge', 'firefox')
            block: Whether to block until browser closes
            close_callback: Function to call when browser closes
        """
        self.url = url
        self.shutdown_callback = close_callback

        # Create temporary user data directory
        self.temp_dir = tempfile.mkdtemp(prefix=f"pywire_{self.app_name.replace(' ', '_')}_")
        self.logger.info(f"Created temporary profile: {self.temp_dir}")

        # Determine browser to use
        if browser == 'auto':
            browser = self._get_best_browser()

        self.browser_type = browser

        # Launch browser based on type
        success = False
        if browser in ['chrome', 'chromium', 'brave']:
            success = self._launch_chromium_controlled(url, mode, size, position, browser)
        elif browser == 'edge':
            success = self._launch_edge_controlled(url, mode, size, position)
        elif browser == 'firefox':
            success = self._launch_firefox_controlled(url, mode, size, position)
        else:
            self.logger.warning(f"Unsupported browser: {browser}, falling back to default")
            webbrowser.open(url)
            return True

        if not success:
            self.logger.error("Failed to launch controlled browser")
            self.cleanup()
            return False

        # Start monitoring thread
        if self.process:
            monitor_thread = threading.Thread(target=self._monitor_process, daemon=True)
            monitor_thread.start()

        # Block if requested
        if block and self.process:
            try:
                self.process.wait()
            except KeyboardInterrupt:
                self.logger.info("Interrupted by user")
            finally:
                self.cleanup()

        return True

    def _get_best_browser(self):
        """Get the best available browser for controlled mode."""
        # Prefer Chromium-based browsers for best app mode support
        for browser in ['chrome', 'chromium', 'brave']:
            if browser in self.detector.detected_browsers:
                return browser

        # Fallback to other browsers
        if 'edge' in self.detector.detected_browsers:
            return 'edge'
        elif 'firefox' in self.detector.detected_browsers:
            return 'firefox'
        else:
            return 'default'

    def _launch_chromium_controlled(self, url: str, mode: str, size: tuple, position: tuple, browser_type: str):
        """Launch Chromium-based browser (Chrome, Chromium, Brave) in controlled mode."""
        browser_info = self.detector.get_browser_info(browser_type)
        if not browser_info or not browser_info.get('path'):
            self.logger.warning(f"{browser_type.title()} not found")
            return False

        args = [browser_info['path']]

        args.extend([
            f'--user-data-dir={self.temp_dir}',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-default-apps',
            '--disable-popup-blocking',
            '--disable-translate',
            '--disable-background-timer-throttling',
            '--disable-renderer-backgrounding',
            '--disable-backgrounding-occluded-windows',
            '--disable-ipc-flooding-protection',
            '--disable-web-security',
            '--disable-features=TranslateUI,BlinkGenPropertyTrees',
            '--enable-features=NetworkService',
            '--force-color-profile=srgb',
            '--metrics-recording-only',
            '--no-report-upload',
            '--safebrowsing-disable-auto-update',
            '--enable-automation',
            '--password-store=basic',
            '--use-mock-keychain',
            '--disable-sync',
            '--disable-background-networking',
            '--disable-extensions',
            '--disable-component-extensions-with-background-pages'
        ])

        if mode == 'app':
            args.extend([
                f'--app={url}',
                '--hide-crash-restore-bubble',
                '--disable-session-crashed-bubble',
                '--disable-infobars',
                '--disable-restore-session-state'
            ])
        elif mode == 'kiosk':
            args.extend([
                '--kiosk',
                '--disable-pinch',
                '--overscroll-history-navigation=0'
            ])
            args.append(url)
        else:  # normal mode
            args.append(url)

        # Window size and position
        if size:
            args.append(f'--window-size={size[0]},{size[1]}')
        if position:
            args.append(f'--window-position={position[0]},{position[1]}')

        try:
            self.process = subprocess.Popen(
                args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            self.logger.info(f"Chrome launched with PID: {self.process.pid}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to launch Chrome: {e}")
            return False

    def _launch_edge_controlled(self, url: str, mode: str, size: tuple, position: tuple):
        """Launch Edge in controlled mode."""
        browser_info = self.detector.get_browser_info('edge')
        if not browser_info or not browser_info.get('path'):
            self.logger.warning("Edge not found")
            return False

        args = [browser_info['path']]

        # Similar to Chrome but with Edge-specific flags
        args.extend([
            f'--user-data-dir={self.temp_dir}',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-default-apps',
            '--disable-popup-blocking',
            '--disable-translate',
            '--disable-web-security',
            '--disable-features=TranslateUI',
            '--enable-automation',
            '--disable-sync',
            '--disable-extensions'
        ])

        if mode == 'app':
            args.extend([
                f'--app={url}',
                '--disable-infobars'
            ])
        elif mode == 'kiosk':
            args.extend(['--kiosk'])
            args.append(url)
        else:
            args.append(url)

        if size:
            args.append(f'--window-size={size[0]},{size[1]}')
        if position:
            args.append(f'--window-position={position[0]},{position[1]}')

        try:
            self.process = subprocess.Popen(
                args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            self.logger.info(f"Edge launched with PID: {self.process.pid}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to launch Edge: {e}")
            return False

    def _launch_firefox_controlled(self, url: str, mode: str, size: tuple, position: tuple):
        """Launch Firefox in controlled mode."""
        browser_info = self.detector.get_browser_info('firefox')
        if not browser_info or not browser_info.get('path'):
            self.logger.warning("Firefox not found")
            return False

        args = [browser_info['path']]

        # Firefox profile arguments
        args.extend([
            '-profile', self.temp_dir,
            '-no-remote',
            '-new-instance'
        ])

        if mode == 'kiosk':
            args.extend(['-kiosk'])

        args.append(url)

        try:
            self.process = subprocess.Popen(
                args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            self.logger.info(f"Firefox launched with PID: {self.process.pid}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to launch Firefox: {e}")
            return False

    def _monitor_process(self):
        """Monitor browser process and handle cleanup when it exits."""
        if not self.process:
            return

        try:
            self.process.wait()
            self.logger.info(f"Browser process {self.process.pid} has exited")

            if self.shutdown_callback:
                try:
                    self.shutdown_callback()
                except Exception as e:
                    self.logger.error(f"Error in shutdown callback: {e}")

            self.cleanup()

        except Exception as e:
            self.logger.error(f"Error monitoring browser process: {e}")

    def is_running(self):
        """Check if browser process is still running."""
        if not self.process:
            return False
        return self.process.poll() is None

    def close(self):
        """Close the browser and cleanup."""
        if self.process and self.is_running():
            try:
                self.logger.info(f"Terminating browser process {self.process.pid}")
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.logger.warning("Force killing browser process")
                    self.process.kill()
                    self.process.wait()

            except Exception as e:
                self.logger.error(f"Error closing browser: {e}")

        self.cleanup()

    def cleanup(self):
        """Clean up temporary files and resources."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                time.sleep(1)
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                self.logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
                self.temp_dir = None
            except Exception as e:
                self.logger.warning(f"Failed to cleanup temp directory: {e}")

        self.process = None
