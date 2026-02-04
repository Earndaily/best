"""
The Infiltrator - Complete Integration Example
Demonstrates all components working together in a realistic browsing session

This example simulates a human user:
1. Starting with configured identity (proxy, timezone, network masking)
2. Navigating to a target website
3. Reading and exploring content naturally
4. Interacting with elements using human-like movements
5. Avoiding honeypots and detection mechanisms
"""

import asyncio
import sys
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright

# Import Infiltrator components
from kinematic_mouse import PlaywrightMouseController
from temporal_entropy import TemporalEntropy, ActivityType
from reading_mimicry import NavigationBehavior, HoneypotDetector


class InfiltratorSession:
    """Main orchestrator for a complete infiltration session"""
    
    def __init__(self):
        self.config = None
        self.identity = None
        self.browser = None
        self.context = None
        self.page = None
        self.mouse_controller = None
        self.navigator = None
    
    def load_configuration(self):
        """Load configuration from bootstrap process"""
        try:
            # Load main config
            with open('/tmp/infiltrator_config.env', 'r') as f:
                config_lines = f.readlines()
                self.config = {}
                for line in config_lines:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        self.config[key] = value
            
            # Load identity
            with open('/tmp/infiltrator_identity.json', 'r') as f:
                self.identity = json.load(f)
            
            print("[+] Configuration loaded successfully")
            print(f"    Target: {self.config.get('TARGET_URL')}")
            print(f"    Location: {self.identity.get('city')}, {self.identity.get('country')}")
            print(f"    Timezone: {self.identity.get('timezone')}")
            
            return True
            
        except Exception as e:
            print(f"[!] Failed to load configuration: {e}")
            return False
    
    async def initialize_browser(self):
        """Initialize Playwright browser with all protections"""
        print("\n[*] Initializing browser with protections...")
        
        playwright = await async_playwright().start()
        
        # Browser launch arguments for stealth
        launch_args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-features=IsolateOrigins,site-per-process',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
        ]
        
        # Launch browser
        self.browser = await playwright.chromium.launch(
            headless=False,  # Visible for demonstration
            args=launch_args,
            # Proxy configuration
            proxy={
                'server': f"{self.config['PROXY_PROTOCOL']}://{self.config['PROXY_HOST']}:{self.config['PROXY_PORT']}",
                'username': self.config.get('PROXY_USERNAME'),
                'password': self.config.get('PROXY_PASSWORD')
            } if self.config.get('PROXY_HOST') else None
        )
        
        # Create context with proper configuration
        self.context = await self.browser.new_context(
            user_agent=self.config['USER_AGENT'],
            viewport={'width': 1920, 'height': 1080},
            locale=self._get_locale_from_timezone(),
            timezone_id=self.identity['timezone'],
            # Additional fingerprinting protection
            permissions=['geolocation'],
            geolocation={
                'latitude': float(self.identity.get('latitude', 0)),
                'longitude': float(self.identity.get('longitude', 0))
            } if self.identity.get('latitude') else None
        )
        
        # Create page
        self.page = await self.context.new_page()
        
        # Inject WebRTC protection
        await self._inject_webrtc_protection()
        
        # Inject additional stealth scripts
        await self._inject_stealth_scripts()
        
        print("[+] Browser initialized with full protection suite")
        
        return True
    
    def _get_locale_from_timezone(self):
        """Convert timezone to locale string"""
        # Simple mapping - can be expanded
        timezone_locale_map = {
            'America/New_York': 'en-US',
            'America/Los_Angeles': 'en-US',
            'Europe/London': 'en-GB',
            'Europe/Paris': 'fr-FR',
            'Asia/Tokyo': 'ja-JP',
            'Asia/Shanghai': 'zh-CN',
        }
        
        return timezone_locale_map.get(
            self.identity['timezone'],
            'en-US'  # Default
        )
    
    async def _inject_webrtc_protection(self):
        """Inject WebRTC kill-switch"""
        try:
            webrtc_script_path = Path('/app/infiltrator/webrtc_killswitch.js')
            
            if webrtc_script_path.exists():
                with open(webrtc_script_path, 'r') as f:
                    webrtc_script = f.read()
                
                # Extract just the first protection function
                # (the complete override, not the examples)
                script_lines = webrtc_script.split('\n')
                actual_script = []
                in_function = False
                paren_count = 0
                
                for line in script_lines:
                    if '(function()' in line and not in_function:
                        in_function = True
                        paren_count = 0
                    
                    if in_function:
                        actual_script.append(line)
                        paren_count += line.count('(') - line.count(')')
                        
                        if '})();' in line and paren_count == 0:
                            break
                
                script_to_inject = '\n'.join(actual_script)
                await self.page.add_init_script(script_to_inject)
                
                print("[+] WebRTC protection injected")
        
        except Exception as e:
            print(f"[!] Failed to inject WebRTC protection: {e}")
    
    async def _inject_stealth_scripts(self):
        """Inject additional stealth/anti-detection scripts"""
        
        # Remove automation indicators
        stealth_script = """
        // Remove webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // Spoof plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // Spoof languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
        
        // Consistent screen properties
        Object.defineProperty(screen, 'availHeight', {
            get: () => 1080
        });
        Object.defineProperty(screen, 'availWidth', {
            get: () => 1920
        });
        
        // Mock permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        console.log('[Stealth] Anti-detection scripts loaded');
        """
        
        await self.page.add_init_script(stealth_script)
        print("[+] Stealth scripts injected")
    
    async def navigate_to_target(self):
        """Navigate to target URL with human-like behavior"""
        target_url = self.config['TARGET_URL']
        
        print(f"\n[*] Navigating to: {target_url}")
        
        # Pre-navigation pause (user types URL and thinks)
        pre_nav_delay = TemporalEntropy.generate_delay(ActivityType.TYPING_WORD)
        await asyncio.sleep(pre_nav_delay)
        
        # Navigate
        response = await self.page.goto(target_url, wait_until='domcontentloaded')
        
        print(f"[+] Page loaded: {response.status}")
        
        # Post-load pause (user looks at page)
        post_load_delay = TemporalEntropy.generate_delay(ActivityType.PAGE_LOAD)
        await asyncio.sleep(post_load_delay)
        
        return True
    
    async def execute_mission(self):
        """Execute the main browsing mission"""
        print("\n" + "="*60)
        print("MISSION EXECUTION - Human Browsing Simulation")
        print("="*60)
        
        # Initialize navigation components
        self.navigator = NavigationBehavior(self.page)
        self.mouse_controller = PlaywrightMouseController(self.page)
        
        # Simulate realistic browsing session
        try:
            # 1. Initial page exploration
            print("\n[*] Phase 1: Initial page exploration")
            await self.navigator.read_and_explore(max_scrolls=3)
            
            # 2. Look for interesting links
            print("\n[*] Phase 2: Finding interesting content")
            await self._find_and_click_interesting_link()
            
            # 3. Deep read on new page
            print("\n[*] Phase 3: Deep content reading")
            await self.navigator.read_and_explore(max_scrolls=None)  # Full page
            
            # 4. Random interaction (if applicable)
            print("\n[*] Phase 4: Random interaction")
            await self._random_interaction()
            
            print("\n[+] Mission execution complete")
            return True
            
        except Exception as e:
            print(f"\n[!] Mission execution error: {e}")
            return False
    
    async def _find_and_click_interesting_link(self):
        """Find and click an interesting link on the page"""
        
        # Common selectors for article/content links
        link_selectors = [
            'article a',
            'a.article-link',
            'a.headline',
            '.post a',
            'h2 a',
            'h3 a',
            'a[href*="article"]',
            'a[href*="post"]',
            'a[href*="blog"]'
        ]
        
        for selector in link_selectors:
            try:
                # Find all matching links
                links = await self.page.query_selector_all(selector)
                
                if not links:
                    continue
                
                # Try up to 3 random links
                for link in links[:3]:
                    # Check if link is safe
                    link_href = await link.get_attribute('href')
                    
                    if not link_href or link_href.startswith('#'):
                        continue
                    
                    # Check visibility and honeypot
                    is_visible = await link.is_visible()
                    if not is_visible:
                        continue
                    
                    # Get link text for logging
                    link_text = await link.inner_text()
                    print(f"    Found link: {link_text[:50]}...")
                    
                    # Attempt safe click
                    try:
                        await link.scroll_into_view_if_needed()
                        
                        # Use kinematic mouse movement
                        await self.mouse_controller.human_click(selector)
                        
                        print(f"[+] Clicked link: {link_text[:50]}")
                        
                        # Wait for navigation
                        await self.page.wait_for_load_state('domcontentloaded')
                        
                        return True
                        
                    except Exception as e:
                        print(f"    Failed to click: {e}")
                        continue
            
            except Exception as e:
                continue
        
        print("[!] No suitable links found")
        return False
    
    async def _random_interaction(self):
        """Perform a random realistic interaction"""
        
        interactions = [
            self._scroll_to_bottom,
            self._hover_over_images,
            self._read_comments_section
        ]
        
        # Pick random interaction
        interaction = interactions[int(len(interactions) * hash(str(asyncio.get_event_loop().time())) % len(interactions))]
        
        try:
            await interaction()
        except Exception as e:
            print(f"[!] Random interaction failed: {e}")
    
    async def _scroll_to_bottom(self):
        """Scroll to bottom of page"""
        print("    Action: Scrolling to bottom")
        await self.navigator.scroll_behavior.burst_scroll(reading_behavior=True)
    
    async def _hover_over_images(self):
        """Hover over images on page"""
        print("    Action: Hovering over images")
        
        images = await self.page.query_selector_all('img')
        
        for img in images[:3]:  # Hover over up to 3 images
            try:
                is_visible = await img.is_visible()
                if is_visible:
                    await img.hover()
                    hover_time = TemporalEntropy.generate_delay(ActivityType.THINKING)
                    await asyncio.sleep(hover_time)
            except:
                pass
    
    async def _read_comments_section(self):
        """Scroll to and read comments"""
        print("    Action: Reading comments")
        
        comment_selectors = [
            '#comments',
            '.comments',
            '[id*="comment"]',
            '.comment-section'
        ]
        
        for selector in comment_selectors:
            try:
                element = await self.page.query_selector(selector)
                if element:
                    await element.scroll_into_view_if_needed()
                    
                    # Read comments
                    read_time = TemporalEntropy.generate_delay(ActivityType.READING_PARAGRAPH)
                    await asyncio.sleep(read_time)
                    
                    return
            except:
                continue
    
    async def cleanup(self):
        """Clean up resources"""
        print("\n[*] Cleaning up...")
        
        if self.context:
            await self.context.close()
        
        if self.browser:
            await self.browser.close()
        
        print("[+] Cleanup complete")


async def main():
    """Main execution function"""
    
    print("="*60)
    print("THE INFILTRATOR - Complete Integration")
    print("="*60)
    
    # Create session
    session = InfiltratorSession()
    
    try:
        # Load configuration
        if not session.load_configuration():
            print("[!] Configuration loading failed")
            return 1
        
        # Initialize browser
        if not await session.initialize_browser():
            print("[!] Browser initialization failed")
            return 1
        
        # Navigate to target
        if not await session.navigate_to_target():
            print("[!] Navigation failed")
            return 1
        
        # Execute mission
        if not await session.execute_mission():
            print("[!] Mission execution failed")
            return 1
        
        print("\n" + "="*60)
        print("[+] INFILTRATION COMPLETE - All systems nominal")
        print("="*60)
        
        # Keep browser open for inspection
        await asyncio.sleep(10)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
        return 130
    
    except Exception as e:
        print(f"\n[!] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        await session.cleanup()


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
