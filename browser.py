import asyncio
from typing import Optional, List
from playwright.async_api import async_playwright, Browser, Page, Locator
from credentials import PORT, CHROME_PATH


class BrowserWrapper:
    """Wrapper for Playwright browser automation"""
    
    def __init__(self, chrome_path: Optional[str] = None, port: Optional[int] = None):
        """Initialize browser wrapper
        
        Args:
            chrome_path (Optional[str]): Path to Chrome executable (not used in Playwright)
            port (Optional[int]): Port for remote debugging (not used in Playwright)
        """
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.chrome_path = chrome_path or CHROME_PATH
        self.port = port or PORT
        
    async def connect(self) -> None:
        """Connect to browser"""
        self.playwright = await async_playwright().start()
        
        # Connect to existing Chrome instance if port is specified, otherwise launch new
        if self.port:
            self.browser = await self.playwright.chromium.connect_over_cdp(
                f"http://localhost:{self.port}"
            )
        else:
            self.browser = await self.playwright.chromium.launch(
                headless=False,
                channel="chrome" if self.chrome_path else None
            )
        
        # Get or create page
        contexts = self.browser.contexts
        if contexts:
            self.page = contexts[0].pages[0] if contexts[0].pages else await contexts[0].new_page()
        else:
            context = await self.browser.new_context()
            self.page = await context.new_page()
    
    async def set_page(self, url: str) -> None:
        """Navigate to URL
        
        Args:
            url (str): URL to navigate to
        """
        if not self.page:
            await self.connect()
        await self.page.goto(url, wait_until="networkidle")
    
    async def count_elems(self, selector: str) -> int:
        """Count elements matching selector
        
        Args:
            selector (str): CSS selector
            
        Returns:
            int: Number of elements found
        """
        if not self.page:
            return 0
        return await self.page.locator(selector).count()
    
    async def get_text(self, selector: str) -> str:
        """Get text from element
        
        Args:
            selector (str): CSS selector
            
        Returns:
            str: Text content of element
        """
        if not self.page:
            return ""
        try:
            elem = self.page.locator(selector).first
            if await elem.count() > 0:
                return await elem.inner_text()
        except Exception:
            pass
        return ""
    
    async def send_data(self, selector: str, text: str) -> None:
        """Send text to input element
        
        Args:
            selector (str): CSS selector
            text (str): Text to send
        """
        if not self.page:
            return
        elem = self.page.locator(selector).first
        await elem.fill(text)
    
    async def click(self, selector: str) -> None:
        """Click element
        
        Args:
            selector (str): CSS selector
        """
        if not self.page:
            return
        elem = self.page.locator(selector).first
        await elem.click()
    
    async def close(self) -> None:
        """Close browser connection"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
