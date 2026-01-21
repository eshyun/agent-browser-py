"""
Async Python wrapper for agent-browser CLI
Provides async control of browser automation via agent-browser commands
"""

import json
import asyncio
import tempfile
import os
from typing import Optional, Dict, Any, List, Union
from pathlib import Path

from agent_browser import AgentBrowserError


class AsyncBatchContext:
    """Async context manager for batched command execution"""

    def __init__(self, browser: "AsyncAgentBrowser"):
        self.browser = browser
        self.commands: List[Dict[str, Any]] = []
        self.results: List[Any] = []

    async def __aenter__(self) -> "AsyncBatchContext":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.commands and not exc_type:
            self.results = await self.browser.execute_batch(self.commands)
        return False

    def open(
        self, url: str, headers: Optional[Dict[str, str]] = None
    ) -> "AsyncBatchContext":
        """Queue open command"""
        cmd = {"method": "open", "args": [url]}
        if headers:
            cmd["kwargs"] = {"headers": headers}
        self.commands.append(cmd)
        return self

    def click(self, selector: str) -> "AsyncBatchContext":
        """Queue click command"""
        self.commands.append({"method": "click", "args": [selector]})
        return self

    def fill(self, selector: str, text: str) -> "AsyncBatchContext":
        """Queue fill command"""
        self.commands.append({"method": "fill", "args": [selector, text]})
        return self

    def type(self, selector: str, text: str) -> "AsyncBatchContext":
        """Queue type command"""
        self.commands.append({"method": "type", "args": [selector, text]})
        return self

    def press(self, key: str) -> "AsyncBatchContext":
        """Queue press command"""
        self.commands.append({"method": "press", "args": [key]})
        return self

    def hover(self, selector: str) -> "AsyncBatchContext":
        """Queue hover command"""
        self.commands.append({"method": "hover", "args": [selector]})
        return self

    def wait(self, selector_or_ms: str) -> "AsyncBatchContext":
        """Queue wait command"""
        self.commands.append({"method": "wait", "args": [selector_or_ms]})
        return self

    def get_title(self) -> "AsyncBatchContext":
        """Queue get title command"""
        self.commands.append(
            {"method": "get", "args": ["title"], "kwargs": {"json_output": True}}
        )
        return self

    def get_url(self) -> "AsyncBatchContext":
        """Queue get url command"""
        self.commands.append(
            {"method": "get", "args": ["url"], "kwargs": {"json_output": True}}
        )
        return self

    def get_text(self, selector: str) -> "AsyncBatchContext":
        """Queue get text command"""
        self.commands.append(
            {
                "method": "get",
                "args": ["text", selector],
                "kwargs": {"json_output": True},
            }
        )
        return self

    def screenshot(self, path: Optional[str] = None) -> "AsyncBatchContext":
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
    ) -> "AsyncBatchContext":
        """Queue snapshot command"""
        cmd = {"method": "snapshot", "args": [], "kwargs": {"json_output": True}}
        if interactive_only or compact:
            cmd["kwargs"]["interactive_only"] = interactive_only
            cmd["kwargs"]["compact"] = compact
        self.commands.append(cmd)
        return self


class AsyncAgentBrowser:
    """
    Async Python wrapper for agent-browser CLI

    Examples:
        # Basic usage
        browser = AsyncAgentBrowser()
        await browser.open("https://example.com")
        snapshot = await browser.snapshot(interactive_only=True)
        await browser.click("@e2")
        await browser.close()

        # With session
        browser = AsyncAgentBrowser(session="my-session")
        await browser.open("https://example.com")

        # Headed mode (visible browser)
        browser = AsyncAgentBrowser(headed=True)
        await browser.open("https://example.com")

        # Context manager
        async with AsyncAgentBrowser() as browser:
            await browser.open("https://example.com")
            title = await browser.get_title()
    """

    def __init__(
        self,
        session: Optional[str] = None,
        executable_path: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        headed: bool = False,
        debug: bool = False,
        cdp_port: Optional[int] = None,
    ):
        """
        Initialize AsyncAgentBrowser controller

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

    async def __aenter__(self):
        """Context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic cleanup"""
        await self.close()
        return False

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

    async def _run(
        self, *args: str, json_output: bool = False, check: bool = True
    ) -> Any:
        """Run agent-browser command asynchronously and return result"""
        cmd = self._build_command(*args, json_output=json_output)

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if check and process.returncode != 0:
                error_msg = stderr.decode().strip() if stderr else "Unknown error"
                raise AgentBrowserError(f"Command failed: {error_msg}")

            stdout_text = stdout.decode().strip()

            if json_output and stdout_text:
                try:
                    data = json.loads(stdout_text)
                    if not data.get("success"):
                        raise AgentBrowserError(data.get("error", "Unknown error"))
                    return data.get("data")
                except json.JSONDecodeError as e:
                    raise AgentBrowserError(f"Failed to parse JSON output: {e}")

            return stdout_text if stdout_text else None

        except Exception as e:
            if isinstance(e, AgentBrowserError):
                raise
            raise AgentBrowserError(f"Command execution failed: {str(e)}")

    # Navigation
    async def open(self, url: str, headers: Optional[Dict[str, str]] = None) -> None:
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
        await self._run(*cmd_args)

    async def goto(self, url: str, headers: Optional[Dict[str, str]] = None) -> None:
        """Alias for open()"""
        await self.open(url, headers)

    async def back(self) -> None:
        """Go back in history"""
        await self._run("back")

    async def forward(self) -> None:
        """Go forward in history"""
        await self._run("forward")

    async def reload(self) -> None:
        """Reload current page"""
        await self._run("reload")

    # Actions
    async def click(self, selector: str) -> None:
        """Click element by selector or ref"""
        await self._run("click", selector)

    async def dblclick(self, selector: str) -> None:
        """Double-click element"""
        await self._run("dblclick", selector)

    async def focus(self, selector: str) -> None:
        """Focus element"""
        await self._run("focus", selector)

    async def type(self, selector: str, text: str) -> None:
        """Type into element"""
        await self._run("type", selector, text)

    async def fill(self, selector: str, text: str) -> None:
        """Clear and fill element"""
        await self._run("fill", selector, text)

    async def press(self, key: str) -> None:
        """Press key (e.g., 'Enter', 'Tab', 'Control+a')"""
        await self._run("press", key)

    async def key(self, key: str) -> None:
        """Alias for press()"""
        await self.press(key)

    async def keydown(self, key: str) -> None:
        """Hold key down"""
        await self._run("keydown", key)

    async def keyup(self, key: str) -> None:
        """Release key"""
        await self._run("keyup", key)

    async def hover(self, selector: str) -> None:
        """Hover over element"""
        await self._run("hover", selector)

    async def select(self, selector: str, value: str) -> None:
        """Select dropdown option"""
        await self._run("select", selector, value)

    async def check(self, selector: str) -> None:
        """Check checkbox"""
        await self._run("check", selector)

    async def uncheck(self, selector: str) -> None:
        """Uncheck checkbox"""
        await self._run("uncheck", selector)

    async def scroll(self, direction: str, pixels: Optional[int] = None) -> None:
        """
        Scroll page

        Args:
            direction: 'up', 'down', 'left', 'right'
            pixels: Number of pixels (optional)
        """
        cmd_args = ["scroll", direction]
        if pixels:
            cmd_args.append(str(pixels))
        await self._run(*cmd_args)

    async def scroll_into_view(self, selector: str) -> None:
        """Scroll element into view"""
        await self._run("scroll-into-view", selector)

    async def drag(
        self,
        source: str,
        target: str,
    ) -> None:
        """Drag element to target"""
        await self._run("drag", source, target)

    async def upload(self, selector: str, file_path: str) -> None:
        """Upload file to input element"""
        await self._run("upload", selector, file_path)

    # Information retrieval
    async def get_text(self, selector: str) -> str:
        """Get text content of element"""
        return await self._run("get", "text", selector, json_output=True)

    async def get_html(self, selector: str) -> str:
        """Get HTML of element"""
        return await self._run("get", "html", selector, json_output=True)

    async def get_value(self, selector: str) -> str:
        """Get value of input element"""
        return await self._run("get", "value", selector, json_output=True)

    async def get_attr(self, selector: str, attr: str) -> str:
        """Get attribute value of element"""
        return await self._run("get", "attr", selector, attr, json_output=True)

    async def get_title(self) -> str:
        """Get page title"""
        return await self._run("get", "title", json_output=True)

    async def get_url(self) -> str:
        """Get current URL"""
        return await self._run("get", "url", json_output=True)

    async def get_count(self, selector: str) -> int:
        """Get count of matching elements"""
        return await self._run("get", "count", selector, json_output=True)

    async def get_box(self, selector: str) -> Dict[str, float]:
        """Get bounding box of element (x, y, width, height)"""
        return await self._run("get", "box", selector, json_output=True)

    async def is_visible(self, selector: str) -> bool:
        """Check if element is visible"""
        return await self._run("is", "visible", selector, json_output=True)

    async def is_enabled(self, selector: str) -> bool:
        """Check if element is enabled"""
        return await self._run("is", "enabled", selector, json_output=True)

    async def is_checked(self, selector: str) -> bool:
        """Check if checkbox is checked"""
        return await self._run("is", "checked", selector, json_output=True)

    # Snapshot
    async def snapshot(
        self,
        interactive_only: bool = False,
        compact: bool = False,
        depth: int = 5,
        selector: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get accessibility tree snapshot with refs

        Args:
            interactive_only: Only interactive elements
            compact: Compact output
            depth: Tree depth
            selector: Root selector

        Returns:
            Dict with 'tree' and 'refs' keys
        """
        cmd_args = ["snapshot"]
        if interactive_only:
            cmd_args.append("--interactive-only")
        if compact:
            cmd_args.append("--compact")
        if depth != 5:
            cmd_args.extend(["--depth", str(depth)])
        if selector:
            cmd_args.extend(["--selector", selector])

        return await self._run(*cmd_args, json_output=True)

    # Screenshot & PDF
    async def screenshot(
        self, path: Optional[str] = None, full_page: bool = False
    ) -> Optional[str]:
        """
        Take screenshot

        Args:
            path: File path to save (PNG)
            full_page: Capture full scrollable page

        Returns:
            Base64-encoded PNG if no path, else None
        """
        cmd_args = ["screenshot"]
        if path:
            cmd_args.append(path)
        if full_page:
            cmd_args.append("--full-page")

        result = await self._run(*cmd_args)
        return result if not path else None

    async def pdf(self, path: str) -> None:
        """Generate PDF of page"""
        await self._run("pdf", path)

    # Wait
    async def wait(
        self,
        selector_or_ms: Optional[Union[str, int]] = None,
        text: Optional[str] = None,
        url: Optional[str] = None,
        load_state: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        """
        Wait for condition

        Args:
            selector_or_ms: Selector to wait for or milliseconds to wait
            text: Text content to wait for
            url: URL pattern to wait for
            load_state: 'load', 'domcontentloaded', 'networkidle'
            timeout: Maximum wait time in ms
        """
        cmd_args = ["wait"]

        if selector_or_ms is not None:
            cmd_args.append(str(selector_or_ms))

        if text:
            cmd_args.extend(["--text", text])
        if url:
            cmd_args.extend(["--url", url])
        if load_state:
            cmd_args.extend(["--state", load_state])
        if timeout:
            cmd_args.extend(["--timeout", str(timeout)])

        await self._run(*cmd_args)

    # Mouse
    async def mouse_move(self, x: int, y: int) -> None:
        """Move mouse to position"""
        await self._run("mouse", "move", str(x), str(y))

    async def mouse_down(self, button: str = "left") -> None:
        """Press mouse button"""
        await self._run("mouse", "down", button)

    async def mouse_up(self, button: str = "left") -> None:
        """Release mouse button"""
        await self._run("mouse", "up", button)

    async def mouse_wheel(self, delta: int) -> None:
        """Scroll mouse wheel"""
        await self._run("mouse", "wheel", str(delta))

    # Settings
    async def set_viewport(self, width: int, height: int) -> None:
        """Set viewport size"""
        await self._run("set", "viewport", str(width), str(height))

    async def set_device(self, device_name: str) -> None:
        """Emulate device (e.g., 'iPhone 14')"""
        await self._run("set", "device", device_name)

    async def set_geolocation(self, latitude: float, longitude: float) -> None:
        """Set geolocation"""
        await self._run("set", "geolocation", str(latitude), str(longitude))

    async def set_offline(self, offline: bool = True) -> None:
        """Toggle offline mode"""
        await self._run("set", "offline", str(offline).lower())

    async def set_headers(self, headers: Dict[str, str]) -> None:
        """Set HTTP headers"""
        headers_json = json.dumps(headers)
        await self._run("set", "headers", headers_json)

    # Cookies
    async def get_cookies(self) -> List[Dict[str, Any]]:
        """Get all cookies"""
        return await self._run("cookies", "get", json_output=True)

    async def set_cookie(
        self, name: str, value: str, domain: Optional[str] = None
    ) -> None:
        """Set cookie"""
        cmd_args = ["cookies", "set", name, value]
        if domain:
            cmd_args.extend(["--domain", domain])
        await self._run(*cmd_args)

    async def clear_cookies(self) -> None:
        """Clear all cookies"""
        await self._run("cookies", "clear")

    # Storage
    async def get_local_storage(self) -> Dict[str, str]:
        """Get localStorage data"""
        return await self._run("storage", "get", "local", json_output=True)

    async def set_local_storage(self, key: str, value: str) -> None:
        """Set localStorage item"""
        await self._run("storage", "set", "local", key, value)

    async def clear_local_storage(self) -> None:
        """Clear localStorage"""
        await self._run("storage", "clear", "local")

    async def get_session_storage(self) -> Dict[str, str]:
        """Get sessionStorage data"""
        return await self._run("storage", "get", "session", json_output=True)

    async def set_session_storage(self, key: str, value: str) -> None:
        """Set sessionStorage item"""
        await self._run("storage", "set", "session", key, value)

    async def clear_session_storage(self) -> None:
        """Clear sessionStorage"""
        await self._run("storage", "clear", "session")

    # Network
    async def network_route(
        self,
        url_pattern: str,
        abort: bool = False,
        body: Optional[Union[str, Dict]] = None,
    ) -> None:
        """
        Route/mock network requests

        Args:
            url_pattern: URL pattern to match
            abort: Abort matching requests
            body: Response body (string or dict for JSON)
        """
        cmd_args = ["network", "route", url_pattern]
        if abort:
            cmd_args.append("--abort")
        if body:
            body_json = json.dumps(body) if isinstance(body, dict) else body
            cmd_args.extend(["--body", body_json])
        await self._run(*cmd_args)

    async def network_requests(self, filter_text: Optional[str] = None) -> List[Dict]:
        """Get captured network requests"""
        cmd_args = ["network", "requests"]
        if filter_text:
            cmd_args.extend(["--filter", filter_text])
        return await self._run(*cmd_args, json_output=True)

    # Tabs
    async def list_tabs(self) -> List[Dict[str, Any]]:
        """List all tabs"""
        return await self._run("tabs", "list", json_output=True)

    async def new_tab(self, url: Optional[str] = None) -> None:
        """Open new tab"""
        cmd_args = ["tabs", "new"]
        if url:
            cmd_args.append(url)
        await self._run(*cmd_args)

    async def switch_tab(self, index: int) -> None:
        """Switch to tab by index"""
        await self._run("tabs", "switch", str(index))

    async def close_tab(self, index: Optional[int] = None) -> None:
        """Close tab (current if no index)"""
        cmd_args = ["tabs", "close"]
        if index is not None:
            cmd_args.append(str(index))
        await self._run(*cmd_args)

    # Frames
    async def list_frames(self) -> List[str]:
        """List all frames"""
        return await self._run("frames", "list", json_output=True)

    async def switch_frame(self, selector: str) -> None:
        """Switch to frame"""
        await self._run("frames", "switch", selector)

    async def switch_main_frame(self) -> None:
        """Switch to main frame"""
        await self._run("frames", "main")

    # Dialogs
    async def accept_dialog(self, text: Optional[str] = None) -> None:
        """Accept dialog (alert/confirm/prompt)"""
        cmd_args = ["dialog", "accept"]
        if text:
            cmd_args.append(text)
        await self._run(*cmd_args)

    async def dismiss_dialog(self) -> None:
        """Dismiss dialog"""
        await self._run("dialog", "dismiss")

    # Debug
    async def trace_start(self, output_path: str) -> None:
        """Start trace recording"""
        await self._run("trace", "start", output_path)

    async def trace_stop(self) -> None:
        """Stop trace recording"""
        await self._run("trace", "stop")

    async def console(self) -> List[str]:
        """Get console messages"""
        return await self._run("console", json_output=True)

    async def errors(self) -> List[str]:
        """Get page errors"""
        return await self._run("errors", json_output=True)

    async def highlight(self, selector: str) -> None:
        """Highlight element"""
        await self._run("highlight", selector)

    # Session management
    async def close(self) -> None:
        """Close current browser session"""
        await self._run("close")

    @staticmethod
    async def list_sessions() -> List[str]:
        """List all active browser sessions"""
        cmd = ["agent-browser", "sessions", "--json"]
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await process.communicate()

        if process.returncode == 0 and stdout:
            try:
                data = json.loads(stdout.decode().strip())
                return data.get("data", [])
            except json.JSONDecodeError:
                pass
        return []

    async def get_current_session(self) -> Optional[str]:
        """Get current session name"""
        return self.session

    async def is_session_active(self) -> bool:
        """Check if current session is active"""
        if not self.session:
            return False
        sessions = await self.list_sessions()
        return self.session in sessions

    @staticmethod
    async def close_all_sessions(max_retries: int = 2, retry_delay: float = 0.5):
        """
        Close all active browser sessions with retry logic

        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds

        Returns:
            Number of sessions closed
        """
        closed_count = 0

        for attempt in range(max_retries + 1):
            sessions = await AsyncAgentBrowser.list_sessions()

            if not sessions:
                break

            for session in sessions:
                try:
                    browser = AsyncAgentBrowser(session=session)
                    await browser.close()
                    closed_count += 1
                except Exception:
                    pass

            if attempt < max_retries:
                await asyncio.sleep(retry_delay)

        return closed_count

    @staticmethod
    async def shutdown(verbose: bool = False) -> Dict[str, Any]:
        """
        Complete shutdown: close all sessions and verify cleanup

        Args:
            verbose: Print detailed information

        Returns:
            Dict with sessions_closed, cleanup_performed, remaining_sessions
        """
        if verbose:
            print("Shutting down all browser sessions...")

        closed_count = await AsyncAgentBrowser.close_all_sessions()

        await asyncio.sleep(1)

        remaining_sessions = await AsyncAgentBrowser.list_sessions()

        result = {
            "sessions_closed": closed_count,
            "cleanup_performed": True,
            "remaining_sessions": remaining_sessions,
        }

        if verbose:
            print(f"Closed {closed_count} session(s)")
            if remaining_sessions:
                print(f"Warning: {len(remaining_sessions)} session(s) still active")
            else:
                print("All sessions successfully closed")

        return result

    # Batch execution
    def batch(self) -> AsyncBatchContext:
        """Create batch context for multiple commands"""
        return AsyncBatchContext(self)

    async def execute_batch(self, commands: List[Dict[str, Any]]) -> List[Any]:
        """
        Execute multiple commands in a single subprocess call

        Args:
            commands: List of command dictionaries with 'method', 'args', 'kwargs'

        Returns:
            List of results (one per command)
        """
        script_lines = ["#!/bin/bash", "set -e"]

        for cmd_dict in commands:
            method = cmd_dict["method"]
            args = cmd_dict.get("args", [])
            kwargs = cmd_dict.get("kwargs", {})
            json_flag = kwargs.get("json_output", False)

            if method == "get":
                cmd_parts = self._build_command("get", *args, json_output=json_flag)
            elif method == "snapshot":
                interactive_only = kwargs.get("interactive_only", False)
                compact = kwargs.get("compact", False)
                cmd_parts = ["agent-browser"]
                if self.session:
                    cmd_parts.extend(["--session", self.session])
                cmd_parts.append("snapshot")
                if interactive_only:
                    cmd_parts.append("--interactive-only")
                if compact:
                    cmd_parts.append("--compact")
                cmd_parts.append("--json")
            elif method == "open":
                headers = kwargs.get("headers")
                cmd_parts = ["agent-browser"]
                if self.session:
                    cmd_parts.extend(["--session", self.session])
                cmd_parts.extend(["open", *args])
                if headers:
                    cmd_parts.extend(["--headers", json.dumps(headers)])
            else:
                cmd_parts = self._build_command(method, *args)

            script_lines.append(" ".join(f'"{p}"' for p in cmd_parts))

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".sh", delete=False
        ) as script_file:
            script_file.write("\n".join(script_lines))
            script_path = script_file.name

        try:
            process = await asyncio.create_subprocess_exec(
                "bash",
                script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode().strip() if stderr else "Unknown error"
                raise AgentBrowserError(f"Batch execution failed: {error_msg}")

            output_lines = stdout.decode().strip().split("\n")
            results = []

            for line in output_lines:
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    if isinstance(data, dict) and "success" in data:
                        if not data.get("success"):
                            raise AgentBrowserError(data.get("error", "Command failed"))
                        results.append(data.get("data"))
                    else:
                        results.append(data)
                except json.JSONDecodeError:
                    results.append(line)

            return results

        finally:
            try:
                os.unlink(script_path)
            except Exception:
                pass
