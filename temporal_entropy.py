"""
The Infiltrator - Temporal Entropy
Generates human-like timing delays using Gaussian (Normal) Distribution

Replaces static delays with statistically natural variations that mimic
human behavior patterns.
"""

import random
import time
from typing import Optional, Dict
from dataclasses import dataclass
from enum import Enum


class ActivityType(Enum):
    """Common activity types with characteristic timing profiles"""
    READING_WORD = "reading_word"           # Reading a single word
    READING_SENTENCE = "reading_sentence"   # Reading a sentence
    READING_PARAGRAPH = "reading_paragraph" # Reading a paragraph
    THINKING = "thinking"                    # Pausing to think
    TYPING_CHAR = "typing_char"             # Typing a single character
    TYPING_WORD = "typing_word"             # Typing a word
    MOUSE_MOVE = "mouse_move"               # Moving mouse
    CLICK_DELAY = "click_delay"             # Delay before clicking
    PAGE_LOAD = "page_load"                 # Waiting for page to load
    FORM_FILL = "form_fill"                 # Filling a form field
    DECISION = "decision"                   # Making a decision
    SCROLL_PAUSE = "scroll_pause"           # Pausing while scrolling


@dataclass
class TimingProfile:
    """Statistical profile for a timing activity"""
    mean: float          # Mean delay in seconds
    std_dev: float       # Standard deviation in seconds
    min_value: float     # Minimum allowed value (clamp floor)
    max_value: float     # Maximum allowed value (clamp ceiling)


class TemporalEntropy:
    """
    Generates human-like timing delays using Gaussian distribution
    
    All times are in seconds unless otherwise specified
    """
    
    # Predefined timing profiles based on human behavior studies
    PROFILES: Dict[ActivityType, TimingProfile] = {
        # Reading times (based on average reading speed of ~250 wpm)
        ActivityType.READING_WORD: TimingProfile(
            mean=0.24,        # 240ms per word
            std_dev=0.08,     # ±80ms variance
            min_value=0.10,
            max_value=0.50
        ),
        ActivityType.READING_SENTENCE: TimingProfile(
            mean=2.5,         # ~2.5 seconds for average sentence
            std_dev=0.8,
            min_value=1.0,
            max_value=5.0
        ),
        ActivityType.READING_PARAGRAPH: TimingProfile(
            mean=8.0,         # ~8 seconds for short paragraph
            std_dev=2.5,
            min_value=3.0,
            max_value=15.0
        ),
        
        # Thinking/decision times
        ActivityType.THINKING: TimingProfile(
            mean=1.5,         # Brief pause to think
            std_dev=0.5,
            min_value=0.5,
            max_value=3.0
        ),
        ActivityType.DECISION: TimingProfile(
            mean=2.5,         # Making a choice
            std_dev=1.0,
            min_value=0.8,
            max_value=5.0
        ),
        
        # Typing times (based on ~40 wpm typing speed)
        ActivityType.TYPING_CHAR: TimingProfile(
            mean=0.15,        # 150ms per character
            std_dev=0.05,
            min_value=0.08,
            max_value=0.30
        ),
        ActivityType.TYPING_WORD: TimingProfile(
            mean=0.75,        # ~750ms per word (5 chars)
            std_dev=0.25,
            min_value=0.30,
            max_value=1.50
        ),
        
        # Mouse interactions
        ActivityType.MOUSE_MOVE: TimingProfile(
            mean=0.50,        # Movement duration
            std_dev=0.15,
            min_value=0.20,
            max_value=1.00
        ),
        ActivityType.CLICK_DELAY: TimingProfile(
            mean=0.15,        # Delay before clicking
            std_dev=0.05,
            min_value=0.05,
            max_value=0.40
        ),
        
        # Page interactions
        ActivityType.PAGE_LOAD: TimingProfile(
            mean=2.0,         # Waiting for page load
            std_dev=0.5,
            min_value=1.0,
            max_value=4.0
        ),
        ActivityType.FORM_FILL: TimingProfile(
            mean=1.5,         # Filling a form field
            std_dev=0.5,
            min_value=0.5,
            max_value=3.0
        ),
        ActivityType.SCROLL_PAUSE: TimingProfile(
            mean=1.2,         # Pause between scrolls
            std_dev=0.4,
            min_value=0.3,
            max_value=2.5
        )
    }
    
    @staticmethod
    def generate_delay(
        activity: ActivityType,
        multiplier: float = 1.0,
        randomness_factor: float = 1.0
    ) -> float:
        """
        Generate a delay for a specific activity using Gaussian distribution
        
        Args:
            activity: Type of activity being timed
            multiplier: Scale the mean time (e.g., 2.0 for double speed)
            randomness_factor: Scale the variance (1.0 = normal, 2.0 = more random)
        
        Returns:
            Delay time in seconds
        """
        profile = TemporalEntropy.PROFILES[activity]
        
        # Generate from Gaussian distribution
        delay = random.gauss(
            profile.mean * multiplier,
            profile.std_dev * randomness_factor
        )
        
        # Clamp to min/max bounds
        delay = max(profile.min_value, min(profile.max_value, delay))
        
        return delay
    
    @staticmethod
    def generate_custom_delay(
        mean: float,
        std_dev: float,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> float:
        """
        Generate a custom delay with specified parameters
        
        Args:
            mean: Mean delay in seconds
            std_dev: Standard deviation in seconds
            min_value: Optional minimum value
            max_value: Optional maximum value
        
        Returns:
            Delay time in seconds
        """
        delay = random.gauss(mean, std_dev)
        
        if min_value is not None:
            delay = max(min_value, delay)
        if max_value is not None:
            delay = min(max_value, delay)
        
        return delay
    
    @staticmethod
    def generate_reading_time(text: str, wpm: int = 250) -> float:
        """
        Generate realistic reading time for text based on word count
        
        Args:
            text: Text to read
            wpm: Words per minute reading speed
        
        Returns:
            Reading time in seconds
        """
        word_count = len(text.split())
        
        if word_count == 0:
            return 0.0
        
        # Base reading time
        base_time = (word_count / wpm) * 60  # Convert to seconds
        
        # Add Gaussian variance (±20%)
        variance = base_time * 0.2
        reading_time = random.gauss(base_time, variance)
        
        # Minimum time (can't read instantly)
        min_time = word_count * 0.15  # At least 150ms per word
        
        return max(min_time, reading_time)
    
    @staticmethod
    def generate_typing_time(text: str, wpm: int = 40) -> float:
        """
        Generate realistic typing time for text
        
        Args:
            text: Text to type
            wpm: Words per minute typing speed
        
        Returns:
            Typing time in seconds
        """
        char_count = len(text)
        
        if char_count == 0:
            return 0.0
        
        # Average word length is 5 characters
        words = char_count / 5
        
        # Base typing time
        base_time = (words / wpm) * 60
        
        # Add Gaussian variance (±25%)
        variance = base_time * 0.25
        typing_time = random.gauss(base_time, variance)
        
        # Minimum time
        min_time = char_count * 0.08  # At least 80ms per character
        
        return max(min_time, typing_time)
    
    @staticmethod
    def burst_activity(
        activity: ActivityType,
        count: int,
        burst_randomness: float = 0.5
    ) -> list:
        """
        Generate a burst of similar activities with varied timing
        
        Args:
            activity: Type of activity
            count: Number of activities in burst
            burst_randomness: How varied the timing is (0-1)
        
        Returns:
            List of delay times
        """
        delays = []
        
        for i in range(count):
            # First and last items might be slower (startup/ending)
            if i == 0 or i == count - 1:
                multiplier = random.uniform(1.2, 1.5)
            else:
                multiplier = random.uniform(0.8, 1.2)
            
            delay = TemporalEntropy.generate_delay(
                activity,
                multiplier=multiplier,
                randomness_factor=burst_randomness
            )
            
            delays.append(delay)
        
        return delays


class TimingBudget:
    """
    Manages a timing budget for a sequence of actions
    Ensures total time stays within realistic bounds
    """
    
    def __init__(self, total_budget_seconds: float):
        """
        Args:
            total_budget_seconds: Total time budget for all actions
        """
        self.total_budget = total_budget_seconds
        self.remaining_budget = total_budget_seconds
        self.actions_taken = 0
    
    def allocate(self, activity: ActivityType, count: int = 1) -> list:
        """
        Allocate time for activities within budget
        
        Args:
            activity: Type of activity
            count: Number of times to perform activity
        
        Returns:
            List of allocated delays
        """
        if self.remaining_budget <= 0:
            return [0.0] * count
        
        # Calculate ideal time per action
        profile = TemporalEntropy.PROFILES[activity]
        ideal_time = profile.mean * count
        
        # Scale if budget is tight
        if ideal_time > self.remaining_budget:
            scale = self.remaining_budget / ideal_time
        else:
            scale = 1.0
        
        delays = []
        for _ in range(count):
            delay = TemporalEntropy.generate_delay(activity, multiplier=scale)
            delays.append(delay)
            self.remaining_budget -= delay
            self.actions_taken += 1
        
        return delays
    
    def get_remaining_time(self) -> float:
        """Get remaining time in budget"""
        return max(0.0, self.remaining_budget)


# Utility functions for common patterns
def sleep_human(activity: ActivityType):
    """Sleep for a human-like duration based on activity type"""
    delay = TemporalEntropy.generate_delay(activity)
    time.sleep(delay)


def async_sleep_human(activity: ActivityType):
    """
    Async version - returns delay value for use with asyncio.sleep
    """
    return TemporalEntropy.generate_delay(activity)


# Example usage
if __name__ == '__main__':
    print("Temporal Entropy - Timing Demonstration")
    print("=" * 50)
    
    # Example 1: Reading delays
    print("\nReading Times:")
    for i in range(5):
        delay = TemporalEntropy.generate_delay(ActivityType.READING_SENTENCE)
        print(f"  Sentence {i+1}: {delay:.3f}s")
    
    # Example 2: Typing delays
    print("\nTyping Times:")
    for i in range(5):
        delay = TemporalEntropy.generate_delay(ActivityType.TYPING_CHAR)
        print(f"  Character {i+1}: {delay:.3f}s")
    
    # Example 3: Reading time for text
    print("\nReading Time for Sample Text:")
    sample_text = "This is a sample sentence that we will measure reading time for."
    reading_time = TemporalEntropy.generate_reading_time(sample_text)
    print(f"  Text: '{sample_text}'")
    print(f"  Reading time: {reading_time:.2f}s")
    
    # Example 4: Burst activities
    print("\nBurst Scroll Pauses:")
    scroll_delays = TemporalEntropy.burst_activity(ActivityType.SCROLL_PAUSE, count=5)
    for i, delay in enumerate(scroll_delays):
        print(f"  Scroll {i+1}: {delay:.3f}s")
    
    # Example 5: Timing budget
    print("\nTiming Budget Example (10 second budget):")
    budget = TimingBudget(total_budget_seconds=10.0)
    reading_times = budget.allocate(ActivityType.READING_SENTENCE, count=3)
    thinking_times = budget.allocate(ActivityType.THINKING, count=2)
    
    print(f"  Reading times: {[f'{t:.2f}s' for t in reading_times]}")
    print(f"  Thinking times: {[f'{t:.2f}s' for t in thinking_times]}")
    print(f"  Remaining budget: {budget.get_remaining_time():.2f}s")
