import asyncio
from async_agent_browser import AsyncAgentBrowser


async def basic_example():
    print("=== Basic Async Example ===")
    browser = AsyncAgentBrowser()

    await browser.open("https://example.com")

    title = await browser.get_title()
    print(f"Page title: {title}")

    url = await browser.get_url()
    print(f"Current URL: {url}")

    await browser.close()


async def context_manager_example():
    print("\n=== Context Manager Example ===")
    async with AsyncAgentBrowser() as browser:
        await browser.open("https://example.com")

        text = await browser.get_text("h1")
        print(f"H1 text: {text}")

        count = await browser.get_count("p")
        print(f"Paragraph count: {count}")


async def batch_execution_example():
    print("\n=== Batch Execution Example ===")
    browser = AsyncAgentBrowser()

    async with browser.batch() as b:
        b.open("https://example.com")
        b.wait("h1")
        b.get_title()
        b.get_url()
        b.get_text("h1")

    print(f"Batch results: {b.results}")

    await browser.close()


async def parallel_browsers_example():
    print("\n=== Parallel Browsers Example ===")

    browser1 = AsyncAgentBrowser(session="session-1")
    browser2 = AsyncAgentBrowser(session="session-2")

    results = await asyncio.gather(
        browser1.open("https://example.com"),
        browser2.open("https://github.com"),
    )

    titles = await asyncio.gather(
        browser1.get_title(),
        browser2.get_title(),
    )

    print(f"Browser 1 title: {titles[0]}")
    print(f"Browser 2 title: {titles[1]}")

    await asyncio.gather(
        browser1.close(),
        browser2.close(),
    )


async def form_interaction_example():
    print("\n=== Form Interaction Example ===")
    async with AsyncAgentBrowser() as browser:
        await browser.open("https://example.com")

        await browser.fill("input[name='email']", "test@example.com")
        await browser.fill("input[name='password']", "password123")
        await browser.click("button[type='submit']")

        await browser.wait(url="**/dashboard")
        print("Form submitted and redirected!")


async def snapshot_and_refs_example():
    print("\n=== Snapshot and Refs Example ===")
    async with AsyncAgentBrowser() as browser:
        await browser.open("https://example.com")

        snapshot = await browser.snapshot(interactive_only=True)

        print("Interactive elements:")
        refs = snapshot.get("refs", {})
        for ref_id, element in list(refs.items())[:5]:
            print(f"  {ref_id}: {element.get('role')} - {element.get('name', 'N/A')}")

        if refs:
            first_ref = list(refs.keys())[0]
            print(f"\nClicking on {first_ref}...")
            await browser.click(f"@{first_ref}")


async def session_management_example():
    print("\n=== Session Management Example ===")

    sessions_before = await AsyncAgentBrowser.list_sessions()
    print(f"Sessions before: {sessions_before}")

    browser1 = AsyncAgentBrowser(session="test-1")
    browser2 = AsyncAgentBrowser(session="test-2")

    await browser1.open("https://example.com")
    await browser2.open("https://example.com")

    sessions_active = await AsyncAgentBrowser.list_sessions()
    print(f"Active sessions: {sessions_active}")

    await browser1.close()
    await browser2.close()

    sessions_after = await AsyncAgentBrowser.list_sessions()
    print(f"Sessions after: {sessions_after}")


async def shutdown_example():
    print("\n=== Shutdown Example ===")

    browser1 = AsyncAgentBrowser(session="work")
    browser2 = AsyncAgentBrowser(session="personal")

    await browser1.open("https://example.com")
    await browser2.open("https://github.com")

    print("Shutting down all sessions...")
    result = await AsyncAgentBrowser.shutdown(verbose=True)

    print(f"Shutdown result: {result}")


async def main():
    try:
        await basic_example()
        await context_manager_example()
        await batch_execution_example()
        await parallel_browsers_example()

        print("\n=== All examples completed! ===")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await AsyncAgentBrowser.shutdown(verbose=False)


if __name__ == "__main__":
    asyncio.run(main())
