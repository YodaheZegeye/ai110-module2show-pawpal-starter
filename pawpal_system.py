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
from datetime import date, timedelta
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
    due_date: Optional[str] = None

    def get_priority_score(self) -> int:
        """Calculate and return numerical priority score with mandatory weighting."""
        priority_weights = {"high": 30, "medium": 20, "low": 10}
        score = priority_weights.get(self.priority.lower(), 10)
        if self.is_mandatory:
            score += 100
        return score

    def mark_completed(self, base_date: Optional[date] = None) -> Optional["Task"]:
        """
        Mark task as completed and automatically generate the next recurring instance.

        For 'daily' tasks, schedules the next occurrence for base_date + 1 day.
        For 'weekly' tasks, schedules the next occurrence for base_date + 7 days.
        For non-recurring or 'as-needed' tasks, returns None.

        Args:
            base_date: Reference date for recurrence calculation (defaults to date.today()).

        Returns:
            A new pending Task instance for the next occurrence, or None if non-recurring.
        """
        self.completed = True
        ref_date = base_date or date.today()

        freq = (self.frequency or "").lower()
        if freq == "daily":
            next_date = ref_date + timedelta(days=1)
        elif freq == "weekly":
            next_date = ref_date + timedelta(weeks=1)
        else:
            return None

        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
            is_mandatory=self.is_mandatory,
            preferred_time=self.preferred_time,
            pet_name=self.pet_name,
            frequency=self.frequency,
            completed=False,
            due_date=next_date.isoformat(),
        )

    def mark_complete(self, base_date: Optional[date] = None) -> Optional["Task"]:
        """Alias for mark_completed()."""
        return self.mark_completed(base_date=base_date)

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
            "due_date": self.due_date or "Today",
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

    def mark_task_complete(self, task: Task, base_date: Optional[date] = None) -> Optional[Task]:
        """
        Mark a pet's task as complete and append its next recurring occurrence if applicable.

        Args:
            task: The Task to mark completed.
            base_date: Optional reference date for calculating the next recurrence.

        Returns:
            The newly created recurring Task instance if recurring, or None.
        """
        next_task = task.mark_complete(base_date=base_date)
        if next_task is not None:
            self.add_task(next_task)
        return next_task

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

    def mark_task_complete(self, task: Task, base_date: Optional[date] = None) -> Optional[Task]:
        """
        Mark a task complete across owner's pets and add recurring instance to the matching pet.

        Args:
            task: The Task to complete.
            base_date: Optional reference date for recurrence calculation.

        Returns:
            The newly created recurring Task instance if recurring, or None.
        """
        next_task = task.mark_complete(base_date=base_date)
        if next_task is not None:
            for p in self.pets:
                if p.name == task.pet_name:
                    p.add_task(next_task)
                    break
        return next_task

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
    conflicts: List[str] = field(default_factory=list)

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

        if self.conflicts:
            lines.append("\nTime Conflicts & Warnings:")
            for warn in self.conflicts:
                lines.append(f"  ! {warn}")

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
            available_time_minutes=budget,
            conflicts=self.detect_conflicts(task_pool)
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

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        """
        Identify pairwise time conflicts between tasks with identical preferred times.

        Scans tasks for identical 'HH:MM' time slots across the same pet or different pets.
        Generates descriptive warning messages without halting execution or raising exceptions.

        Args:
            tasks: List of Task objects to inspect for time collisions.

        Returns:
            A list of user-facing warning strings detailing conflicting tasks and times.
        """
        warnings: List[str] = []
        timed_tasks = [t for t in tasks if t.preferred_time and ":" in t.preferred_time]

        for i in range(len(timed_tasks)):
            for j in range(i + 1, len(timed_tasks)):
                t1 = timed_tasks[i]
                t2 = timed_tasks[j]
                if t1.preferred_time == t2.preferred_time:
                    p1 = t1.pet_name or "Unassigned"
                    p2 = t2.pet_name or "Unassigned"
                    target = f"the same pet ({p1})" if p1 == p2 else f"different pets ({p1} and {p2})"
                    warnings.append(
                        f"Warning: Conflict at {t1.preferred_time}! '{t1.title}' and '{t2.title}' are scheduled at the same time for {target}."
                    )
        return warnings

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """
        Sort tasks chronologically by preferred_time ('HH:MM') using a lambda key.

        Timed tasks ('HH:MM') are sorted earlier in chronological order.
        Untimed or flexible tasks (preferred_time is None) are placed at the end.

        Args:
            tasks: List of Task objects to sort.

        Returns:
            A new list of Task objects sorted chronologically.
        """
        return sorted(
            tasks,
            key=lambda t: (0, t.preferred_time) if (t.preferred_time and ":" in t.preferred_time) else (1, "99:99")
        )

    def filter_tasks(
        self,
        tasks: List[Task],
        completed: Optional[bool] = None,
        pet_name: Optional[str] = None
    ) -> List[Task]:
        """
        Filter a list of tasks by completion status, pet name, or both criteria.

        Args:
            tasks: The collection of Task objects to filter.
            completed: If specified (True/False), filters tasks matching completion state.
            pet_name: If specified, filters tasks assigned to this specific pet.

        Returns:
            A filtered list of Task objects satisfying all provided criteria.
        """
        filtered = list(tasks)
        if completed is not None:
            filtered = [t for t in filtered if t.completed == completed]
        if pet_name is not None:
            filtered = [t for t in filtered if t.pet_name == pet_name]
        return filtered

    def _sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """
        Sort tasks using a multi-criteria priority heuristic.

        Orders tasks by:
        1. Priority score (mandatory items boosted by +100, then high > medium > low).
        2. Duration (longer tasks first as tiebreaker to greedily allocate available time).

        Args:
            tasks: List of Task objects to prioritize.

        Returns:
            Sorted list of Task objects ordered from highest to lowest urgency.
        """
        return sorted(
            tasks,
            key=lambda t: (
                t.get_priority_score(),
                -t.duration_minutes
            ),
            reverse=True
        )

    def _evaluate_fit(self, task: Task, remaining_time: int) -> Tuple[bool, str]:
        """
        Evaluate if a task fits within the remaining time budget and provide reasoning.

        Args:
            task: The Task being evaluated.
            remaining_time: Current remaining minutes in the owner's budget.

        Returns:
            Tuple of (fits_boolean, explanation_reason_string).
        """
        if task.duration_minutes <= remaining_time:
            importance = "Mandatory item" if task.is_mandatory else f"{task.priority.capitalize()} priority"
            return True, f"Fits within available time ({task.duration_minutes} min allocated, {remaining_time - task.duration_minutes} min remaining). {importance}."
        else:
            deficit = task.duration_minutes - remaining_time
            return False, f"Exceeds remaining time budget by {deficit} min (needed {task.duration_minutes} min, only {remaining_time} min left)."
