"""
pawpal_system.py

Logic layer for PawPal+ containing the core domain classes:
- Task: Represents individual pet care activities.
- Pet: Stores pet details and manages pet-specific tasks.
- Owner: Manages multiple pets and provides unified access to all tasks.
- Schedule: Encapsulates the daily plan, timestamps, duration, and rationale.
- Scheduler: The brain that retrieves tasks from the Owner and generates an
             optimized schedule respecting time and priority constraints.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple


def _advance_time(current_time: str, minutes_to_add: int) -> str:
    """Helper to add minutes to an 'HH:MM' 24-hour time string."""
    try:
        parts = current_time.split(":")
        hour, minute = int(parts[0]), int(parts[1])
        total_minutes = hour * 60 + minute + minutes_to_add
        new_hour = (total_minutes // 60) % 24
        new_minute = total_minutes % 60
        return f"{new_hour:02d}:{new_minute:02d}"
    except Exception:
        return current_time


@dataclass
class Task:
    """Represents a single care activity for a pet."""
    title: str
    duration_minutes: int
    priority: str = "medium"  # 'low', 'medium', 'high'
    category: str = "general"  # 'walk', 'feeding', 'medication', 'grooming', 'enrichment'
    is_mandatory: bool = False
    preferred_time: Optional[str] = None
    pet_name: Optional[str] = None
    frequency: str = "daily"  # 'daily', 'weekly', 'as-needed'
    completed: bool = False

    def get_priority_score(self) -> int:
        """Calculate and return numerical priority score with mandatory weighting."""
        priority_weights = {"high": 30, "medium": 20, "low": 10}
        score = priority_weights.get(self.priority.lower(), 10)
        if self.is_mandatory:
            score += 100
        return score

    def mark_completed(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_complete(self) -> None:
        """Alias for mark_completed() to mark task as completed."""
        self.mark_completed()

    def to_dict(self) -> Dict[str, Any]:
        """Convert task attributes into a dictionary format for UI tables."""
        return {
            "title": self.title,
            "pet": self.pet_name or "All/Unspecified",
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "category": self.category,
            "mandatory": self.is_mandatory,
            "preferred_time": self.preferred_time or "Flexible",
            "frequency": self.frequency,
            "completed": self.completed,
        }


@dataclass
class Pet:
    """Represents a pet receiving care, storing profile data and tasks."""
    name: str
    species: str
    energy_level: str = "medium"
    preferences: List[str] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet and ensure pet_name is set."""
        if not task.pet_name:
            task.pet_name = self.name
        self.tasks.append(task)

    def get_summary(self) -> str:
        """Return a formatted string summarizing the pet's profile."""
        prefs = ", ".join(self.preferences) if self.preferences else "None"
        return f"{self.name} ({self.species.capitalize()}, {self.energy_level} energy) - Preferences: {prefs}"

    def add_preference(self, pref: str) -> None:
        """Add a care preference or special instruction for this pet."""
        clean_pref = pref.strip()
        if clean_pref and clean_pref not in self.preferences:
            self.preferences.append(clean_pref)


@dataclass
class Owner:
    """Represents a pet owner managing multiple pets and daily time constraints."""
    name: str
    available_time_minutes: int = 60
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Associate a pet with this owner."""
        if pet not in self.pets:
            self.pets.append(pet)

    def set_available_time(self, minutes: int) -> None:
        """Set the owner's total time budget for pet care today."""
        self.available_time_minutes = max(0, int(minutes))

    def get_available_time(self) -> int:
        """Return the owner's available time budget in minutes."""
        return self.available_time_minutes

    def get_all_tasks(self) -> List[Task]:
        """Return a consolidated list of all tasks across every pet owned."""
        all_tasks: List[Task] = []
        for pet in self.pets:
            for task in pet.tasks:
                if not task.pet_name:
                    task.pet_name = pet.name
                all_tasks.append(task)
        return all_tasks


@dataclass
class Schedule:
    """Represents the generated daily care plan."""
    owner_name: Optional[str] = None
    pet: Optional[Pet] = None
    available_time_minutes: int = 0
    scheduled_tasks: List[Dict[str, Any]] = field(default_factory=list)
    unscheduled_tasks: List[Dict[str, Any]] = field(default_factory=list)
    total_duration_minutes: int = 0
    reasoning: List[str] = field(default_factory=list)

    @property
    def remaining_time_minutes(self) -> int:
        """Return the unused time remaining in the budget."""
        return max(0, self.available_time_minutes - self.total_duration_minutes)

    def add_scheduled_task(self, task: Task, time_slot: str, reason: str) -> None:
        """Add a task that was successfully scheduled into the plan."""
        entry = {
            "time_slot": time_slot,
            "title": task.title,
            "pet_name": task.pet_name or (self.pet.name if self.pet else "All"),
            "duration_minutes": task.duration_minutes,
            "priority": task.priority,
            "category": task.category,
            "reason": reason,
        }
        self.scheduled_tasks.append(entry)
        self.total_duration_minutes += task.duration_minutes
        self.reasoning.append(
            f"[{time_slot}] Scheduled '{task.title}' ({task.duration_minutes} min) for {entry['pet_name']}: {reason}"
        )

    def add_unscheduled_task(self, task: Task, reason: str) -> None:
        """Record a task that could not be scheduled along with the reason."""
        entry = {
            "title": task.title,
            "pet_name": task.pet_name or (self.pet.name if self.pet else "All"),
            "duration_minutes": task.duration_minutes,
            "priority": task.priority,
            "category": task.category,
            "reason": reason,
        }
        self.unscheduled_tasks.append(entry)
        self.reasoning.append(
            f"[Omitted] '{task.title}' ({task.duration_minutes} min) for {entry['pet_name']}: {reason}"
        )

    def get_formatted_plan(self) -> str:
        """Return a user-friendly string representation of the scheduled daily plan."""
        target = self.pet.name if self.pet else (f"{self.owner_name}'s pets" if self.owner_name else "All pets")
        lines = [
            f"Daily plan for {target}:",
            f"Time Budget: {self.available_time_minutes} min | Scheduled: {self.total_duration_minutes} min | Remaining: {self.remaining_time_minutes} min",
            "-" * 60,
        ]

        if not self.scheduled_tasks:
            lines.append("  No tasks scheduled.")
        else:
            for item in self.scheduled_tasks:
                lines.append(
                    f"  {item['time_slot']} - {item['title']} ({item['duration_minutes']} min) [{item['pet_name']}] [priority: {item['priority']}]"
                )

        if self.unscheduled_tasks:
            lines.append("\nUnscheduled Tasks (Exceeded constraints):")
            for item in self.unscheduled_tasks:
                lines.append(
                    f"  - {item['title']} ({item['duration_minutes']} min) [{item['pet_name']}] - {item['reason']}"
                )

        lines.append("\nScheduling Rationale:")
        for note in self.reasoning:
            lines.append(f"  - {note}")

        return "\n".join(lines)


class Scheduler:
    """
    Planning engine responsible for organizing and scheduling tasks across pets.
    Retrieves tasks directly from the Owner's get_all_tasks() method to satisfy
    multi-pet scheduling requirements.
    """

    def __init__(self, strategy: str = "priority_first") -> None:
        self.strategy: str = strategy

    def generate_plan(
        self,
        owner: Optional[Owner] = None,
        tasks: Optional[List[Task]] = None,
        available_time_minutes: Optional[int] = None,
        pet: Optional[Pet] = None,
        start_time: str = "08:00"
    ) -> Schedule:
        """Generate a prioritized daily care plan within available time constraints."""
        # 1. Retrieve tasks and time budget
        if owner is not None:
            task_pool = owner.get_all_tasks() if tasks is None else list(tasks)
            budget = owner.get_available_time() if available_time_minutes is None else available_time_minutes
            owner_name = owner.name
        else:
            task_pool = list(tasks) if tasks is not None else []
            budget = available_time_minutes if available_time_minutes is not None else 60
            owner_name = None

        # Filter by single pet if a specific pet is requested
        if pet is not None:
            task_pool = [t for t in task_pool if t.pet_name == pet.name or t.pet_name is None]

        schedule = Schedule(
            owner_name=owner_name,
            pet=pet,
            available_time_minutes=budget
        )

        # 2. Sort tasks by priority, mandatory status, and duration
        sorted_tasks = self._sort_tasks(task_pool)

        # 3. Schedule tasks sequentially respecting available time
        current_time = start_time
        remaining_time = budget

        for task in sorted_tasks:
            fits, reason = self._evaluate_fit(task, remaining_time)
            if fits:
                schedule.add_scheduled_task(
                    task=task,
                    time_slot=current_time,
                    reason=reason
                )
                remaining_time -= task.duration_minutes
                current_time = _advance_time(current_time, task.duration_minutes)
            else:
                schedule.add_unscheduled_task(
                    task=task,
                    reason=reason
                )

        return schedule

    def _sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by mandatory status, priority score, and duration."""
        return sorted(
            tasks,
            key=lambda t: (
                t.get_priority_score(),
                -t.duration_minutes
            ),
            reverse=True
        )

    def _evaluate_fit(self, task: Task, remaining_time: int) -> Tuple[bool, str]:
        """Determine whether a task fits within the remaining time budget."""
        if task.duration_minutes <= remaining_time:
            importance = "Mandatory item" if task.is_mandatory else f"{task.priority.capitalize()} priority"
            return True, f"Fits within available time ({task.duration_minutes} min allocated, {remaining_time - task.duration_minutes} min remaining). {importance}."
        else:
            deficit = task.duration_minutes - remaining_time
            return False, f"Exceeds remaining time budget by {deficit} min (needed {task.duration_minutes} min, only {remaining_time} min left)."
