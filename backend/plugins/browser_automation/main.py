"""
Browser Automation Plugin - FULLY FUNCTIONAL
Web browser automation using Playwright
"""
import os
import sys
import asyncio
from typing import Dict, Any, Optional, List

# Add backend path for imports
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Try to import Playwright
_playwright_available = False
_playwright = None

try:
    from playwright.async_api import async_playwright
    _playwright_available = True
except ImportError:
    pass


class Plugin:
    """
    Browser automation plugin using Playwright
    
    Commands:
    - open: Open a URL in headless browser
    - screenshot: Capture a webpage screenshot
    - get_text: Extract all text from a page
    - get_links: Get all links from a page
    - click: Click an element on the page
    - type: Type text into an input field
    - scroll: Scroll the page
    - search: Search Google and return results
    - fill_form: Fill out a form and submit
    """
    
    def __init__(self):
        self.name = "Browser Automation"
        self.version = "1.0.0"
        self.browser = None
        self.page = None
        self._loop = None
        
        # Screenshot directory
        self.screenshot_dir = os.path.join(backend_path, "temp", "screenshots")
        os.makedirs(self.screenshot_dir, exist_ok=True)
    
    def _get_event_loop(self):
        """Get or create event loop"""
        try:
            self._loop = asyncio.get_event_loop()
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        return self._loop
    
    def run(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command"""
        if not _playwright_available:
            return {
                "error": "Playwright not installed. Run: pip install playwright && playwright install chromium"
            }
        
        commands = {
            "open": self.open_page,
            "screenshot": self.take_screenshot,
            "get_text": self.get_text,
            "get_links": self.get_links,
            "click": self.click_element,
            "type": self.type_text,
            "scroll": self.scroll_page,
            "search": self.google_search,
            "fill_form": self.fill_form,
            "close": self.close_browser,
        }
        
        handler = commands.get(command)
        if handler:
            try:
                loop = self._get_event_loop()
                return loop.run_until_complete(handler(params))
            except Exception as e:
                return {"error": str(e)}
        
        return {"error": f"Unknown command: {command}"}
    
    async def _ensure_browser(self, headless: bool = True):
        """Ensure browser is running"""
        if self.browser is None:
            pw = await async_playwright().start()
            self.browser = await pw.chromium.launch(headless=headless)
            self.page = await self.browser.new_page()
        return self.page
    
    async def open_page(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Open a URL in the browser
        
        Params:
        - url: URL to open
        - wait: Wait for load (default: True)
        - headless: Run headless (default: True)
        """
        url = params.get("url")
        if not url:
            return {"error": "No URL provided"}
        
        headless = params.get("headless", True)
        
        try:
            page = await self._ensure_browser(headless)
            await page.goto(url, wait_until="domcontentloaded")
            
            return {
                "status": "success",
                "url": page.url,
                "title": await page.title()
            }
        except Exception as e:
            return {"error": f"Failed to open URL: {e}"}
    
    async def take_screenshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Take a screenshot of the current page
        
        Params:
        - url: URL to screenshot (optional if already open)
        - filename: Output filename (optional)
        - full_page: Capture full page (default: False)
        """
        url = params.get("url")
        full_page = params.get("full_page", False)
        filename = params.get("filename", f"screenshot_{os.urandom(4).hex()}.png")
        
        try:
            page = await self._ensure_browser()
            
            if url:
                await page.goto(url, wait_until="domcontentloaded")
            
            screenshot_path = os.path.join(self.screenshot_dir, filename)
            await page.screenshot(path=screenshot_path, full_page=full_page)
            
            return {
                "status": "success",
                "path": screenshot_path,
                "url": page.url,
                "filename": filename
            }
        except Exception as e:
            return {"error": f"Screenshot failed: {e}"}
    
    async def get_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract all text from the page
        
        Params:
        - url: URL to extract from (optional if already open)
        - selector: CSS selector to limit extraction (optional)
        """
        url = params.get("url")
        selector = params.get("selector", "body")
        
        try:
            page = await self._ensure_browser()
            
            if url:
                await page.goto(url, wait_until="domcontentloaded")
            
            element = await page.query_selector(selector)
            if element:
                text = await element.text_content()
            else:
                text = ""
            
            return {
                "status": "success",
                "text": text.strip() if text else "",
                "url": page.url,
                "length": len(text) if text else 0
            }
        except Exception as e:
            return {"error": f"Text extraction failed: {e}"}
    
    async def get_links(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get all links from the page
        
        Params:
        - url: URL to extract links from (optional)
        - limit: Maximum number of links (default: 50)
        """
        url = params.get("url")
        limit = params.get("limit", 50)
        
        try:
            page = await self._ensure_browser()
            
            if url:
                await page.goto(url, wait_until="domcontentloaded")
            
            links = await page.eval_on_selector_all(
                "a[href]",
                """elements => elements.slice(0, arguments[0]).map(el => ({
                    href: el.href,
                    text: el.textContent.trim().substring(0, 100)
                }))""",
                limit
            )
            
            return {
                "status": "success",
                "links": links,
                "count": len(links),
                "url": page.url
            }
        except Exception as e:
            return {"error": f"Link extraction failed: {e}"}
    
    async def click_element(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Click an element on the page
        
        Params:
        - selector: CSS selector for element
        - wait: Wait for navigation after click (default: True)
        """
        selector = params.get("selector")
        if not selector:
            return {"error": "No selector provided"}
        
        wait_for_nav = params.get("wait", True)
        
        try:
            page = await self._ensure_browser()
            
            if wait_for_nav:
                async with page.expect_navigation(wait_until="domcontentloaded", timeout=10000):
                    await page.click(selector)
            else:
                await page.click(selector)
            
            return {
                "status": "success",
                "selector": selector,
                "url": page.url
            }
        except Exception as e:
            return {"error": f"Click failed: {e}"}
    
    async def type_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Type text into an input field
        
        Params:
        - selector: CSS selector for input
        - text: Text to type
        - clear: Clear field first (default: True)
        """
        selector = params.get("selector")
        text = params.get("text", "")
        clear = params.get("clear", True)
        
        if not selector:
            return {"error": "No selector provided"}
        
        try:
            page = await self._ensure_browser()
            
            if clear:
                await page.fill(selector, text)
            else:
                await page.type(selector, text)
            
            return {
                "status": "success",
                "selector": selector,
                "text_length": len(text)
            }
        except Exception as e:
            return {"error": f"Typing failed: {e}"}
    
    async def scroll_page(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scroll the page
        
        Params:
        - direction: "down", "up", "bottom", "top" (default: "down")
        - amount: Pixels to scroll (for up/down)
        """
        direction = params.get("direction", "down")
        amount = params.get("amount", 500)
        
        try:
            page = await self._ensure_browser()
            
            if direction == "bottom":
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            elif direction == "top":
                await page.evaluate("window.scrollTo(0, 0)")
            elif direction == "up":
                await page.evaluate(f"window.scrollBy(0, -{amount})")
            else:  # down
                await page.evaluate(f"window.scrollBy(0, {amount})")
            
            return {
                "status": "success",
                "direction": direction,
                "amount": amount
            }
        except Exception as e:
            return {"error": f"Scroll failed: {e}"}
    
    async def google_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search Google and return results
        
        Params:
        - query: Search query
        - limit: Number of results (default: 10)
        """
        query = params.get("query", "")
        limit = params.get("limit", 10)
        
        if not query:
            return {"error": "No search query provided"}
        
        try:
            page = await self._ensure_browser()
            
            # Go to Google
            await page.goto(f"https://www.google.com/search?q={query}", wait_until="domcontentloaded")
            
            # Wait for results
            await page.wait_for_selector("div#search", timeout=5000)
            
            # Extract results
            results = await page.eval_on_selector_all(
                "div.g",
                f"""elements => elements.slice(0, {limit}).map(el => {{
                    const titleEl = el.querySelector('h3');
                    const linkEl = el.querySelector('a');
                    const snippetEl = el.querySelector('.VwiC3b');
                    return {{
                        title: titleEl ? titleEl.textContent : '',
                        url: linkEl ? linkEl.href : '',
                        snippet: snippetEl ? snippetEl.textContent : ''
                    }};
                }}).filter(r => r.title && r.url)"""
            )
            
            return {
                "status": "success",
                "query": query,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {"error": f"Search failed: {e}"}
    
    async def fill_form(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fill out a form
        
        Params:
        - fields: Dict of {selector: value}
        - submit: Selector for submit button (optional)
        """
        fields = params.get("fields", {})
        submit_selector = params.get("submit")
        
        if not fields:
            return {"error": "No form fields provided"}
        
        try:
            page = await self._ensure_browser()
            
            # Fill each field
            for selector, value in fields.items():
                await page.fill(selector, str(value))
            
            # Submit if specified
            if submit_selector:
                await page.click(submit_selector)
                await page.wait_for_load_state("domcontentloaded")
            
            return {
                "status": "success",
                "fields_filled": len(fields),
                "submitted": submit_selector is not None,
                "url": page.url
            }
        except Exception as e:
            return {"error": f"Form fill failed: {e}"}
    
    async def close_browser(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Close the browser"""
        try:
            if self.browser:
                await self.browser.close()
                self.browser = None
                self.page = None
            
            return {"status": "success", "message": "Browser closed"}
        except Exception as e:
            return {"error": f"Failed to close browser: {e}"}


# Export plugin instance
plugin = Plugin()
