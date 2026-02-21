import statistics
import time
from typing import Optional

import typer

from agent_browser import AgentBrowser
from fnguide_utils import (
    get_sise_hyeonhwang_df_agent_browser,
    get_sise_hyeonhwang_df_agent_browser_with_instance,
    get_sise_hyeonhwang_df_playwright,
)


app = typer.Typer(add_completion=False)


DEFAULT_URL = "https://comp.fnguide.com/svo2/asp/etf_snapshot.asp?pGB=1&gicode=A237350&cID=&MenuYn=N&ReportGB=&NewMenuID=401&stkGb=770"


def _measure(fn, iterations: int, warmup: int) -> list[float]:
    for _ in range(warmup):
        fn()

    times: list[float] = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t0)

    return times


def _summary(times: list[float]) -> dict:
    return {
        "n": len(times),
        "mean_s": statistics.mean(times) if times else float("nan"),
        "stdev_s": statistics.pstdev(times) if len(times) >= 2 else 0.0,
        "min_s": min(times) if times else float("nan"),
        "max_s": max(times) if times else float("nan"),
    }


@app.command()
def run(
    url: str = typer.Option(DEFAULT_URL, help="Target FnGuide ETF snapshot URL"),
    iterations: int = typer.Option(10, min=1),
    warmup: int = typer.Option(2, min=0),
    headed: bool = typer.Option(False, help="Run headed mode for agent-browser"),
    playwright_headless: bool = typer.Option(True, help="Run Playwright headless"),
    reuse_agent_browser: bool = typer.Option(
        True, help="Reuse a single agent-browser instance/session across iterations"
    ),
    agent_browser_session: str = typer.Option(
        "bench-fnguide", help="Session name for agent-browser"
    ),
    print_df: str = typer.Option(
        "",
        help="Print extracted DataFrame for validation. Values: playwright|agent-browser|both",
    ),
    print_rows: int = typer.Option(12, min=1, help="Number of rows to print"),
):
    """Benchmark Playwright vs agent-browser for extracting '시세현황' as DataFrame."""

    print_choice = (print_df or "").strip().lower()
    if print_choice and print_choice not in {"playwright", "agent-browser", "both"}:
        raise typer.BadParameter(
            "print_df must be one of: playwright, agent-browser, both"
        )

    # Playwright
    def _pw_extract():
        return get_sise_hyeonhwang_df_playwright(url, headless=playwright_headless)

    if print_choice in {"playwright", "both"}:
        df = _pw_extract()
        typer.echo("\n=== DataFrame (Playwright) ===")
        typer.echo(df.head(print_rows).to_string(index=False))

    pw_times = _measure(
        _pw_extract,
        iterations=iterations,
        warmup=warmup,
    )

    # agent-browser
    if reuse_agent_browser:
        b = AgentBrowser(
            session=agent_browser_session,
            headed=headed,
            auto_close=False,
            close_on_exit=False,
        )
        try:
            def _ab_extract():
                return get_sise_hyeonhwang_df_agent_browser_with_instance(b, url)

            if print_choice in {"agent-browser", "both"}:
                df = _ab_extract()
                typer.echo("\n=== DataFrame (agent-browser) ===")
                typer.echo(df.head(print_rows).to_string(index=False))

            ab_times = _measure(
                _ab_extract,
                iterations=iterations,
                warmup=warmup,
            )
        finally:
            try:
                b.close()
            except Exception:
                pass
    else:
        def _ab_extract_fresh():
            return get_sise_hyeonhwang_df_agent_browser(
                url, session=None, headed=headed, close=True
            )

        if print_choice in {"agent-browser", "both"}:
            df = _ab_extract_fresh()
            typer.echo("\n=== DataFrame (agent-browser) ===")
            typer.echo(df.head(print_rows).to_string(index=False))

        ab_times = _measure(
            _ab_extract_fresh,
            iterations=iterations,
            warmup=warmup,
        )

    pw = _summary(pw_times)
    ab = _summary(ab_times)

    typer.echo("\n=== Benchmark Results (seconds) ===")
    typer.echo(f"Playwright:   n={pw['n']} mean={pw['mean_s']:.4f} stdev={pw['stdev_s']:.4f} min={pw['min_s']:.4f} max={pw['max_s']:.4f}")
    typer.echo(f"agent-browser n={ab['n']} mean={ab['mean_s']:.4f} stdev={ab['stdev_s']:.4f} min={ab['min_s']:.4f} max={ab['max_s']:.4f}")


if __name__ == "__main__":
    app()
