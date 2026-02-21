"""
Tests for AsyncAgentBrowser
"""

import pytest
import asyncio
import sys
import atexit
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_browser import AsyncAgentBrowser, AgentBrowserError
from agent_browser.async_agent_browser import AsyncBatchContext


class TestAsyncAgentBrowserInit:
    def test_init_default(self):
        browser = AsyncAgentBrowser()
        assert browser.session is None
        assert browser.executable_path is None
        assert browser.headers is None
        assert browser.headed is False
        assert browser.debug is False
        assert browser.cdp_port is None
        assert browser.auto_close is True
        assert browser.close_on_exit is False

    def test_init_with_session(self):
        browser = AsyncAgentBrowser(session="test-session")
        assert browser.session == "test-session"

    def test_init_with_all_options(self):
        browser = AsyncAgentBrowser(
            session="test",
            executable_path="/usr/bin/chromium",
            headers={"X-Test": "value"},
            headed=True,
            debug=True,
            cdp_port=9222,
        )
        assert browser.session == "test"
        assert browser.executable_path == "/usr/bin/chromium"
        assert browser.headers == {"X-Test": "value"}
        assert browser.headed is True
        assert browser.debug is True
        assert browser.cdp_port == 9222


class TestAsyncCommandBuilding:
    def test_build_command_minimal(self):
        browser = AsyncAgentBrowser()
        cmd = browser._build_command("open", "https://example.com")
        assert cmd == ["agent-browser", "open", "https://example.com"]

    def test_build_command_with_session(self):
        browser = AsyncAgentBrowser(session="test")
        cmd = browser._build_command("open", "https://example.com")
        assert cmd == [
            "agent-browser",
            "--session",
            "test",
            "open",
            "https://example.com",
        ]

    def test_build_command_with_json_flag(self):
        browser = AsyncAgentBrowser()
        cmd = browser._build_command("snapshot", json_output=True)
        assert cmd == ["agent-browser", "--json", "snapshot"]

    def test_build_command_with_all_options(self):
        browser = AsyncAgentBrowser(
            session="test",
            executable_path="/usr/bin/chromium",
            headed=True,
            debug=True,
            cdp_port=9222,
        )
        cmd = browser._build_command("click", "@e1")
        assert "--session" in cmd
        assert "test" in cmd
        assert "--executable-path" in cmd
        assert "/usr/bin/chromium" in cmd
        assert "--headed" in cmd
        assert "--debug" in cmd
        assert "--cdp" in cmd
        assert "9222" in cmd


class TestAsyncAPISignatures:
    @pytest.mark.asyncio
    async def test_navigation_methods_exist(self):
        browser = AsyncAgentBrowser()
        assert hasattr(browser, "open")
        assert hasattr(browser, "goto")
        assert hasattr(browser, "back")
        assert hasattr(browser, "forward")
        assert hasattr(browser, "reload")

        assert asyncio.iscoroutinefunction(browser.open)
        assert asyncio.iscoroutinefunction(browser.goto)
        assert asyncio.iscoroutinefunction(browser.back)

    @pytest.mark.asyncio
    async def test_action_methods_exist(self):
        browser = AsyncAgentBrowser()
        assert hasattr(browser, "click")
        assert hasattr(browser, "dblclick")
        assert hasattr(browser, "fill")
        assert hasattr(browser, "type")
        assert hasattr(browser, "press")
        assert hasattr(browser, "hover")

        assert asyncio.iscoroutinefunction(browser.click)
        assert asyncio.iscoroutinefunction(browser.fill)

    @pytest.mark.asyncio
    async def test_info_methods_exist(self):
        browser = AsyncAgentBrowser()
        assert hasattr(browser, "get_text")
        assert hasattr(browser, "get_html")
        assert hasattr(browser, "get_value")
        assert hasattr(browser, "get_attr")
        assert hasattr(browser, "get_title")
        assert hasattr(browser, "get_url")
        assert hasattr(browser, "get_page")
        assert hasattr(browser, "get_content")
        assert hasattr(browser, "eval")

        assert asyncio.iscoroutinefunction(browser.get_text)
        assert asyncio.iscoroutinefunction(browser.get_title)

    @pytest.mark.asyncio
    async def test_snapshot_method_exists(self):
        browser = AsyncAgentBrowser()
        assert hasattr(browser, "snapshot")
        assert asyncio.iscoroutinefunction(browser.snapshot)

    @pytest.mark.asyncio
    async def test_media_methods_exist(self):
        browser = AsyncAgentBrowser()
        assert hasattr(browser, "screenshot")
        assert hasattr(browser, "pdf")
        assert asyncio.iscoroutinefunction(browser.screenshot)
        assert asyncio.iscoroutinefunction(browser.pdf)


class TestAsyncSessionManagement:
    @pytest.mark.asyncio
    async def test_list_sessions_static_method(self):
        sessions = await AsyncAgentBrowser.list_sessions()
        assert isinstance(sessions, list)

    @pytest.mark.asyncio
    async def test_get_current_session(self):
        browser = AsyncAgentBrowser(session="test-session")
        current = await browser.get_current_session()
        assert current == "test-session"

    @pytest.mark.asyncio
    async def test_get_current_session_none(self):
        browser = AsyncAgentBrowser()
        current = await browser.get_current_session()
        assert current is None

    @pytest.mark.asyncio
    async def test_is_session_active_no_session(self):
        browser = AsyncAgentBrowser()
        is_active = await browser.is_session_active()
        assert is_active is False

    @pytest.mark.asyncio
    async def test_close_all_sessions_exists(self):
        result = await AsyncAgentBrowser.close_all_sessions()
        assert isinstance(result, int)

    @pytest.mark.asyncio
    async def test_shutdown_exists(self):
        result = await AsyncAgentBrowser.shutdown(verbose=False)
        assert isinstance(result, dict)
        assert "sessions_closed" in result
        assert "cleanup_performed" in result
        assert "remaining_sessions" in result


class TestAsyncBatchContext:
    def test_batch_context_creation(self):
        browser = AsyncAgentBrowser()
        batch = browser.batch()
        assert isinstance(batch, AsyncBatchContext)
        assert batch.browser is browser
        assert batch.commands == []
        assert batch.results == []

    def test_batch_fluent_api(self):
        browser = AsyncAgentBrowser()
        batch = browser.batch()

        result = (
            batch.open("https://example.com")
            .click("@e1")
            .fill("@e2", "text")
            .wait("h1")
        )

        assert result is batch
        assert len(batch.commands) == 4

    def test_batch_command_structure(self):
        browser = AsyncAgentBrowser()
        batch = browser.batch()

        batch.open("https://example.com")
        batch.click("@e1")
        batch.get_title()

        assert batch.commands[0] == {"method": "open", "args": ["https://example.com"]}
        assert batch.commands[1] == {"method": "click", "args": ["@e1"]}
        assert batch.commands[2] == {
            "method": "get",
            "args": ["title"],
            "kwargs": {"json_output": True},
        }

    def test_batch_all_methods_return_self(self):
        browser = AsyncAgentBrowser()
        batch = browser.batch()

        assert batch.open("https://example.com") is batch
        assert batch.click("@e1") is batch
        assert batch.fill("@e2", "text") is batch
        assert batch.type("@e3", "text") is batch
        assert batch.press("Enter") is batch
        assert batch.hover("@e4") is batch
        assert batch.wait("1000") is batch
        assert batch.get_title() is batch
        assert batch.get_url() is batch
        assert batch.get_text("h1") is batch
        assert batch.get_page("html") is batch
        assert batch.screenshot("test.png") is batch
        assert batch.snapshot() is batch


class TestAsyncContextManager:
    @pytest.mark.asyncio
    async def test_context_manager_protocol(self):
        browser = AsyncAgentBrowser()
        assert hasattr(browser, "__aenter__")
        assert hasattr(browser, "__aexit__")

    @pytest.mark.asyncio
    async def test_aexit_calls_close_by_default(self):
        browser = AsyncAgentBrowser()
        called = {"v": False}

        async def fake_close():
            called["v"] = True

        browser.close = fake_close
        await browser.__aexit__(None, None, None)
        assert called["v"] is True

    @pytest.mark.asyncio
    async def test_aexit_does_not_call_close_when_auto_close_false(self):
        browser = AsyncAgentBrowser(auto_close=False)
        called = {"v": False}

        async def fake_close():
            called["v"] = True

        browser.close = fake_close
        await browser.__aexit__(None, None, None)
        assert called["v"] is False


class TestAsyncCloseOnExit:
    def test_close_on_exit_registers_atexit_hook(self, monkeypatch):
        calls = {"n": 0}

        def fake_register(fn):
            calls["n"] += 1
            return fn

        monkeypatch.setattr(atexit, "register", fake_register)

        AsyncAgentBrowser(close_on_exit=True)
        assert calls["n"] == 1

    def test_close_on_exit_false_does_not_register_atexit_hook(self, monkeypatch):
        calls = {"n": 0}

        def fake_register(fn):
            calls["n"] += 1
            return fn

        monkeypatch.setattr(atexit, "register", fake_register)

        AsyncAgentBrowser(close_on_exit=False)
        assert calls["n"] == 0


class TestAsyncBatchExecution:
    def test_execute_batch_method_exists(self):
        browser = AsyncAgentBrowser()
        assert hasattr(browser, "execute_batch")
        assert asyncio.iscoroutinefunction(browser.execute_batch)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
