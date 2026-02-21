# Implementation Details

## Architecture

### Overview
The `agent-browser-wrapper` is a Python wrapper that communicates with the `agent-browser` CLI tool via subprocess. It provides a Pythonic API while leveraging the battle-tested agent-browser implementation.

### Design Decisions

#### 1. Subprocess-based Communication
**Why**: Instead of reimplementing browser automation, we delegate to the agent-browser CLI
- **Pros**: 
  - Leverage existing, well-tested implementation
  - Automatic updates when agent-browser improves
  - No need to maintain browser automation logic
- **Cons**: 
  - Requires agent-browser installation
  - Subprocess overhead (minimal for browser operations)

#### 2. JSON Output Parsing
All methods that return data use `--json` flag to get structured output
- Consistent error handling
- Type-safe data access
- Easy to parse and validate

#### 3. Context Manager Support
```python
with AgentBrowser() as browser:
    # Automatically closes browser on exit
```
- Ensures proper cleanup
- Pythonic resource management
- Exception-safe

Context manager cleanup can be controlled via `auto_close`.

For process-level cleanup, instances can opt-in to registering a per-instance atexit hook via `close_on_exit`.

#### 4. Method Naming
Python conventions instead of CLI conventions:
- `get_text()` instead of `get text`
- `scroll_into_view()` instead of `scrollintoview`
- `is_visible()` instead of `is visible`

#### 5. Page-level Content Retrieval
Page 전체 HTML/Text는 `agent-browser`의 `eval` 서브커맨드로 구현한다.
- `get_page("html")` => `eval("document.documentElement.outerHTML")`
- `get_page("text")` => `eval("document.body.innerText")`

기존 `get_content()`는 하위 호환을 위해 유지하며, 내부적으로 `get_page("html")`로 위임한다.

Batch 모드에서도 동일한 방식으로 `eval` 명령을 큐잉하여 페이지 HTML/Text를 가져온다.

### Class Structure

```
AgentBrowser
├── __init__()           # Configuration
├── _build_command()     # Command builder
├── _run()              # Command executor
├── Navigation methods   # open, back, forward, reload
├── Action methods       # click, fill, type, hover, etc.
├── Info methods         # get_text, get_html, is_visible, etc.
├── Page methods         # get_page, get_content
├── Snapshot methods     # snapshot with filtering options
├── Media methods        # screenshot, pdf
├── Wait methods         # wait with various conditions
├── Mouse methods        # mouse_move, mouse_down, etc.
├── Settings methods     # set_viewport, set_device, etc.
├── Cookie methods       # get/set/clear cookies
├── Storage methods      # localStorage and sessionStorage
├── Network methods      # route, unroute, requests
├── Tab methods          # list, new, switch, close tabs
├── Frame methods        # switch to iframe
├── Dialog methods       # accept, dismiss dialogs
├── Debug methods        # trace, console, errors
└── Session methods      # connect, close
```

### Error Handling

Custom exception `AgentBrowserError`:
- Raised when agent-browser command fails
- Contains stderr output or JSON error message
- Allows graceful error recovery

### Command Building

`_build_command()` method:
1. Start with base command: `["agent-browser"]`
2. Add global options (session, executable-path, headed, debug, cdp)
3. Add JSON flag if structured output needed
4. Add command-specific arguments

Example:
```python
# Input: click("@e2")
# Output: ["agent-browser", "--session", "test", "--json", "click", "@e2"]
```

### JSON Parsing

Response format from agent-browser:
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

Or on error:
```json
{
  "success": false,
  "data": null,
  "error": "Error message"
}
```

## Testing Strategy

### Unit Tests
- Initialization tests: Verify constructor parameters
- Command building tests: Verify CLI command construction
- API signature tests: Ensure all methods exist
- Exception tests: Verify error handling

### Integration Tests
Not included yet, would require:
- agent-browser CLI installed
- Mock or real web server
- Browser automation scenarios

## Future Enhancements

### Potential Improvements
1. **Async Support**: Add async/await API
   ```python
   async with AsyncAgentBrowser() as browser:
       await browser.open("https://example.com")
   ```

2. **Type Hints**: Add more specific return types
   ```python
   def get_text(self, selector: str) -> str: ...
   ```

3. **Retry Logic**: Add automatic retries for flaky operations
   ```python
   @retry(max_attempts=3)
   def click(self, selector: str) -> None: ...
   ```

4. **Recording**: Add action recording for test generation
   ```python
   browser.start_recording()
   # ... actions ...
   browser.save_recording("test.py")
   ```

5. **Plugin System**: Allow extending with custom commands
   ```python
   @browser.register_command
   def custom_action(self, arg): ...
   ```

## Dependencies

### Runtime
- Python >= 3.13
- agent-browser CLI (external dependency)
- Chromium browser (installed via agent-browser)

### Development
- pytest >= 8.3.4
- uv (package manager)

## File Structure

```
agent-browser/
├── agent_browser.py      # Main implementation
├── example_usage.py      # Usage examples
├── main.py              # Demo script
├── tests/
│   └── test_agent_browser.py  # Unit tests
├── pyproject.toml       # Project configuration
├── README.md            # User documentation
├── CHANGELOG.md         # Version history
└── IMPLEMENTATION.md    # This file
```

## Performance Considerations

### Subprocess Overhead
- Each command spawns new process: ~10-50ms overhead
- Minimal compared to browser operations (100ms+)
- Consider batching commands if performance critical

### Memory Usage
- No browser in Python process (runs in agent-browser daemon)
- Minimal memory footprint (<10MB)
- Multiple sessions = multiple browser processes

### Concurrency
- Multiple `AgentBrowser` instances = safe (different sessions)
- Same session across instances = not safe (state conflicts)
- Use different session names for parallel automation

## Security Considerations

### Command Injection
- All arguments passed as list, not shell string
- No shell=True in subprocess.run()
- Safe from command injection

### Sensitive Data
- Avoid passing credentials in commands (visible in process list)
- Use state files for authentication
- Clear cookies/storage after sensitive operations

### Network Security
- Headers scoped to origin by default
- Use CDP over localhost only
- Be cautious with network interception
