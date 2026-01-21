"""
Examples of using batch execution to improve performance
"""

from agent_browser import AgentBrowser
import time


def basic_batch_example():
    """Basic batch execution example"""
    print("\n=== Basic Batch Example ===")

    browser = AgentBrowser()

    with browser.batch() as b:
        b.open("https://example.com")
        b.get_title()
        b.get_url()
        b.get_text("h1")

    print(f"Results: {b.results}")
    browser.close()


def fluent_api_example():
    """Fluent API chaining example"""
    print("\n=== Fluent API Example ===")

    browser = AgentBrowser()

    with browser.batch() as b:
        (
            b.open("https://example.com")
            .wait("h1")
            .get_title()
            .get_url()
            .screenshot("example.png")
        )

    print(f"Executed {len(b.commands)} commands")
    print(f"Results: {len([r for r in b.results if r])} successful")
    browser.close()


def performance_comparison():
    """Compare batch vs sequential performance"""
    print("\n=== Performance Comparison ===")

    browser = AgentBrowser()
    browser.open("https://example.com")

    print("Batch execution (5 commands)...")
    start = time.time()
    with browser.batch() as b:
        for _ in range(5):
            b.get_title()
    batch_time = time.time() - start

    print("Sequential execution (5 commands)...")
    start = time.time()
    for _ in range(5):
        browser.get_title()
    seq_time = time.time() - start

    print(f"\nBatch: {batch_time:.3f}s ({(batch_time / 5) * 1000:.1f}ms per cmd)")
    print(f"Sequential: {seq_time:.3f}s ({(seq_time / 5) * 1000:.1f}ms per cmd)")

    if batch_time < seq_time:
        speedup = seq_time / batch_time
        saved = ((seq_time - batch_time) / seq_time) * 100
        print(f"✅ Batch is {speedup:.2f}x faster ({saved:.1f}% time saved)")

    browser.close()


def scraping_workflow():
    """Realistic scraping workflow with batch"""
    print("\n=== Scraping Workflow ===")

    browser = AgentBrowser()

    with browser.batch() as b:
        b.open("https://example.com")
        b.wait("h1")
        b.get_title()
        b.get_url()
        b.get_text("h1")
        b.get_text("p")
        b.screenshot("scraped.png")

    print(f"Scraped data:")
    for i, result in enumerate(b.results):
        if result and isinstance(result, (str, dict)):
            print(f"  [{i}] {result}")

    browser.close()


def multi_action_workflow():
    """Multiple actions in sequence"""
    print("\n=== Multi-Action Workflow ===")

    browser = AgentBrowser()

    with browser.batch() as b:
        b.open("https://example.com")
        b.wait("body")
        b.click("a")
        b.wait(1000)
        b.get_title()
        b.screenshot("after-click.png")

    print(f"Workflow completed: {len(b.commands)} steps")
    browser.close()


def error_handling_example():
    """Batch execution with error handling"""
    print("\n=== Error Handling Example ===")

    browser = AgentBrowser()

    try:
        with browser.batch() as b:
            b.open("https://example.com")
            b.get_title()
            b.click("@invalid-ref")
            b.get_url()

        print(f"Results: {b.results}")
    except Exception as e:
        print(f"Error during batch: {e}")
    finally:
        browser.close()


def when_to_use_batch():
    """Guidelines on when to use batch execution"""
    print("\n=== When to Use Batch ===")
    print("""
    ✅ Use Batch When:
    - Executing 5+ sequential commands
    - All commands target the same page/session
    - Order doesn't depend on previous results
    - Performance is important
    
    ❌ Don't Use Batch When:
    - Need to check results between commands
    - Conditional logic based on previous results
    - Commands are on different pages/sessions
    - Only 1-2 commands total
    
    📊 Performance Sweet Spot:
    - Best for 5-20 commands
    - ~20-30% faster than sequential
    - Diminishing returns beyond 20 commands
    """)


if __name__ == "__main__":
    print("=" * 60)
    print("Agent Browser Batch Execution Examples")
    print("=" * 60)

    basic_batch_example()
    fluent_api_example()
    performance_comparison()
    scraping_workflow()
    multi_action_workflow()

    when_to_use_batch()

    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("=" * 60)
