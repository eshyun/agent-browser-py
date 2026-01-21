# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-01-21

### Added
- **Batch Execution** - Execute multiple commands in single subprocess call
  - `browser.batch()` - Context manager for batch execution
  - `browser.execute_batch()` - Direct batch execution method
  - `BatchContext` - Fluent API for command chaining
  - Supports all major commands: open, click, fill, get_*, screenshot, etc.
  - Performance improvement: 20-40% faster for 5+ commands
- `example_batch.py` - Comprehensive batch execution examples
- 6 new batch execution tests

### Performance
- Batch execution reduces subprocess overhead
- Best for 5-20 sequential commands
- ~25ms per command in batch vs ~28ms sequential

## [0.1.4] - 2026-01-21

### Added
- `AgentBrowser.shutdown()` - Complete cleanup with verification (static method)
  - Closes all sessions and waits for cleanup
  - Returns detailed result dict with sessions_closed, cleanup_performed, remaining_sessions
  - Supports `verbose` parameter for status messages
- `AgentBrowser.register_shutdown_hook()` - Auto-cleanup on program exit (static method)
  - Uses Python's atexit to register cleanup
  - Supports verbose mode
  - Ensures clean exit even if sessions are left open
- shutdown_example and auto_shutdown_example in example_usage.py
- Comprehensive documentation in README

## [0.1.3] - 2026-01-21

### Added
- `AgentBrowser.close_all_sessions()` - Close all active browser sessions at once (static method)
  - Supports `max_retries` parameter (default: 2)
  - Automatically retries with 0.5s delay between attempts
  - Returns total count of closed sessions
- close_all_sessions_example in example_usage.py
- Documentation and examples in README

## [0.1.2] - 2026-01-21

### Added
- Session management methods:
  - `AgentBrowser.list_sessions()` - List all active browser sessions (static method)
  - `browser.get_current_session()` - Get current session name
  - `browser.is_session_active()` - Check if session is active
- Session management example in example_usage.py
- Documentation for session management in README

### Fixed
- Removed unnecessary `benedict` import

## [0.1.1] - 2026-01-21

### Fixed
- Fixed JSON response parsing for get methods (get_text, get_html, get_value, get_attr, get_title, get_url, get_count, get_box)
- Now properly extracts values from nested JSON responses returned by agent-browser CLI

## [0.1.0] - 2026-01-21

### Added
- Initial implementation of AgentBrowser Python wrapper
- Comprehensive examples for get_value, get_attr, get_count, get_box methods
- Support for all major agent-browser CLI commands:
  - Navigation (open, back, forward, reload)
  - Actions (click, fill, type, hover, check, scroll, etc.)
  - Information retrieval (get_text, get_html, get_value, etc.)
  - State checks (is_visible, is_enabled, is_checked)
  - Snapshot with refs support
  - Screenshot and PDF generation
  - Wait conditions
  - Mouse control
  - Browser settings (viewport, device emulation, geolocation, etc.)
  - Cookies and storage management
  - Network interception
  - Tab management
  - Frame switching
  - Dialog handling
  - Debug tools (trace, console, errors)
- Context manager support (`with AgentBrowser() as browser:`)
- Multi-session support
- JSON output parsing
- Custom error handling with `AgentBrowserError`
- Comprehensive test suite with 25+ tests
- Example usage scripts
- Complete documentation in README.md

### Features
- Subprocess-based communication with agent-browser CLI
- Automatic JSON parsing for structured data
- Support for headed/headless modes
- CDP (Chrome DevTools Protocol) support
- Custom browser executable path support
- HTTP headers configuration
