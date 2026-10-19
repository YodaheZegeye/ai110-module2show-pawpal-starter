"""
pawpal_system.py

Logic layer for PawPal+ containing the core domain classes and stubs
for pets, owners, tasks, schedules, and scheduling behavior.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple


@dataclass
class Pet:
    """Represents a pet receiving care."""
    name: str
    species: str
    energy_level: str = "medium"
    preferences: List[str] = field(default_factory=list)

    def get_summary(self) -> str:
        """Return a formatted string summarizing the pet's profile."""
        pass

    def add_preference(self, pref: str) -> None:
        """Add a care preference or special instruction for this pet."""
        pass


@dataclass
class Owner:
    """Represents a pet owner with available time constraints."""
    name: str
    available_time_minutes: int = 60
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Associate a pet with this owner."""
        pass

    def set_available_time(self, minutes: int) -> None:
        """Set the owner's total time budget for pet care today."""
        pass

    def get_available_time(self) -> int:
        """Return the owner's available time budget in minutes."""
        pass


@dataclass
class Task:
    """Represents an individual care task to be scheduled."""
    title: str
    duration_minutes: int
    priority: str = "medium"  # 'low', 'medium', 'high'
    category: str = "general"  # 'walk', 'feeding', 'medication', 'grooming', 'enrichment'
    is_mandatory: bool = False
    preferred_time: Optional[str] = None

    def get_priority_score(self) -> int:
        """Return a numerical score for priority sorting (e.g., high=3, medium=2, low=1)."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert task attributes into a dictionary format for UI tables."""
        pass


@dataclass
class Schedule:
    """Represents the generated daily care plan."""
    pet: Optional[Pet] = None
    scheduled_tasks: List[Dict[str, Any]] = field(default_factory=list)
    unscheduled_tasks: List[Dict[str, Any]] = field(default_factory=list)
    total_duration_minutes: int = 0
    reasoning: List[str] = field(default_factory=list)

    def add_scheduled_task(self, task: Task, time_slot: str, reason: str) -> None:
        """Add a task that was successfully scheduled into the plan."""
        pass

    def add_unscheduled_task(self, task: Task, reason: str) -> None:
        """Record a task that could not be scheduled along with the reason."""
        pass

    def get_formatted_plan(self) -> str:
        """Return a user-friendly string representation of the scheduled daily plan."""
        pass


class Scheduler:
    """Planning engine responsible for scheduling tasks within constraints."""

    def __init__(self, strategy: str = "priority_first") -> None:
        self.strategy: str = strategy

    def generate_plan(
        self,
        tasks: List[Task],
        available_time_minutes: int,
        pet: Optional[Pet] = None
    ) -> Schedule:
        """Generate a daily care schedule based on priorities and time constraints."""
        pass

    def _sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """Order tasks based on mandatory status, priority, and duration."""
        pass

    def _evaluate_fit(self, task: Task, remaining_time: int) -> Tuple[bool, str]:
        """Determine whether a task fits within the remaining time budget."""
        pass
