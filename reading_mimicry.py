"""
The Infiltrator - Reading Mimicry & Navigation
Simulates realistic human reading and browsing behavior with honeypot avoidance

Features:
- Burst scrolling with reading pauses
- CSS visibility checking (honeypot detection)
- Z-index validation
- Contextual hovering over interesting content
- Non-linear navigation patterns
"""

import random
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from temporal_entropy import TemporalEntropy, ActivityType


@dataclass
class ViewportInfo:
    """Information about current viewport"""
    width: int
    height: int
    scroll_y: int
    scroll_x: int
    max_scroll_y: int
    max_scroll_x: int


class HoneypotDetector:
    """Detects and avoids honeypot elements"""
    
    # JavaScript snippets for element validation
    JS_VISIBILITY_CHECK = """
    (element) => {
        if (!element) return false;
        
        const style = window.getComputedStyle(element);
        const rect = element.getBoundingClientRect();
        
        // Check CSS properties that indicate invisibility
        const checks = {
            display: style.display !== 'none',
            visibility: style.visibility !== 'hidden',
            opacity: parseFloat(style.opacity) > 0,
            zIndex: parseInt(style.zIndex) || 0,
            width: rect.width > 0,
            height: rect.height > 0,
            inViewport: rect.top < window.innerHeight && rect.bottom > 0
        };
        
        return checks;
    }
    """
    
    JS_HONEYPOT_DETECTION = """
    (element) => {
        if (!element) return true; // Assume honeypot if element not found
        
        const style = window.getComputedStyle(element);
        const rect = element.getBoundingClientRect();
        
        // Honeypot indicators
        const honeypotIndicators = {
            // Hidden via CSS
            displayNone: style.display === 'none',
            visibilityHidden: style.visibility === 'hidden',
            opacityZero: parseFloat(style.opacity) === 0,
            
            // Positioned off-screen
            offScreenLeft: rect.left < -100,
            offScreenTop: rect.top < -100,
            offScreenRight: rect.right > window.innerWidth + 100,
            
            // Negative z-index (behind other content)
            negativeZIndex: parseInt(style.zIndex) < 0,
            
            // Zero dimensions
            zeroWidth: rect.width === 0,
            zeroHeight: rect.height === 0,
            
            // Tiny dimensions (likely hidden)
            tinyElement: rect.width < 2 && rect.height < 2,
            
            // Common honeypot class/id patterns
            suspiciousClass: element.className.match(/hidden|trap|honeypot|bot-trap/i) !== null,
            suspiciousId: element.id.match(/hidden|trap|honeypot|bot-trap/i) !== null,
            
            // Position fixed with negative values
            fixedNegative: style.position === 'fixed' && 
                          (parseInt(style.left) < -50 || parseInt(style.top) < -50)
        };
        
        // If any indicator is true, it's likely a honeypot
        const isHoneypot = Object.values(honeypotIndicators).some(v => v === true);
        
        return {
            isHoneypot: isHoneypot,
            indicators: honeypotIndicators,
            zIndex: parseInt(style.zIndex) || 0,
            visibility: style.visibility,
            opacity: parseFloat(style.opacity),
            display: style.display,
            rect: {
                x: rect.x,
                y: rect.y,
                width: rect.width,
                height: rect.height
            }
        };
    }
    """
    
    @staticmethod
    async def is_element_safe(page, selector: str) -> Tuple[bool, Dict]:
        """
        Check if element is safe to interact with (not a honeypot)
        
        Args:
            page: Playwright page object
            selector: CSS selector for element
        
        Returns:
            Tuple of (is_safe, details_dict)
        """
        try:
            element = await page.query_selector(selector)
            if not element:
                return False, {"error": "Element not found"}
            
            # Run honeypot detection
            result = await page.evaluate(HoneypotDetector.JS_HONEYPOT_DETECTION, element)
            
            is_safe = not result['isHoneypot']
            
            return is_safe, result
            
        except Exception as e:
            return False, {"error": str(e)}
    
    @staticmethod
    async def is_element_visible(page, selector: str) -> Tuple[bool, Dict]:
        """
        Check if element is truly visible to the user
        
        Args:
            page: Playwright page object
            selector: CSS selector for element
        
        Returns:
            Tuple of (is_visible, checks_dict)
        """
        try:
            element = await page.query_selector(selector)
            if not element:
                return False, {"error": "Element not found"}
            
            checks = await page.evaluate(HoneypotDetector.JS_VISIBILITY_CHECK, element)
            
            # Element is visible if all critical checks pass
            is_visible = all([
                checks['display'],
                checks['visibility'],
                checks['opacity'],
                checks['width'],
                checks['height'],
                checks['zIndex'] >= 0
            ])
            
            return is_visible, checks
            
        except Exception as e:
            return False, {"error": str(e)}


class ScrollBehavior:
    """Simulates human-like scrolling patterns"""
    
    def __init__(self, page):
        self.page = page
        self.current_position = 0
    
    async def get_viewport_info(self) -> ViewportInfo:
        """Get current viewport and scroll information"""
        info = await self.page.evaluate("""
            () => {
                return {
                    width: window.innerWidth,
                    height: window.innerHeight,
                    scrollY: window.scrollY,
                    scrollX: window.scrollX,
                    maxScrollY: document.documentElement.scrollHeight - window.innerHeight,
                    maxScrollX: document.documentElement.scrollWidth - window.innerWidth
                };
            }
        """)
        
        return ViewportInfo(**info)
    
    async def burst_scroll(
        self, 
        num_scrolls: int = None,
        reading_behavior: bool = True
    ):
        """
        Perform burst scrolling with reading pauses
        
        Args:
            num_scrolls: Number of scroll bursts (None = scroll entire page)
            reading_behavior: Whether to pause and "read" between scrolls
        """
        viewport = await self.get_viewport_info()
        
        if num_scrolls is None:
            # Calculate scrolls needed to reach bottom (with some randomness)
            viewport_height = viewport.height
            total_height = viewport.max_scroll_y
            num_scrolls = int((total_height / viewport_height) * random.uniform(0.7, 1.0))
            num_scrolls = max(3, num_scrolls)  # At least 3 scrolls
        
        print(f"[*] Burst scrolling: {num_scrolls} scroll actions")
        
        for i in range(num_scrolls):
            # Calculate scroll distance (variable, not constant)
            viewport = await self.get_viewport_info()
            
            # Random scroll amount (60-120% of viewport height)
            scroll_amount = int(viewport.height * random.uniform(0.6, 1.2))
            
            # Don't scroll past the end
            new_position = min(
                self.current_position + scroll_amount,
                viewport.max_scroll_y
            )
            
            # Perform scroll
            await self.page.evaluate(f"window.scrollTo(0, {new_position})")
            self.current_position = new_position
            
            print(f"    Scroll {i+1}/{num_scrolls}: {new_position}px")
            
            # Check if we've reached the bottom
            if new_position >= viewport.max_scroll_y:
                print("[+] Reached bottom of page")
                break
            
            # Reading pause (Gaussian timing)
            if reading_behavior:
                # Longer pauses at interesting content (random chance)
                if random.random() < 0.3:  # 30% chance of longer pause
                    pause = TemporalEntropy.generate_delay(ActivityType.READING_PARAGRAPH)
                    print(f"    Reading pause (long): {pause:.2f}s")
                else:
                    pause = TemporalEntropy.generate_delay(ActivityType.SCROLL_PAUSE)
                    print(f"    Reading pause: {pause:.2f}s")
                
                await self.page.wait_for_timeout(int(pause * 1000))
                
                # Sometimes hover over interesting elements
                if random.random() < 0.4:  # 40% chance
                    await self._hover_interesting_content()
    
    async def _hover_interesting_content(self):
        """Hover over interesting content (images, headings, links)"""
        try:
            # Find interesting elements in viewport
            interesting_selectors = [
                'h1', 'h2', 'h3',           # Headings
                'img[src]',                 # Images
                'a[href]',                  # Links
                'button',                   # Buttons
                'article',                  # Article content
                '.card', '.post'            # Common content containers
            ]
            
            for selector in interesting_selectors:
                elements = await self.page.query_selector_all(selector)
                
                if not elements:
                    continue
                
                # Pick a random visible element
                for element in random.sample(elements, min(3, len(elements))):
                    # Check if element is visible and safe
                    is_visible = await element.is_visible()
                    
                    if not is_visible:
                        continue
                    
                    # Check for honeypot
                    element_id = await element.get_attribute('id')
                    element_class = await element.get_attribute('class')
                    
                    # Skip suspicious elements
                    if element_id and any(x in element_id.lower() for x in ['hidden', 'trap', 'honeypot']):
                        continue
                    if element_class and any(x in element_class.lower() for x in ['hidden', 'trap', 'honeypot']):
                        continue
                    
                    # Hover over element
                    try:
                        await element.hover()
                        print(f"    Hovered over: {selector}")
                        
                        # Short hover duration
                        hover_time = TemporalEntropy.generate_delay(ActivityType.THINKING)
                        await self.page.wait_for_timeout(int(hover_time * 1000))
                        
                        return  # Only hover once per scroll pause
                    except:
                        continue
        
        except Exception as e:
            # Silently fail - hovering is optional behavior
            pass


class NavigationBehavior:
    """Handles realistic navigation and interaction patterns"""
    
    def __init__(self, page):
        self.page = page
        self.honeypot_detector = HoneypotDetector()
        self.scroll_behavior = ScrollBehavior(page)
    
    async def safe_click(self, selector: str, check_honeypot: bool = True) -> bool:
        """
        Safely click an element after validating it's not a honeypot
        
        Args:
            selector: CSS selector for element
            check_honeypot: Whether to perform honeypot checks
        
        Returns:
            True if click was successful
        """
        try:
            # Check if element is safe
            if check_honeypot:
                is_safe, details = await self.honeypot_detector.is_element_safe(
                    self.page, selector
                )
                
                if not is_safe:
                    print(f"[!] Honeypot detected, skipping: {selector}")
                    print(f"    Details: {details}")
                    return False
                
                print(f"[+] Element is safe: {selector}")
            
            # Check visibility
            is_visible, checks = await self.honeypot_detector.is_element_visible(
                self.page, selector
            )
            
            if not is_visible:
                print(f"[!] Element not visible, skipping: {selector}")
                return False
            
            # Scroll element into view if needed
            element = await self.page.query_selector(selector)
            if element:
                await element.scroll_into_view_if_needed()
                
                # Wait for scroll to complete
                await self.page.wait_for_timeout(
                    int(TemporalEntropy.generate_delay(ActivityType.SCROLL_PAUSE) * 1000)
                )
            
            # Pre-click delay (decision time)
            pre_click_delay = TemporalEntropy.generate_delay(ActivityType.DECISION)
            await self.page.wait_for_timeout(int(pre_click_delay * 1000))
            
            # Perform click
            await self.page.click(selector)
            print(f"[+] Clicked: {selector}")
            
            # Post-click delay
            post_click_delay = TemporalEntropy.generate_delay(ActivityType.PAGE_LOAD)
            await self.page.wait_for_timeout(int(post_click_delay * 1000))
            
            return True
            
        except Exception as e:
            print(f"[!] Click failed on {selector}: {e}")
            return False
    
    async def read_and_explore(self, max_scrolls: int = None):
        """
        Main reading and exploration loop
        Simulates a user reading through a page
        """
        print("\n[*] Starting reading and exploration behavior")
        
        # Initial page load pause (user orients themselves)
        initial_pause = TemporalEntropy.generate_delay(ActivityType.THINKING)
        print(f"[*] Initial orientation pause: {initial_pause:.2f}s")
        await self.page.wait_for_timeout(int(initial_pause * 1000))
        
        # Perform burst scrolling with reading behavior
        await self.scroll_behavior.burst_scroll(
            num_scrolls=max_scrolls,
            reading_behavior=True
        )
        
        print("[+] Reading and exploration complete")


# Example usage for Playwright
async def example_news_site_exploration(page):
    """
    Example: Exploring a news site with human-like behavior
    """
    from playwright.async_api import async_playwright
    
    # Navigate to news site
    await page.goto('https://example-news-site.com')
    
    # Create navigation controller
    navigator = NavigationBehavior(page)
    
    # Read the homepage
    await navigator.read_and_explore(max_scrolls=5)
    
    # Find and click on an article (with safety checks)
    article_selector = 'article a.headline'
    success = await navigator.safe_click(article_selector)
    
    if success:
        # Read the article
        await navigator.read_and_explore(max_scrolls=8)
    
    print("[+] Exploration complete")


# Standalone example
if __name__ == '__main__':
    import asyncio
    from playwright.async_api import async_playwright
    
    async def main():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            # Example navigation
            await example_news_site_exploration(page)
            
            await browser.close()
    
    asyncio.run(main())
