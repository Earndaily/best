"""
The Infiltrator - Kinematic Mouse Brain
Generates human-like mouse movements using Cubic Bézier curves with physics simulation

Features:
- Cubic Bézier curve path generation
- Fitts's Law velocity modeling (target distance + size affects speed)
- Micro-tremor simulation (hand jitter)
- Overshoot and correction behavior
- Randomized acceleration/deceleration
"""

import random
import math
from typing import Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class Point:
    """2D point representation"""
    x: float
    y: float
    
    def distance_to(self, other: 'Point') -> float:
        """Calculate Euclidean distance to another point"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


class BezierCurve:
    """Cubic Bézier curve generator for smooth mouse paths"""
    
    @staticmethod
    def calculate_point(t: float, p0: Point, p1: Point, p2: Point, p3: Point) -> Point:
        """
        Calculate point on cubic Bézier curve at parameter t
        P(t) = (1-t)³P₀ + 3(1-t)²tP₁ + 3(1-t)t²P₂ + t³P₃
        
        Args:
            t: Parameter from 0 to 1
            p0: Start point
            p1: First control point
            p2: Second control point
            p3: End point
        """
        u = 1 - t
        tt = t * t
        uu = u * u
        uuu = uu * u
        ttt = tt * t
        
        # Calculate Bézier curve point
        x = (uuu * p0.x + 
             3 * uu * t * p1.x + 
             3 * u * tt * p2.x + 
             ttt * p3.x)
        
        y = (uuu * p0.y + 
             3 * uu * t * p1.y + 
             3 * u * tt * p2.y + 
             ttt * p3.y)
        
        return Point(x, y)
    
    @staticmethod
    def generate_control_points(start: Point, end: Point, randomness: float = 0.3) -> Tuple[Point, Point]:
        """
        Generate control points for natural-looking curves
        
        Args:
            start: Starting point
            end: Ending point
            randomness: How much randomness in control point placement (0-1)
        
        Returns:
            Tuple of (control_point_1, control_point_2)
        """
        # Calculate midpoint
        mid_x = (start.x + end.x) / 2
        mid_y = (start.y + end.y) / 2
        
        # Calculate perpendicular offset for curve depth
        dx = end.x - start.x
        dy = end.y - start.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Perpendicular vector (rotated 90 degrees)
        perp_x = -dy
        perp_y = dx
        
        # Normalize
        if distance > 0:
            perp_x /= distance
            perp_y /= distance
        
        # Random curve depth (typically 10-30% of distance)
        curve_depth = distance * random.uniform(0.1, 0.3) * randomness
        
        # Random offset direction (left or right of straight line)
        offset_direction = random.choice([-1, 1])
        
        # Generate control points with randomization
        # First control point (near start)
        cp1_offset_ratio = random.uniform(0.2, 0.4)
        cp1 = Point(
            start.x + dx * cp1_offset_ratio + perp_x * curve_depth * offset_direction * random.uniform(0.5, 1.0),
            start.y + dy * cp1_offset_ratio + perp_y * curve_depth * offset_direction * random.uniform(0.5, 1.0)
        )
        
        # Second control point (near end)
        cp2_offset_ratio = random.uniform(0.6, 0.8)
        cp2 = Point(
            start.x + dx * cp2_offset_ratio + perp_x * curve_depth * offset_direction * random.uniform(0.5, 1.0),
            start.y + dy * cp2_offset_ratio + perp_y * curve_depth * offset_direction * random.uniform(0.5, 1.0)
        )
        
        return cp1, cp2


class FittsLaw:
    """
    Fitts's Law implementation for realistic movement timing
    MT = a + b × log₂(D/W + 1)
    
    Where:
    - MT = Movement Time
    - D = Distance to target
    - W = Width of target (target size)
    - a, b = empirically determined constants
    """
    
    # Empirical constants (in milliseconds)
    A_CONSTANT = 0.0
    B_CONSTANT = 150.0  # Typical value for pointing tasks
    
    @staticmethod
    def calculate_movement_time(distance: float, target_width: float) -> float:
        """
        Calculate expected movement time based on Fitts's Law
        
        Args:
            distance: Distance to target in pixels
            target_width: Width/size of target in pixels
        
        Returns:
            Movement time in milliseconds
        """
        # Prevent division by zero
        if target_width <= 0:
            target_width = 1
        
        # Calculate Index of Difficulty (ID)
        index_of_difficulty = math.log2(distance / target_width + 1)
        
        # Calculate movement time
        movement_time = FittsLaw.A_CONSTANT + FittsLaw.B_CONSTANT * index_of_difficulty
        
        # Add some randomness (±20%)
        randomness = random.uniform(0.8, 1.2)
        
        return movement_time * randomness


class MicroTremor:
    """Simulates natural hand tremor/jitter"""
    
    @staticmethod
    def apply_tremor(point: Point, intensity: float = 0.5) -> Point:
        """
        Apply micro-tremor to a point
        
        Args:
            point: Original point
            intensity: Tremor intensity (0-1), typically 0.3-0.7
        
        Returns:
            Point with tremor applied
        """
        # Tremor follows a small normal distribution
        tremor_x = random.gauss(0, intensity)
        tremor_y = random.gauss(0, intensity)
        
        return Point(
            point.x + tremor_x,
            point.y + tremor_y
        )


class HumanMouseMovement:
    """Main class for generating human-like mouse movements"""
    
    def __init__(self):
        self.overshoot_probability = 0.10  # 10% chance of overshooting
        self.min_steps = 10  # Minimum number of steps in path
        self.max_steps = 100  # Maximum number of steps in path
    
    def generate_path(
        self, 
        start: Tuple[float, float], 
        end: Tuple[float, float],
        target_size: Optional[float] = None
    ) -> List[Tuple[float, float, float]]:
        """
        Generate a human-like mouse path from start to end
        
        Args:
            start: Starting (x, y) coordinates
            end: Ending (x, y) coordinates
            target_size: Size of target element (for Fitts's Law)
        
        Returns:
            List of (x, y, timestamp_ms) tuples representing the path
        """
        start_point = Point(*start)
        end_point = Point(*end)
        
        # Calculate distance
        distance = start_point.distance_to(end_point)
        
        # Default target size if not provided
        if target_size is None:
            target_size = max(10, distance * 0.05)  # 5% of distance
        
        # Calculate movement time using Fitts's Law
        base_movement_time = FittsLaw.calculate_movement_time(distance, target_size)
        
        # Decide if we should overshoot
        should_overshoot = random.random() < self.overshoot_probability
        
        if should_overshoot:
            # Generate overshoot path
            return self._generate_overshoot_path(start_point, end_point, base_movement_time)
        else:
            # Generate normal path
            return self._generate_normal_path(start_point, end_point, base_movement_time)
    
    def _generate_normal_path(
        self, 
        start: Point, 
        end: Point, 
        movement_time_ms: float
    ) -> List[Tuple[float, float, float]]:
        """Generate a normal Bézier curve path"""
        
        # Generate control points
        cp1, cp2 = BezierCurve.generate_control_points(start, end)
        
        # Calculate number of steps based on distance
        distance = start.distance_to(end)
        num_steps = int(max(self.min_steps, min(self.max_steps, distance / 10)))
        
        path = []
        current_time = 0.0
        
        for i in range(num_steps + 1):
            # Progress along curve (0 to 1)
            t = i / num_steps
            
            # Non-linear time progression (ease-in-ease-out)
            # Starts slow, speeds up in middle, slows at end
            time_progress = self._ease_in_out_cubic(t)
            timestamp = movement_time_ms * time_progress
            
            # Calculate point on Bézier curve
            point = BezierCurve.calculate_point(t, start, cp1, cp2, end)
            
            # Apply micro-tremor
            tremor_intensity = 0.3 if i > 0 and i < num_steps else 0.1  # Less tremor at start/end
            point = MicroTremor.apply_tremor(point, tremor_intensity)
            
            path.append((point.x, point.y, timestamp))
        
        return path
    
    def _generate_overshoot_path(
        self, 
        start: Point, 
        end: Point, 
        movement_time_ms: float
    ) -> List[Tuple[float, float, float]]:
        """
        Generate path with overshoot and correction
        Simulates when user overshoots target and corrects back
        """
        
        # Calculate overshoot point (5-15% beyond target)
        overshoot_ratio = random.uniform(1.05, 1.15)
        dx = end.x - start.x
        dy = end.y - start.y
        
        overshoot_point = Point(
            start.x + dx * overshoot_ratio,
            start.y + dy * overshoot_ratio
        )
        
        # Path 1: Start to overshoot (70% of time)
        path1 = self._generate_normal_path(start, overshoot_point, movement_time_ms * 0.7)
        
        # Path 2: Overshoot back to target (30% of time)
        # This is faster and more direct (correction)
        path2 = self._generate_normal_path(
            overshoot_point, 
            end, 
            movement_time_ms * 0.3
        )
        
        # Adjust timestamps for second path
        last_timestamp = path1[-1][2]
        path2_adjusted = [
            (x, y, t + last_timestamp) for x, y, t in path2
        ]
        
        # Combine paths
        return path1 + path2_adjusted[1:]  # Skip duplicate point
    
    @staticmethod
    def _ease_in_out_cubic(t: float) -> float:
        """
        Cubic ease-in-ease-out function for natural acceleration
        Slow at start, fast in middle, slow at end
        """
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2


class PlaywrightMouseController:
    """Integration with Playwright for realistic mouse movement"""
    
    def __init__(self, page):
        """
        Args:
            page: Playwright page object
        """
        self.page = page
        self.movement_generator = HumanMouseMovement()
    
    async def move_to_element(self, selector: str, duration_override: Optional[float] = None):
        """
        Move mouse to an element using human-like path
        
        Args:
            selector: CSS selector for target element
            duration_override: Optional override for movement duration (ms)
        """
        # Get element bounding box
        element = await self.page.query_selector(selector)
        if not element:
            raise ValueError(f"Element not found: {selector}")
        
        box = await element.bounding_box()
        if not box:
            raise ValueError(f"Element not visible: {selector}")
        
        # Calculate target center point with small randomization
        target_x = box['x'] + box['width'] / 2 + random.uniform(-5, 5)
        target_y = box['y'] + box['height'] / 2 + random.uniform(-5, 5)
        
        # Get current mouse position (or start from 0,0 if first move)
        current_position = await self.page.evaluate('() => [window.mouseX || 0, window.mouseY || 0]')
        
        # Generate human path
        path = self.movement_generator.generate_path(
            start=tuple(current_position),
            end=(target_x, target_y),
            target_size=min(box['width'], box['height'])
        )
        
        # Execute movement
        for x, y, timestamp in path:
            await self.page.mouse.move(x, y)
            
            # Track mouse position in page context
            await self.page.evaluate(f'window.mouseX = {x}; window.mouseY = {y};')
            
            # Wait for next step (convert to seconds)
            if path.index((x, y, timestamp)) < len(path) - 1:
                next_timestamp = path[path.index((x, y, timestamp)) + 1][2]
                delay_ms = next_timestamp - timestamp
                await self.page.wait_for_timeout(int(delay_ms))
    
    async def human_click(self, selector: str, button: str = 'left'):
        """
        Perform a human-like click with natural movement
        
        Args:
            selector: CSS selector for element to click
            button: Mouse button ('left', 'right', 'middle')
        """
        # Move to element
        await self.move_to_element(selector)
        
        # Small delay before click (20-100ms)
        await self.page.wait_for_timeout(random.randint(20, 100))
        
        # Click
        await self.page.mouse.click(
            *await self.page.evaluate('() => [window.mouseX, window.mouseY]'),
            button=button
        )


# Example usage
async def example_usage():
    """Example of how to use the kinematic mouse brain"""
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Create mouse controller
        mouse = PlaywrightMouseController(page)
        
        # Navigate to page
        await page.goto('https://example.com')
        
        # Perform human-like click on an element
        await mouse.human_click('button#submit')
        
        await browser.close()
