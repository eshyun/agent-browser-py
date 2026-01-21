from agent_browser import AgentBrowser


def main():
    print("Agent Browser Python Wrapper Demo")
    print("=" * 50)

    with AgentBrowser() as browser:
        print("\n1. Opening example.com...")
        browser.open("https://example.com")

        print("2. Getting page info...")
        title = browser.get_title()
        url = browser.get_url()
        print(f"   Title: {title}")
        print(f"   URL: {url}")

        print("\n3. Getting snapshot...")
        snapshot = browser.snapshot(interactive_only=True, compact=True)

        print(f"   Available refs: {list(snapshot.get('refs', {}).keys())[:5]}...")

        print("\n4. Taking screenshot...")
        browser.screenshot("example.png")
        print("   Screenshot saved to example.png")

    print("\n✓ Demo completed successfully!")


if __name__ == "__main__":
    main()
