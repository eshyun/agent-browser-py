import pytest
from agent_browser import AgentBrowser, AgentBrowserError


class TestAgentBrowserInit:
    def test_basic_init(self):
        browser = AgentBrowser()
        assert browser.session is None
        assert browser.executable_path is None
        assert browser.headed is False
        assert browser.debug is False

    def test_init_with_options(self):
        browser = AgentBrowser(
            session="test-session", headed=True, debug=True, cdp_port=9222
        )
        assert browser.session == "test-session"
        assert browser.headed is True
        assert browser.debug is True
        assert browser.cdp_port == 9222


class TestCommandBuilding:
    def test_build_basic_command(self):
        browser = AgentBrowser()
        cmd = browser._build_command("open", "https://example.com")
        assert cmd == ["agent-browser", "open", "https://example.com"]

    def test_build_command_with_session(self):
        browser = AgentBrowser(session="test")
        cmd = browser._build_command("open", "https://example.com")
        assert "--session" in cmd
        assert "test" in cmd

    def test_build_command_with_json_output(self):
        browser = AgentBrowser()
        cmd = browser._build_command("snapshot", json_output=True)
        assert "--json" in cmd

    def test_build_command_with_headed(self):
        browser = AgentBrowser(headed=True)
        cmd = browser._build_command("open", "https://example.com")
        assert "--headed" in cmd

    def test_build_command_with_debug(self):
        browser = AgentBrowser(debug=True)
        cmd = browser._build_command("open", "https://example.com")
        assert "--debug" in cmd

    def test_build_command_with_cdp(self):
        browser = AgentBrowser(cdp_port=9222)
        cmd = browser._build_command("snapshot")
        assert "--cdp" in cmd
        assert "9222" in cmd


class TestContextManager:
    def test_context_manager(self):
        browser = AgentBrowser()
        assert browser.__enter__() is browser

    def test_context_manager_exit(self):
        browser = AgentBrowser()
        result = browser.__exit__(None, None, None)
        assert result is False


class TestAPISignatures:
    def test_navigation_methods_exist(self):
        browser = AgentBrowser()
        assert hasattr(browser, "open")
        assert hasattr(browser, "goto")
        assert hasattr(browser, "back")
        assert hasattr(browser, "forward")
        assert hasattr(browser, "reload")

    def test_action_methods_exist(self):
        browser = AgentBrowser()
        assert hasattr(browser, "click")
        assert hasattr(browser, "dblclick")
        assert hasattr(browser, "fill")
        assert hasattr(browser, "type")
        assert hasattr(browser, "press")
        assert hasattr(browser, "hover")
        assert hasattr(browser, "check")
        assert hasattr(browser, "uncheck")

    def test_info_methods_exist(self):
        browser = AgentBrowser()
        assert hasattr(browser, "get_text")
        assert hasattr(browser, "get_html")
        assert hasattr(browser, "get_value")
        assert hasattr(browser, "get_title")
        assert hasattr(browser, "get_url")
        assert hasattr(browser, "is_visible")
        assert hasattr(browser, "is_enabled")

    def test_snapshot_method_exists(self):
        browser = AgentBrowser()
        assert hasattr(browser, "snapshot")

    def test_screenshot_methods_exist(self):
        browser = AgentBrowser()
        assert hasattr(browser, "screenshot")
        assert hasattr(browser, "pdf")

    def test_wait_method_exists(self):
        browser = AgentBrowser()
        assert hasattr(browser, "wait")

    def test_mouse_methods_exist(self):
        browser = AgentBrowser()
        assert hasattr(browser, "mouse_move")
        assert hasattr(browser, "mouse_down")
        assert hasattr(browser, "mouse_up")
        assert hasattr(browser, "mouse_wheel")

    def test_settings_methods_exist(self):
        browser = AgentBrowser()
        assert hasattr(browser, "set_viewport")
        assert hasattr(browser, "set_device")
        assert hasattr(browser, "set_geolocation")
        assert hasattr(browser, "set_offline")

    def test_cookie_methods_exist(self):
        browser = AgentBrowser()
        assert hasattr(browser, "get_cookies")
        assert hasattr(browser, "set_cookie")
        assert hasattr(browser, "clear_cookies")

    def test_storage_methods_exist(self):
        browser = AgentBrowser()
        assert hasattr(browser, "get_local_storage")
        assert hasattr(browser, "set_local_storage")
        assert hasattr(browser, "clear_local_storage")
        assert hasattr(browser, "get_session_storage")
        assert hasattr(browser, "set_session_storage")
        assert hasattr(browser, "clear_session_storage")

    def test_network_methods_exist(self):
        browser = AgentBrowser()
        assert hasattr(browser, "network_route")
        assert hasattr(browser, "network_unroute")
        assert hasattr(browser, "network_requests")

    def test_tab_methods_exist(self):
        browser = AgentBrowser()
        assert hasattr(browser, "list_tabs")
        assert hasattr(browser, "new_tab")
        assert hasattr(browser, "switch_tab")
        assert hasattr(browser, "close_tab")

    def test_session_methods_exist(self):
        browser = AgentBrowser()
        assert hasattr(browser, "connect")
        assert hasattr(browser, "close")
        assert hasattr(browser, "quit")


class TestExceptionHandling:
    def test_exception_type(self):
        assert issubclass(AgentBrowserError, Exception)

    def test_exception_message(self):
        error = AgentBrowserError("Test error")
        assert str(error) == "Test error"


class TestExampleUsage:
    def test_example_file_imports(self):
        import example_usage

        assert hasattr(example_usage, "basic_example")
        assert hasattr(example_usage, "context_manager_example")
        assert hasattr(example_usage, "session_example")
        assert hasattr(example_usage, "refs_workflow")
        assert hasattr(example_usage, "get_methods_example")
        assert hasattr(example_usage, "advanced_get_example")
        assert hasattr(example_usage, "form_interaction_example")
        assert hasattr(example_usage, "session_management_example")
        assert hasattr(example_usage, "close_all_sessions_example")
        assert hasattr(example_usage, "shutdown_example")
        assert hasattr(example_usage, "auto_shutdown_example")


class TestSessionManagement:
    def test_list_sessions_exists(self):
        assert hasattr(AgentBrowser, "list_sessions")
        assert callable(AgentBrowser.list_sessions)

    def test_list_sessions_returns_list(self):
        sessions = AgentBrowser.list_sessions()
        assert isinstance(sessions, list)

    def test_get_current_session_exists(self):
        browser = AgentBrowser()
        assert hasattr(browser, "get_current_session")
        assert callable(browser.get_current_session)

    def test_is_session_active_exists(self):
        browser = AgentBrowser()
        assert hasattr(browser, "is_session_active")
        assert callable(browser.is_session_active)

    def test_close_all_sessions_exists(self):
        assert hasattr(AgentBrowser, "close_all_sessions")
        assert callable(AgentBrowser.close_all_sessions)

    def test_close_all_sessions_returns_int(self):
        closed = AgentBrowser.close_all_sessions()
        assert isinstance(closed, int)
        assert closed >= 0

    def test_shutdown_exists(self):
        assert hasattr(AgentBrowser, "shutdown")
        assert callable(AgentBrowser.shutdown)

    def test_shutdown_returns_dict(self):
        result = AgentBrowser.shutdown(wait=False)
        assert isinstance(result, dict)
        assert "sessions_closed" in result
        assert "cleanup_performed" in result
        assert "remaining_sessions" in result
        assert isinstance(result["sessions_closed"], int)
        assert isinstance(result["cleanup_performed"], bool)
        assert isinstance(result["remaining_sessions"], list)

    def test_register_shutdown_hook_exists(self):
        assert hasattr(AgentBrowser, "register_shutdown_hook")
        assert callable(AgentBrowser.register_shutdown_hook)


class TestBatchExecution:
    def test_batch_method_exists(self):
        browser = AgentBrowser()
        assert hasattr(browser, "batch")
        assert callable(browser.batch)
    
    def test_execute_batch_method_exists(self):
        browser = AgentBrowser()
        assert hasattr(browser, "execute_batch")
        assert callable(browser.execute_batch)
    
    def test_batch_context_manager(self):
        browser = AgentBrowser()
        batch_ctx = browser.batch()
        assert batch_ctx is not None
        assert hasattr(batch_ctx, "__enter__")
        assert hasattr(batch_ctx, "__exit__")
    
    def test_batch_context_has_methods(self):
        browser = AgentBrowser()
        with browser.batch() as b:
            assert hasattr(b, "open")
            assert hasattr(b, "click")
            assert hasattr(b, "fill")
            assert hasattr(b, "get_title")
            assert hasattr(b, "screenshot")
    
    def test_batch_context_chaining(self):
        browser = AgentBrowser()
        with browser.batch() as b:
            result = b.open("https://example.com")
            assert result is b
            result = b.get_title()
            assert result is b
    
    def test_execute_batch_with_empty_list(self):
        browser = AgentBrowser()
        results = browser.execute_batch([])
        assert results == []
