"""
Python wrapper for agent-browser CLI
Provides easy control of browser automation via agent-browser commands
"""

import json
import subprocess
import atexit
import tempfile
import os
from typing import Optional, Dict, Any, List, Union, Literal
from pathlib import Path
from benedict import BeneDict


class AgentBrowserError(Exception):
    """Base exception for agent-browser errors"""

    pass


class BatchContext:
    """Context manager for batched command execution"""

    def __init__(self, browser: "AgentBrowser"):
        self.browser = browser
        self.commands: List[Dict[str, Any]] = []
        self.results: List[Any] = []

    def __enter__(self) -> "BatchContext":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.commands and not exc_type:
            self.results = self.browser.execute_batch(self.commands)
        return False

    def open(
        self, url: str, headers: Optional[Dict[str, str]] = None
    ) -> "BatchContext":
        """Queue open command"""
        cmd = {"method": "open", "args": [url]}
        if headers:
            cmd["kwargs"] = {"headers": headers}
        self.commands.append(cmd)
        return self

    def click(self, selector: str) -> "BatchContext":
        """Queue click command"""
        self.commands.append({"method": "click", "args": [selector]})
        return self

    def fill(self, selector: str, text: str) -> "BatchContext":
        """Queue fill command"""
        self.commands.append({"method": "fill", "args": [selector, text]})
        return self

    def type(self, selector: str, text: str) -> "BatchContext":
        """Queue type command"""
        self.commands.append({"method": "type", "args": [selector, text]})
        return self

    def press(self, key: str) -> "BatchContext":
        """Queue press command"""
        self.commands.append({"method": "press", "args": [key]})
        return self

    def hover(self, selector: str) -> "BatchContext":
        """Queue hover command"""
        self.commands.append({"method": "hover", "args": [selector]})
        return self

    def wait(self, selector_or_ms: str) -> "BatchContext":
        """Queue wait command"""
        self.commands.append({"method": "wait", "args": [selector_or_ms]})
        return self

    def get_title(self) -> "BatchContext":
        """Queue get title command"""
        self.commands.append(
            {"method": "get", "args": ["title"], "kwargs": {"json_output": True}}
        )
        return self

    def get_url(self) -> "BatchContext":
        """Queue get url command"""
        self.commands.append(
            {"method": "get", "args": ["url"], "kwargs": {"json_output": True}}
        )
        return self

    def get_text(self, selector: str) -> "BatchContext":
        """Queue get text command"""
        self.commands.append(
            {
                "method": "get",
                "args": ["text", selector],
                "kwargs": {"json_output": True},
            }
        )
        return self

    def get_page(self, mode: Literal["html", "text"]) -> "BatchContext":
        if mode == "html":
            javascript = "document.documentElement.outerHTML"
        elif mode == "text":
            javascript = "document.body.innerText"
        else:
            raise ValueError(f"Unsupported mode: {mode}")

        self.commands.append(
            {"method": "eval", "args": [javascript], "kwargs": {"json_output": True}}
        )
        return self

    def screenshot(self, path: Optional[str] = None) -> "BatchContext":
        """Queue screenshot command"""
        args = ["screenshot"]
        if path:
            args.append(path)
        self.commands.append(
            {"method": args[0], "args": args[1:] if len(args) > 1 else []}
        )
        return self

    def snapshot(
        self, interactive_only: bool = False, compact: bool = False
    ) -> "BatchContext":
        """Queue snapshot command"""
        cmd = {"method": "snapshot", "args": [], "kwargs": {"json_output": True}}
        if interactive_only or compact:
            cmd["kwargs"]["interactive_only"] = interactive_only
            cmd["kwargs"]["compact"] = compact
        self.commands.append(cmd)
        return self


class AgentBrowser:
    """
    Python wrapper for agent-browser CLI

    Examples:
        # Basic usage
        browser = AgentBrowser()
        browser.open("https://example.com")
        snapshot = browser.snapshot(interactive_only=True)
        browser.click("@e2")
        browser.close()

        # With session
        browser = AgentBrowser(session="my-session")
        browser.open("https://example.com")

        # Headed mode (visible browser)
        browser = AgentBrowser(headed=True)
        browser.open("https://example.com")
    """

    def __init__(
        self,
        session: Optional[str] = None,
        executable_path: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        headed: bool = False,
        debug: bool = False,
        cdp_port: Optional[int] = None,
        auto_close: bool = True,
        close_on_exit: bool = False,
    ):
        """
        Initialize AgentBrowser controller

        Args:
            session: Session name for isolated browser instance
            executable_path: Custom browser executable path
            headers: HTTP headers to set
            headed: Show browser window (not headless)
            debug: Enable debug output
            cdp_port: Connect via Chrome DevTools Protocol port
        """
        self.session = session
        self.executable_path = executable_path
        self.headers = headers
        self.headed = headed
        self.debug = debug
        self.cdp_port = cdp_port

        self.auto_close = auto_close
        self.close_on_exit = close_on_exit
        self._close_on_exit_registered = False

        if self.close_on_exit:
            self.register_close_on_exit()

    def register_close_on_exit(self) -> None:
        if self._close_on_exit_registered:
            return

        def cleanup():
            try:
                self.close()
            except Exception:
                pass

        atexit.register(cleanup)
        self._close_on_exit_registered = True

    def _build_command(self, *args: str, json_output: bool = False) -> List[str]:
        """Build agent-browser command with common options"""
        cmd = ["agent-browser"]

        if self.session:
            cmd.extend(["--session", self.session])
        if self.executable_path:
            cmd.extend(["--executable-path", self.executable_path])
        if self.headed:
            cmd.append("--headed")
        if self.debug:
            cmd.append("--debug")
        if self.cdp_port:
            cmd.extend(["--cdp", str(self.cdp_port)])
        if json_output:
            cmd.append("--json")

        cmd.extend(args)
        return cmd

    def _run(self, *args: str, json_output: bool = False, check: bool = True) -> Any:
        """Run agent-browser command and return result"""
        cmd = self._build_command(*args, json_output=json_output)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=check)

            if json_output and result.stdout:
                try:
                    data = json.loads(result.stdout)
                    if not data.get("success"):
                        raise AgentBrowserError(data.get("error", "Unknown error"))
                    return data.get("data")
                except json.JSONDecodeError as e:
                    raise AgentBrowserError(f"Failed to parse JSON output: {e}")

            return result.stdout.strip() if result.stdout else None

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else str(e)
            raise AgentBrowserError(f"Command failed: {error_msg}")

    # Navigation
    def open(self, url: str, headers: Optional[Dict[str, str]] = None) -> None:
        """
        Navigate to URL

        Args:
            url: URL to navigate to
            headers: Optional HTTP headers (scoped to URL's origin)
        """
        cmd_args = ["open", url]
        if headers or self.headers:
            headers_json = json.dumps(headers or self.headers)
            cmd_args.extend(["--headers", headers_json])
        self._run(*cmd_args)

    def goto(self, url: str, headers: Optional[Dict[str, str]] = None) -> None:
        """Alias for open()"""
        self.open(url, headers)

    def back(self) -> None:
        """Go back in history"""
        self._run("back")

    def forward(self) -> None:
        """Go forward in history"""
        self._run("forward")

    def reload(self) -> None:
        """Reload current page"""
        self._run("reload")

    # Actions
    def click(self, selector: str) -> None:
        """Click element by selector or ref"""
        self._run("click", selector)

    def dblclick(self, selector: str) -> None:
        """Double-click element"""
        self._run("dblclick", selector)

    def focus(self, selector: str) -> None:
        """Focus element"""
        self._run("focus", selector)

    def type(self, selector: str, text: str) -> None:
        """Type into element"""
        self._run("type", selector, text)

    def fill(self, selector: str, text: str) -> None:
        """Clear and fill element"""
        self._run("fill", selector, text)

    def press(self, key: str) -> None:
        """Press key (e.g., 'Enter', 'Tab', 'Control+a')"""
        self._run("press", key)

    def key(self, key: str) -> None:
        """Alias for press()"""
        self.press(key)

    def keydown(self, key: str) -> None:
        """Hold key down"""
        self._run("keydown", key)

    def keyup(self, key: str) -> None:
        """Release key"""
        self._run("keyup", key)

    def hover(self, selector: str) -> None:
        """Hover over element"""
        self._run("hover", selector)

    def select(self, selector: str, value: str) -> None:
        """Select dropdown option"""
        self._run("select", selector, value)

    def check(self, selector: str) -> None:
        """Check checkbox"""
        self._run("check", selector)

    def uncheck(self, selector: str) -> None:
        """Uncheck checkbox"""
        self._run("uncheck", selector)

    def scroll(self, direction: str, pixels: Optional[int] = None) -> None:
        """
        Scroll page

        Args:
            direction: 'up', 'down', 'left', or 'right'
            pixels: Number of pixels to scroll
        """
        args = ["scroll", direction]
        if pixels is not None:
            args.append(str(pixels))
        self._run(*args)

    def scroll_into_view(self, selector: str) -> None:
        """Scroll element into view"""
        self._run("scrollintoview", selector)

    def drag(self, source: str, target: str) -> None:
        """Drag and drop from source to target"""
        self._run("drag", source, target)

    def upload(self, selector: str, *files: str) -> None:
        """Upload files to input element"""
        self._run("upload", selector, *files)

    # Information
    def get_text(self, selector: str) -> str:
        """Get text content of element"""
        result = self._run("get", "text", selector, json_output=True)
        if isinstance(result, dict) and "text" in result:
            return result["text"]
        return result

    def get_html(self, selector: str) -> str:
        """Get innerHTML of element"""
        result = self._run("get", "html", selector, json_output=True)
        if isinstance(result, dict) and "html" in result:
            return result["html"]
        return result

    def get_value(self, selector: str) -> str:
        """Get input value"""
        result = self._run("get", "value", selector, json_output=True)
        if isinstance(result, dict) and "value" in result:
            return result["value"]
        return result

    def get_attr(self, selector: str, attr: str) -> str:
        """Get attribute value"""
        result = self._run("get", "attr", selector, attr, json_output=True)
        if isinstance(result, dict) and "value" in result:
            return result["value"]
        return result

    def get_title(self) -> str:
        """Get page title"""
        result = self._run("get", "title", json_output=True)
        if isinstance(result, dict) and "title" in result:
            return result["title"]
        return result

    def get_url(self) -> str:
        """Get current URL"""
        result = self._run("get", "url", json_output=True)
        if isinstance(result, dict) and "url" in result:
            return result["url"]
        return result

    def get_count(self, selector: str) -> int:
        """Count matching elements"""
        result = self._run("get", "count", selector, json_output=True)
        if isinstance(result, dict) and "count" in result:
            return result["count"]
        return result

    def get_box(self, selector: str) -> Dict[str, float]:
        """Get bounding box of element"""
        result = self._run("get", "box", selector, json_output=True)
        if isinstance(result, dict) and "box" in result:
            return result["box"]
        return result

    def get_page(self, mode: Literal["html", "text"]) -> str:
        if mode == "html":
            return self.eval("document.documentElement.outerHTML")
        if mode == "text":
            return self.eval("document.body.innerText")
        raise ValueError(f"Unsupported mode: {mode}")

    def get_content(self):
        """Get raw HTML content"""
        return self.get_page("html")

    # State checks
    def is_visible(self, selector: str) -> bool:
        """Check if element is visible"""
        return self._run("is", "visible", selector, json_output=True)

    def is_enabled(self, selector: str) -> bool:
        """Check if element is enabled"""
        return self._run("is", "enabled", selector, json_output=True)

    def is_checked(self, selector: str) -> bool:
        """Check if checkbox is checked"""
        return self._run("is", "checked", selector, json_output=True)

    # Snapshot
    def snapshot(
        self,
        interactive_only: bool = False,
        compact: bool = False,
        depth: Optional[int] = None,
        selector: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get accessibility tree snapshot with refs

        Args:
            interactive_only: Only show interactive elements
            compact: Remove empty structural elements
            depth: Limit tree depth
            selector: Scope to CSS selector

        Returns:
            Dict with 'snapshot' (tree string) and 'refs' (element info)
        """
        args = ["snapshot"]
        if interactive_only:
            args.append("-i")
        if compact:
            args.append("-c")
        if depth is not None:
            args.extend(["-d", str(depth)])
        if selector:
            args.extend(["-s", selector])

        ss = self._run(*args, json_output=True)
        return BeneDict(ss)

    # Screenshot & PDF
    def screenshot(
        self, path: Optional[str] = None, full_page: bool = False
    ) -> Optional[str]:
        """
        Take screenshot

        Args:
            path: File path to save screenshot (None returns base64 PNG)
            full_page: Capture full scrollable page

        Returns:
            Base64 PNG string if path is None, otherwise None
        """
        args = ["screenshot"]
        if path:
            args.append(path)
        if full_page:
            args.append("--full")

        return self._run(*args)

    def pdf(self, path: str) -> None:
        """Save page as PDF"""
        self._run("pdf", path)

    # Wait
    def wait(
        self,
        selector_or_ms: Optional[str] = None,
        text: Optional[str] = None,
        url: Optional[str] = None,
        load_state: Optional[str] = None,
        function: Optional[str] = None,
    ) -> None:
        """
        Wait for condition

        Args:
            selector_or_ms: Element selector or milliseconds
            text: Wait for text to appear
            url: Wait for URL pattern
            load_state: Wait for load state ('load', 'domcontentloaded', 'networkidle')
            function: Wait for JS condition
        """
        args = ["wait"]
        if selector_or_ms:
            args.append(selector_or_ms)
        if text:
            args.extend(["--text", text])
        if url:
            args.extend(["--url", url])
        if load_state:
            args.extend(["--load", load_state])
        if function:
            args.extend(["--fn", function])

        self._run(*args)

    # Find (semantic locators)
    def find_role(
        self,
        role: str,
        action: str,
        value: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Any:
        """Find element by ARIA role"""
        args = ["find", "role", role, action]
        if value:
            args.append(value)
        if name:
            args.extend(["--name", name])
        return self._run(*args, json_output=(action == "text"))

    def find_text(self, text: str, action: str) -> Any:
        """Find element by text content"""
        args = ["find", "text", text, action]
        return self._run(*args, json_output=(action == "text"))

    def find_label(self, label: str, action: str, value: Optional[str] = None) -> Any:
        """Find element by label"""
        args = ["find", "label", label, action]
        if value:
            args.append(value)
        return self._run(*args, json_output=(action == "text"))

    # Eval
    def eval(self, javascript: str) -> Any:
        """Execute JavaScript and return result"""
        return self._run("eval", javascript, json_output=True)

    # Mouse
    def mouse_move(self, x: int, y: int) -> None:
        """Move mouse to coordinates"""
        self._run("mouse", "move", str(x), str(y))

    def mouse_down(self, button: str = "left") -> None:
        """Press mouse button"""
        self._run("mouse", "down", button)

    def mouse_up(self, button: str = "left") -> None:
        """Release mouse button"""
        self._run("mouse", "up", button)

    def mouse_wheel(self, dy: int, dx: int = 0) -> None:
        """Scroll mouse wheel"""
        self._run("mouse", "wheel", str(dy), str(dx))

    # Settings
    def set_viewport(self, width: int, height: int) -> None:
        """Set viewport size"""
        self._run("set", "viewport", str(width), str(height))

    def set_device(self, name: str) -> None:
        """Emulate device (e.g., 'iPhone 14')"""
        self._run("set", "device", name)

    def set_geolocation(self, latitude: float, longitude: float) -> None:
        """Set geolocation"""
        self._run("set", "geo", str(latitude), str(longitude))

    def set_offline(self, enabled: bool = True) -> None:
        """Toggle offline mode"""
        self._run("set", "offline", "on" if enabled else "off")

    def set_headers(self, headers: Dict[str, str]) -> None:
        """Set extra HTTP headers"""
        self._run("set", "headers", json.dumps(headers))

    def set_credentials(self, username: str, password: str) -> None:
        """Set HTTP basic auth credentials"""
        self._run("set", "credentials", username, password)

    def set_media(self, scheme: str) -> None:
        """Emulate color scheme ('dark' or 'light')"""
        self._run("set", "media", scheme)

    # Cookies
    def get_cookies(self) -> List[Dict[str, Any]]:
        """Get all cookies"""
        return self._run("cookies", json_output=True)

    def set_cookie(self, name: str, value: str) -> None:
        """Set cookie"""
        self._run("cookies", "set", name, value)

    def clear_cookies(self) -> None:
        """Clear all cookies"""
        self._run("cookies", "clear")

    # Storage
    def get_local_storage(self, key: Optional[str] = None) -> Any:
        """Get localStorage (all or specific key)"""
        args = ["storage", "local"]
        if key:
            args.append(key)
        return self._run(*args, json_output=True)

    def set_local_storage(self, key: str, value: str) -> None:
        """Set localStorage value"""
        self._run("storage", "local", "set", key, value)

    def clear_local_storage(self) -> None:
        """Clear localStorage"""
        self._run("storage", "local", "clear")

    def get_session_storage(self, key: Optional[str] = None) -> Any:
        """Get sessionStorage (all or specific key)"""
        args = ["storage", "session"]
        if key:
            args.append(key)
        return self._run(*args, json_output=True)

    def set_session_storage(self, key: str, value: str) -> None:
        """Set sessionStorage value"""
        self._run("storage", "session", "set", key, value)

    def clear_session_storage(self) -> None:
        """Clear sessionStorage"""
        self._run("storage", "session", "clear")

    # Network
    def network_route(
        self, url: str, abort: bool = False, body: Optional[Dict] = None
    ) -> None:
        """
        Intercept network requests

        Args:
            url: URL pattern to intercept
            abort: Block requests
            body: Mock response body
        """
        args = ["network", "route", url]
        if abort:
            args.append("--abort")
        if body:
            args.extend(["--body", json.dumps(body)])
        self._run(*args)

    def network_unroute(self, url: Optional[str] = None) -> None:
        """Remove network routes"""
        args = ["network", "unroute"]
        if url:
            args.append(url)
        self._run(*args)

    def network_requests(
        self, filter_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """View tracked requests"""
        args = ["network", "requests"]
        if filter_text:
            args.extend(["--filter", filter_text])
        return self._run(*args, json_output=True)

    # Tabs
    def list_tabs(self) -> List[Dict[str, Any]]:
        """List all tabs"""
        return self._run("tab", json_output=True)

    def new_tab(self, url: Optional[str] = None) -> None:
        """Create new tab"""
        args = ["tab", "new"]
        if url:
            args.append(url)
        self._run(*args)

    def switch_tab(self, index: int) -> None:
        """Switch to tab by index"""
        self._run("tab", str(index))

    def close_tab(self, index: Optional[int] = None) -> None:
        """Close tab"""
        args = ["tab", "close"]
        if index is not None:
            args.append(str(index))
        self._run(*args)

    def new_window(self) -> None:
        """Create new window"""
        self._run("window", "new")

    # Frames
    def switch_frame(self, selector: str) -> None:
        """Switch to iframe"""
        self._run("frame", selector)

    def main_frame(self) -> None:
        """Switch back to main frame"""
        self._run("frame", "main")

    # Dialogs
    def accept_dialog(self, text: Optional[str] = None) -> None:
        """Accept dialog (with optional prompt text)"""
        args = ["dialog", "accept"]
        if text:
            args.append(text)
        self._run(*args)

    def dismiss_dialog(self) -> None:
        """Dismiss dialog"""
        self._run("dialog", "dismiss")

    # Debug
    def start_trace(self, path: Optional[str] = None) -> None:
        """Start recording trace"""
        args = ["trace", "start"]
        if path:
            args.append(path)
        self._run(*args)

    def stop_trace(self, path: Optional[str] = None) -> None:
        """Stop and save trace"""
        args = ["trace", "stop"]
        if path:
            args.append(path)
        self._run(*args)

    def get_console(self, clear: bool = False) -> List[str]:
        """View console messages"""
        args = ["console"]
        if clear:
            args.append("--clear")
        result = self._run(*args)
        return result.split("\n") if result else []

    def get_errors(self, clear: bool = False) -> List[str]:
        """View page errors"""
        args = ["errors"]
        if clear:
            args.append("--clear")
        result = self._run(*args)
        return result.split("\n") if result else []

    def highlight(self, selector: str) -> None:
        """Highlight element"""
        self._run("highlight", selector)

    def save_state(self, path: str) -> None:
        """Save authentication state"""
        self._run("state", "save", path)

    def load_state(self, path: str) -> None:
        """Load authentication state"""
        self._run("state", "load", path)

    # Session management
    @staticmethod
    def list_sessions() -> List[str]:
        """List all active browser sessions"""
        result = subprocess.run(
            ["agent-browser", "session", "list", "--json"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout:
            try:
                data = json.loads(result.stdout)
                if data.get("success"):
                    return data.get("data", {}).get("sessions", [])
            except json.JSONDecodeError:
                pass
        return []

    def get_current_session(self) -> str:
        """Get current session name"""
        result = self._run("session", json_output=True)
        if isinstance(result, dict) and "session" in result:
            return result["session"]
        return result or "default"

    def is_session_active(self) -> bool:
        """Check if current session is active"""
        sessions = self.list_sessions()
        current = self.session or "default"
        return current in sessions

    def batch(self) -> BatchContext:
        """Start a batch execution context"""
        return BatchContext(self)

    def execute_batch(self, commands: List[Dict[str, Any]]) -> List[Any]:
        """Execute multiple commands in a single subprocess call"""
        if not commands:
            return []

        script_lines = ["#!/bin/bash", "set -e"]
        json_indices = []

        for idx, cmd_dict in enumerate(commands):
            method = cmd_dict["method"]
            args = cmd_dict.get("args", [])
            kwargs = cmd_dict.get("kwargs", {})

            json_output = kwargs.get("json_output", False)
            if json_output:
                json_indices.append(idx)

            if method == "get":
                cmd_parts = self._build_command("get", *args, json_output=json_output)
            elif method == "eval":
                cmd_parts = self._build_command("eval", *args, json_output=json_output)
            elif method == "snapshot":
                interactive_only = kwargs.get("interactive_only", False)
                compact = kwargs.get("compact", False)
                snapshot_args = ["snapshot"]
                if interactive_only:
                    snapshot_args.append("-i")
                if compact:
                    snapshot_args.append("-c")
                cmd_parts = self._build_command(*snapshot_args, json_output=json_output)
            elif method == "open" and "headers" in kwargs:
                headers_json = json.dumps(kwargs["headers"])
                cmd_parts = self._build_command(method, *args)
                cmd_parts.extend(["--headers", headers_json])
            else:
                cmd_parts = self._build_command(method, *args, json_output=json_output)

            escaped_cmd = " ".join(
                f'"{part}"' if " " in str(part) else str(part) for part in cmd_parts
            )
            script_lines.append(escaped_cmd)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as f:
            f.write("\n".join(script_lines))
            script_path = f.name

        try:
            result = subprocess.run(
                ["bash", script_path], capture_output=True, text=True, check=False
            )

            if result.returncode != 0:
                raise AgentBrowserError(f"Batch execution failed: {result.stderr}")

            return self._parse_batch_results(result.stdout, json_indices, len(commands))

        finally:
            os.unlink(script_path)

    def _parse_batch_results(
        self, output: str, json_indices: List[int], total_commands: int
    ) -> List[Any]:
        """Parse results from batch execution"""
        lines = output.strip().split("\n") if output.strip() else []
        results = [None] * total_commands

        json_results = []

        for line in lines:
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    data = json.loads(line)
                    if isinstance(data, dict) and "success" in data:
                        if not data.get("success"):
                            raise AgentBrowserError(data.get("error", "Command failed"))
                        json_results.append(data.get("data"))
                except json.JSONDecodeError:
                    pass

        json_idx = 0
        for i in json_indices:
            if json_idx < len(json_results):
                results[i] = json_results[json_idx]
                json_idx += 1

        return results

    @staticmethod
    def close_all_sessions(max_retries: int = 2) -> int:
        """Close all active browser sessions"""
        import time

        total_closed = 0

        for attempt in range(max_retries):
            sessions = AgentBrowser.list_sessions()
            if not sessions:
                break

            closed_count = 0
            for session_name in sessions:
                try:
                    browser = AgentBrowser(session=session_name)
                    browser.close()
                    closed_count += 1
                except AgentBrowserError:
                    pass

            total_closed += closed_count

            if attempt < max_retries - 1 and AgentBrowser.list_sessions():
                time.sleep(0.5)

        return total_closed

    @staticmethod
    def shutdown(wait: bool = True, verbose: bool = False) -> Dict[str, Any]:
        """Complete cleanup of all browser resources"""
        import time

        result = {
            "sessions_closed": 0,
            "cleanup_performed": False,
            "remaining_sessions": [],
        }

        if verbose:
            sessions_before = AgentBrowser.list_sessions()
            if sessions_before:
                print(
                    f"[AgentBrowser] Shutting down {len(sessions_before)} session(s)..."
                )

        closed = AgentBrowser.close_all_sessions()
        result["sessions_closed"] = closed
        result["cleanup_performed"] = True

        if wait:
            time.sleep(2)

        remaining = AgentBrowser.list_sessions()
        result["remaining_sessions"] = remaining

        if verbose and not remaining:
            print("[AgentBrowser] Shutdown complete.")

        return result

    @staticmethod
    def register_shutdown_hook(verbose: bool = False) -> None:
        """Register automatic cleanup on program exit"""

        def cleanup():
            sessions = AgentBrowser.list_sessions()
            if sessions:
                AgentBrowser.shutdown(wait=True, verbose=verbose)

        atexit.register(cleanup)

    def connect(self, port: int) -> None:
        """Connect to existing browser via CDP"""
        self._run("connect", str(port))

    def close(self) -> None:
        """Close browser"""
        self._run("close")

    def quit(self) -> None:
        """Alias for close()"""
        self.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close browser"""
        if self.auto_close:
            try:
                self.close()
            except Exception:
                pass
        return False
