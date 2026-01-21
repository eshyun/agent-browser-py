# Agent Browser Python Wrapper

Python wrapper for [agent-browser](https://github.com/vercel-labs/agent-browser) CLI - Browser automation for AI agents.

## Features

- 🚀 Easy-to-use Python API for agent-browser
- 🎯 Supports refs-based element selection (optimal for AI)
- 📦 All agent-browser commands available
- 🔄 Context manager support (sync & async)
- 🌐 Multi-session support
- 🎭 Headed/headless modes
- 🔍 JSON output parsing
- ⚡ Subprocess-based communication
- 🔥 **Batch execution for performance** (NEW!)
- ⚡ **Async API support** (NEW!)

## Prerequisites

You need to have `agent-browser` installed:

```bash
npm install -g agent-browser
agent-browser install
```

## Installation

```bash
uv add agent-browser-wrapper  # Not published yet
# or
pip install agent-browser-wrapper
```

## Quick Start

### Sync API

#### Basic Usage

```python
from agent_browser import AgentBrowser

browser = AgentBrowser()

browser.open("https://example.com")

snapshot = browser.snapshot(interactive_only=True)
print("Available refs:", snapshot.get('refs', {}).keys())

browser.click("@e2")
browser.fill("@e3", "test@example.com")

browser.screenshot("page.png")

browser.close()
```

### Context Manager

```python
with AgentBrowser() as browser:
    browser.open("https://example.com")
    title = browser.get_title()
    print(f"Title: {title}")
```

### Multiple Sessions

```python
browser1 = AgentBrowser(session="agent-1")
browser1.open("https://site-a.com")

browser2 = AgentBrowser(session="agent-2")
browser2.open("https://site-b.com")
```

### Headed Mode (Visible Browser)

```python
browser = AgentBrowser(headed=True)
browser.open("https://example.com")
```

### Batch Execution (Performance Optimization)

Execute multiple commands in a single subprocess call for better performance:

```python
browser = AgentBrowser()

# Context manager automatically executes on exit
with browser.batch() as b:
    b.open("https://example.com")
    b.wait("h1")
    b.get_title()
    b.get_url()
    b.get_text("h1")
    b.screenshot("page.png")

# Results available after context exit
print(b.results)
```

**Performance Benefits:**
- 5 commands: ~20-30% faster
- 10 commands: ~30-40% faster
- Best for 5-20 sequential commands

**When to use batch:**
- ✅ Multiple sequential commands on same page
- ✅ Commands don't depend on previous results
- ✅ Performance is important
- ❌ Need to check results between commands
- ❌ Conditional logic based on previous results

See [example_batch.py](./examples/example_batch.py) for more examples.

### Async API

All sync APIs have async equivalents using `AsyncAgentBrowser`:

```python
import asyncio
from agent_browser import AsyncAgentBrowser

async def main():
    async with AsyncAgentBrowser() as browser:
        await browser.open("https://example.com")
        
        title = await browser.get_title()
        print(f"Title: {title}")
        
        snapshot = await browser.snapshot(interactive_only=True)
        print(f"Found {len(snapshot.get('refs', {}))} interactive elements")

asyncio.run(main())
```

#### Async Batch Execution

```python
async def batch_example():
    browser = AsyncAgentBrowser()
    
    async with browser.batch() as b:
        b.open("https://example.com")
        b.wait("h1")
        b.get_title()
        b.get_url()
        b.get_text("h1")
    
    print(f"Results: {b.results}")
    await browser.close()
```

#### Parallel Browser Operations

```python
async def parallel_example():
    browser1 = AsyncAgentBrowser(session="session-1")
    browser2 = AsyncAgentBrowser(session="session-2")
    
    titles = await asyncio.gather(
        browser1.open("https://example.com"),
        browser2.open("https://github.com"),
    )
    
    await asyncio.gather(
        browser1.close(),
        browser2.close(),
    )
```

See [example_async_usage.py](./examples/example_async_usage.py) for more examples.

## API Reference

### Navigation

```python
browser.open(url, headers=None)
browser.goto(url)
browser.back()
browser.forward()
browser.reload()
```

### Actions

```python
browser.click(selector)
browser.dblclick(selector)
browser.fill(selector, text)
browser.type(selector, text)
browser.press(key)
browser.hover(selector)
browser.check(selector)
browser.uncheck(selector)
browser.scroll(direction, pixels=None)
browser.scroll_into_view(selector)
```

### Information

```python
browser.get_text(selector)
browser.get_html(selector)
browser.get_value(selector)
browser.get_attr(selector, attr)
browser.get_title()
browser.get_url()
browser.get_count(selector)
browser.get_box(selector)
browser.is_visible(selector)
browser.is_enabled(selector)
browser.is_checked(selector)
```

**Examples:**

```python
text = browser.get_text("h1")
value = browser.get_value("input#email")
href = browser.get_attr("a", "href")
link_count = browser.get_count("a")
box = browser.get_box("h1")
print(f"Position: ({box['x']}, {box['y']}), Size: {box['width']}x{box['height']}")
```

### Snapshot (AI-Friendly)

```python
snapshot = browser.snapshot(
    interactive_only=True,
    compact=True,
    depth=5,
    selector="#main"
)
```

### Screenshot & PDF

```python
browser.screenshot("page.png", full_page=True)
base64_png = browser.screenshot()
browser.pdf("page.pdf")
```

### Wait

```python
browser.wait("@e1")
browser.wait(1000)
browser.wait(text="Welcome")
browser.wait(url="**/dashboard")
browser.wait(load_state="networkidle")
```

### Mouse Control

```python
browser.mouse_move(100, 200)
browser.mouse_down("left")
browser.mouse_up("left")
browser.mouse_wheel(100)
```

### Settings

```python
browser.set_viewport(1920, 1080)
browser.set_device("iPhone 14")
browser.set_geolocation(37.7749, -122.4194)
browser.set_offline(True)
browser.set_headers({"Authorization": "Bearer token"})
```

### Cookies & Storage

```python
cookies = browser.get_cookies()
browser.set_cookie("name", "value")
browser.clear_cookies()

data = browser.get_local_storage()
browser.set_local_storage("key", "value")
browser.clear_local_storage()
```

### Network

```python
browser.network_route("**/api/**", abort=True)
browser.network_route("**/api/mock", body={"data": "mocked"})
requests = browser.network_requests(filter_text="api")
```

### Tabs

```python
tabs = browser.list_tabs()
browser.new_tab("https://example.com")
browser.switch_tab(1)
browser.close_tab(1)
```

## Configuration Options

```python
browser = AgentBrowser(
    session="my-session",
    executable_path="/path/to/chromium",
    headers={"X-Custom": "value"},
    headed=True,
    debug=True,
    cdp_port=9222
)
```

## Session Management

Check and manage browser sessions:

```python
sessions = AgentBrowser.list_sessions()
print(f"Active sessions: {sessions}")

browser = AgentBrowser()
browser.open("https://example.com")

print(f"Current session: {browser.get_current_session()}")
print(f"Is active: {browser.is_session_active()}")

browser.close()
```

### Close All Sessions

Close all active browser sessions at once:

```python
browser1 = AgentBrowser(session="session-1")
browser1.open("https://example.com")

browser2 = AgentBrowser(session="session-2")
browser2.open("https://github.com")

print(f"Active: {AgentBrowser.list_sessions()}")

closed_count = AgentBrowser.close_all_sessions()
print(f"Closed {closed_count} sessions")
print(f"Remaining: {AgentBrowser.list_sessions()}")
```

The function automatically retries if some sessions don't close on the first attempt (default: 2 retries with 0.5s delay).

### Complete Shutdown

For complete cleanup with verification:

```python
browser1 = AgentBrowser(session="work")
browser1.open("https://github.com")

browser2 = AgentBrowser(session="personal")
browser2.open("https://example.com")

result = AgentBrowser.shutdown(verbose=True)

print(result)
# {
#   "sessions_closed": 2,
#   "cleanup_performed": True,
#   "remaining_sessions": []
# }
```

### Auto-Shutdown on Exit

Register automatic cleanup when your program exits:

```python
from agent_browser import AgentBrowser

AgentBrowser.register_shutdown_hook(verbose=True)

browser = AgentBrowser()
browser.open("https://example.com")

# Sessions will automatically close when program exits
```

**Note**: Sessions persist in the background briefly after `close()` is called (usually 1-2 seconds) before being fully terminated.

## Refs Workflow (Recommended for AI)

The refs workflow is optimal for AI agents:

1. Get snapshot with refs
2. AI analyzes the tree and identifies target refs
3. Use refs to interact with elements

```python
browser.open("https://example.com")

snapshot = browser.snapshot(interactive_only=True)

refs = snapshot.get('refs', {})
for ref_id, element in refs.items():
    print(f"{ref_id}: {element['role']} - {element.get('name', '')}")

browser.click("@e2")
browser.fill("@e3", "input text")
```

## Error Handling

```python
from agent_browser import AgentBrowser, AgentBrowserError

try:
    browser = AgentBrowser()
    browser.open("https://example.com")
    browser.click("@invalid-ref")
except AgentBrowserError as e:
    print(f"Browser error: {e}")
finally:
    browser.close()
```

## Examples

- [example_usage.py](./examples/example_usage.py) - Sync API examples
- [example_batch.py](./examples/example_batch.py) - Batch execution examples
- [example_async_usage.py](./examples/example_async_usage.py) - Async API examples

## Requirements

- Python >= 3.11
- agent-browser CLI (installed globally via npm)
- Chromium browser (installed via `agent-browser install`)

## License

MIT

## Related

- [agent-browser](https://github.com/vercel-labs/agent-browser) - Original CLI tool
- [Playwright](https://playwright.dev/) - Browser automation library (used by agent-browser)
