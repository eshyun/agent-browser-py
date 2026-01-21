from agent_browser import AgentBrowser


def basic_example():
    browser = AgentBrowser()

    browser.open("https://example.com")

    snapshot = browser.snapshot(interactive_only=True)
    print("Snapshot:", snapshot)

    title = browser.get_title()
    print(f"Page title: {title}")

    url = browser.get_url()
    print(f"Current URL: {url}")

    browser.screenshot("example.png", full_page=True)

    browser.close()


def context_manager_example():
    with AgentBrowser(headed=True) as browser:
        browser.open("https://example.com")

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

    browser.open("https://example.com")

    snapshot = browser.snapshot(interactive_only=True)
    print("Available refs:", snapshot.get("refs", {}).keys())

    browser.click("@e1")
    browser.fill("@e2", "test@example.com")

    browser.close()


def get_methods_example():
    with AgentBrowser() as browser:
        browser.open("https://example.com")

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
        browser.open("https://github.com")

        placeholder = browser.get_attr("input[name='q']", "placeholder")
        print(f"Search input placeholder: {placeholder}")

        button_count = browser.get_count("button")
        print(f"Total buttons on page: {button_count}")

        logo_box = browser.get_box(".octicon-mark-github")
        if logo_box:
            print(f"GitHub logo position: x={logo_box.get('x')}, y={logo_box.get('y')}")

        all_links = browser.get_count("a")
        visible_links = browser.get_count("a:visible")
        print(f"Links: {all_links} total, {visible_links} visible")


def form_interaction_example():
    with AgentBrowser() as browser:
        browser.open("https://example.com")

        browser.fill("input#email", "test@example.com")

        email_value = browser.get_value("input#email")
        print(f"Filled email: {email_value}")

        input_type = browser.get_attr("input#email", "type")
        print(f"Input type: {input_type}")

        input_name = browser.get_attr("input#email", "name")
        print(f"Input name: {input_name}")

        input_box = browser.get_box("input#email")
        print(
            f"Input dimensions: {input_box.get('width')}px × {input_box.get('height')}px"
        )


def session_management_example():
    print("\n=== Session Management ===")

    print(f"Initial sessions: {AgentBrowser.list_sessions()}")

    browser = AgentBrowser()
    browser.open("https://example.com")

    print(f"After open: {AgentBrowser.list_sessions()}")
    print(f"Current session: {browser.get_current_session()}")
    print(f"Session active: {browser.is_session_active()}")

    browser.close()
    print(f"After close: {AgentBrowser.list_sessions()}")


def close_all_sessions_example():
    print("\n=== Close All Sessions ===")

    browser1 = AgentBrowser(session="test-1")
    browser1.open("https://example.com")

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
    browser2.open("https://example.com")

    print(f"Active: {AgentBrowser.list_sessions()}")

    result = AgentBrowser.shutdown(verbose=True)
    print(f"Result: {result}")


def auto_shutdown_example():
    print("\n=== Auto-Shutdown on Exit ===")

    AgentBrowser.register_shutdown_hook(verbose=True)

    browser = AgentBrowser()
    browser.open("https://example.com")

    print(f"Active: {AgentBrowser.list_sessions()}")
    print("Program will auto-cleanup on exit...")


if __name__ == "__main__":
    print("Running basic example...")
    basic_example()

    print("\nRunning context manager example...")
    context_manager_example()

    print("\nRunning get methods example...")
    get_methods_example()

    print("\nRunning advanced get example...")
    advanced_get_example()

    print("\nRunning form interaction example...")
    form_interaction_example()

    print("\nRunning session management example...")
    session_management_example()

    print("\nRunning close all sessions example...")
    close_all_sessions_example()

    print("\nRunning shutdown example...")
    shutdown_example()

    print("\nRunning auto-shutdown example...")
    auto_shutdown_example()
