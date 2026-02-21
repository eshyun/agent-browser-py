import io
from typing import Optional

import pandas as pd

from agent_browser import AgentBrowser


FN_GUIDE_SISE_HYEONHWANG_CONTAINER_SELECTOR = "#etf1Price"


def parse_sise_hyeonhwang_df(html: str) -> pd.DataFrame:
    dfs = pd.read_html(io.StringIO(html))
    if not dfs:
        raise ValueError("No tables found in provided HTML")

    df = dfs[0]

    if df.shape[1] >= 2:
        df = df.iloc[:, :2]
        df.columns = ["item", "value"]

    if "item" in df.columns:
        df["item"] = df["item"].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
    if "value" in df.columns:
        df["value"] = (
            df["value"]
            .astype(str)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

    return df


def get_sise_hyeonhwang_df_agent_browser(
    url: str,
    *,
    session: Optional[str] = None,
    headed: bool = False,
    debug: bool = False,
    close: bool = True,
) -> pd.DataFrame:
    browser = AgentBrowser(session=session, headed=headed, debug=debug, auto_close=False)

    try:
        browser.open(url)
        html = browser.get_html(FN_GUIDE_SISE_HYEONHWANG_CONTAINER_SELECTOR)
        return parse_sise_hyeonhwang_df(html)
    finally:
        if close:
            try:
                browser.close()
            except Exception:
                pass


def get_sise_hyeonhwang_df_agent_browser_with_instance(
    browser: AgentBrowser,
    url: str,
) -> pd.DataFrame:
    browser.open(url)
    html = browser.get_html(FN_GUIDE_SISE_HYEONHWANG_CONTAINER_SELECTOR)
    return parse_sise_hyeonhwang_df(html)


def get_sise_hyeonhwang_df_playwright(
    url: str,
    *,
    headless: bool = True,
    timeout_ms: int = 60_000,
) -> pd.DataFrame:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "Playwright is required for get_sise_hyeonhwang_df_playwright(). "
            "Install it with: uv add --group dev playwright"
        ) from e

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        try:
            page.goto(url, wait_until="networkidle", timeout=timeout_ms)
            locator = page.locator(FN_GUIDE_SISE_HYEONHWANG_CONTAINER_SELECTOR)
            locator.wait_for(state="visible", timeout=timeout_ms)
            html = locator.inner_html()
            return parse_sise_hyeonhwang_df(html)
        finally:
            browser.close()
