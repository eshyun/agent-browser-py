from agent_browser import AgentBrowser
import time


def basic_example():
    browser = AgentBrowser()

    browser.open("https://example.org")

    snapshot = browser.snapshot(interactive_only=True)
    print("Snapshot:", snapshot)

    title = browser.get_title()
    print(f"Page title: {title}")

    url = browser.get_url()
    print(f"Current URL: {url}")

    browser.screenshot("example.png", full_page=True)

    browser.close()


def context_manager_example():
    with AgentBrowser() as browser:
        browser.open("https://example.org")

        snapshot = browser.snapshot(interactive_only=True, compact=True)

        text = browser.get_text("h1")
        print(f"Heading text: {text}")


def session_example():
    browser1 = AgentBrowser(session="session-1")
    browser1.open("https://site-a.com")

    browser2 = AgentBrowser(session="session-2")
    browser2.open("https://site-b.com")

    browser1.close()
    browser2.close()


def refs_workflow():
    browser = AgentBrowser()

    browser.open("https://example.org")

    snapshot = browser.snapshot(interactive_only=True)
    print("Available refs:", snapshot.get("refs", {}).keys())

    browser.click("@e1")
    browser.fill("@e2", "test@example.com")

    browser.close()


def get_methods_example():
    with AgentBrowser() as browser:
        browser.open("https://example.org")

        href = browser.get_attr("a", "href")
        print(f"Link href: {href}")

        link_count = browser.get_count("a")
        print(f"Number of links: {link_count}")

        box = browser.get_box("h1")
        print(f"Heading bounding box: {box}")
        print(f"  Position: ({box.get('x')}, {box.get('y')})")
        print(f"  Size: {box.get('width')}x{box.get('height')}")


def advanced_get_example():
    with AgentBrowser() as browser:
        browser.open("https://example.org")

        # Get various attributes and counts
        link_href = browser.get_attr("a", "href")
        print(f"First link href: {link_href}")

        all_paragraphs = browser.get_count("p")
        print(f"Total paragraphs: {all_paragraphs}")

        page_html = browser.get_html("body")
        print(f"Body HTML length: {len(page_html)} characters")

        # Check element states
        link_visible = browser.is_visible("a")
        print(f"First link is visible: {link_visible}")

        link_enabled = browser.is_enabled("a")
        print(f"First link is enabled: {link_enabled}")


def form_interaction_example():
    with AgentBrowser() as browser:
        browser.open("https://example.org")

        print("Note: example.org has no form elements")
        print("Demonstrating element state checks instead:")

        link_visible = browser.is_visible("a")
        print(f"Link is visible: {link_visible}")

        link_enabled = browser.is_enabled("a")
        print(f"Link is enabled: {link_enabled}")

        link_count = browser.get_count("a")
        print(f"Number of links: {link_count}")


def session_management_example():
    print("\n=== Session Management ===")

    print(f"Initial sessions: {AgentBrowser.list_sessions()}")

    browser = AgentBrowser()
    browser.open("https://example.org")

    print(f"After open: {AgentBrowser.list_sessions()}")
    print(f"Current session: {browser.get_current_session()}")
    print(f"Session active: {browser.is_session_active()}")

    browser.close()
    print(f"After close: {AgentBrowser.list_sessions()}")


def close_all_sessions_example():
    print("\n=== Close All Sessions ===")

    browser1 = AgentBrowser(session="test-1")
    browser1.open("https://example.org")

    browser2 = AgentBrowser(session="test-2")
    browser2.open("https://github.com")

    print(f"Active sessions: {AgentBrowser.list_sessions()}")

    closed = AgentBrowser.close_all_sessions()
    print(f"Closed {closed} sessions")
    print(f"Remaining: {AgentBrowser.list_sessions()}")


def shutdown_example():
    print("\n=== Shutdown (Complete Cleanup) ===")

    browser1 = AgentBrowser(session="work")
    browser1.open("https://github.com")

    browser2 = AgentBrowser(session="personal")
    browser2.open("https://example.org")

    print(f"Active: {AgentBrowser.list_sessions()}")

    result = AgentBrowser.shutdown(verbose=True)
    print(f"Result: {result}")


def auto_shutdown_example():
    print("\n=== Auto-Shutdown on Exit ===")

    AgentBrowser.register_shutdown_hook(verbose=True)

    browser = AgentBrowser()
    browser.open("https://example.org")

    print(f"Active: {AgentBrowser.list_sessions()}")
    print("Program will auto-cleanup on exit...")


if __name__ == "__main__":
    print("Running basic example...")
    basic_example()
    time.sleep(1)

    print("\nRunning context manager example...")
    context_manager_example()
    time.sleep(1)

    print("\nRunning get methods example...")
    get_methods_example()
    time.sleep(1)

    print("\nRunning advanced get example...")
    advanced_get_example()
    time.sleep(1)

    print("\nRunning form interaction example...")
    form_interaction_example()
    time.sleep(1)

    print("\nRunning session management example...")
    session_management_example()
    time.sleep(1)

    print("\nRunning close all sessions example...")
    close_all_sessions_example()
    time.sleep(1)

    print("\nRunning shutdown example...")
    shutdown_example()
    time.sleep(1)

    print("\nRunning auto-shutdown example...")
    auto_shutdown_example()
