"""
tests/test_pawpal.py

Unit tests for PawPal+ core classes.
Covers task completion, pet task management, sorting, filtering,
recurrence logic, and conflict detection -- including edge cases.
"""

import pytest
from pawpal_system import Task, Pet


# =============================================================================
# ORIGINAL TESTS (Phase 2 & 3)
# =============================================================================

def test_task_completion():
    """Verify that calling mark_complete() changes the task's completion status."""
    task = Task(title="Morning walk", duration_minutes=20, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_task_addition():
    """Verify that adding a task to a Pet increases that pet's task count."""
    pet = Pet(name="Biscuit", species="dog")
    assert len(pet.tasks) == 0
    walk_task = Task(title="Park stroll", duration_minutes=30, priority="medium")
    pet.add_task(walk_task)
    assert len(pet.tasks) == 1
    assert pet.tasks[0].title == "Park stroll"
    assert pet.tasks[0].pet_name == "Biscuit"
    feeding_task = Task(title="Evening dinner", duration_minutes=10, priority="high")
    pet.add_task(feeding_task)
    assert len(pet.tasks) == 2


def test_sort_by_time():
    """Verify that Scheduler.sort_by_time orders tasks chronologically."""
    from pawpal_system import Scheduler
    scheduler = Scheduler()
    t1 = Task(title="Evening walk", duration_minutes=30, preferred_time="18:30")
    t2 = Task(title="Morning breakfast", duration_minutes=15, preferred_time="07:45")
    t3 = Task(title="Afternoon play", duration_minutes=20, preferred_time="13:00")
    t4 = Task(title="Cuddle time", duration_minutes=10, preferred_time=None)
    sorted_tasks = scheduler.sort_by_time([t1, t2, t3, t4])
    assert [t.preferred_time for t in sorted_tasks[:3]] == ["07:45", "13:00", "18:30"]
    assert sorted_tasks[3].preferred_time is None


def test_filter_tasks():
    """Verify that Scheduler.filter_tasks filters by completion status and pet name."""
    from pawpal_system import Scheduler
    scheduler = Scheduler()
    t1 = Task(title="Walk", duration_minutes=30, pet_name="Biscuit", completed=True)
    t2 = Task(title="Brushing", duration_minutes=20, pet_name="Biscuit", completed=False)
    t3 = Task(title="Litter box", duration_minutes=10, pet_name="Mochi", completed=False)
    all_tasks = [t1, t2, t3]
    pending = scheduler.filter_tasks(all_tasks, completed=False)
    assert len(pending) == 2
    assert t1 not in pending
    biscuit_tasks = scheduler.filter_tasks(all_tasks, pet_name="Biscuit")
    assert len(biscuit_tasks) == 2
    assert all(t.pet_name == "Biscuit" for t in biscuit_tasks)
    biscuit_pending = scheduler.filter_tasks(all_tasks, completed=False, pet_name="Biscuit")
    assert len(biscuit_pending) == 1
    assert biscuit_pending[0].title == "Brushing"


def test_recurring_daily_task():
    """Verify that completing a daily task creates a successor due in +1 day."""
    from datetime import date, timedelta
    fixed_today = date(2026, 10, 19)
    task = Task(title="Daily feeding", duration_minutes=15, frequency="daily")
    next_task = task.mark_complete(base_date=fixed_today)
    assert task.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.title == "Daily feeding"
    assert next_task.due_date == (fixed_today + timedelta(days=1)).isoformat()
    assert next_task.due_date == "2026-10-20"


def test_recurring_weekly_task():
    """Verify that completing a weekly task creates a successor due in +7 days."""
    from datetime import date, timedelta
    fixed_today = date(2026, 10, 19)
    task = Task(title="Weekly bath", duration_minutes=45, frequency="weekly")
    next_task = task.mark_complete(base_date=fixed_today)
    assert task.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.due_date == (fixed_today + timedelta(weeks=1)).isoformat()
    assert next_task.due_date == "2026-10-26"


def test_pet_mark_task_complete_recurrence():
    """Verify that Pet.mark_task_complete appends recurring tasks to pet.tasks."""
    from datetime import date
    pet = Pet(name="Biscuit", species="dog")
    walk = Task(title="Morning walk", duration_minutes=30, frequency="daily")
    pet.add_task(walk)
    assert len(pet.tasks) == 1
    next_task = pet.mark_task_complete(walk, base_date=date(2026, 10, 19))
    assert len(pet.tasks) == 2
    assert pet.tasks[0].completed is True
    assert pet.tasks[1].completed is False
    assert pet.tasks[1].due_date == "2026-10-20"


def test_detect_conflicts_same_pet():
    """Verify conflict detection when two tasks for the same pet share preferred_time."""
    from pawpal_system import Scheduler
    scheduler = Scheduler()
    t1 = Task(title="Morning walk", duration_minutes=30, preferred_time="08:00", pet_name="Biscuit")
    t2 = Task(title="Vet appointment", duration_minutes=30, preferred_time="08:00", pet_name="Biscuit")
    warnings = scheduler.detect_conflicts([t1, t2])
    assert len(warnings) == 1
    assert "Conflict at 08:00" in warnings[0]
    assert "the same pet (Biscuit)" in warnings[0]


def test_detect_conflicts_different_pets():
    """Verify conflict detection when two tasks for different pets share preferred_time."""
    from pawpal_system import Scheduler
    scheduler = Scheduler()
    t1 = Task(title="Dog walk", duration_minutes=30, preferred_time="08:00", pet_name="Biscuit")
    t2 = Task(title="Cat medicine", duration_minutes=10, preferred_time="08:00", pet_name="Mochi")
    warnings = scheduler.detect_conflicts([t1, t2])
    assert len(warnings) == 1
    assert "Conflict at 08:00" in warnings[0]
    assert "different pets (Biscuit and Mochi)" in warnings[0]


def test_no_conflicts():
    """Verify that no warnings are generated when tasks have different preferred times."""
    from pawpal_system import Scheduler
    scheduler = Scheduler()
    t1 = Task(title="Morning walk", duration_minutes=30, preferred_time="08:00", pet_name="Biscuit")
    t2 = Task(title="Cat medicine", duration_minutes=10, preferred_time="09:00", pet_name="Mochi")
    warnings = scheduler.detect_conflicts([t1, t2])
    assert len(warnings) == 0


# =============================================================================
# NEW EDGE CASE TESTS -- Phase 4 Extension
# =============================================================================

def test_sort_by_time_already_sorted():
    """
    SORTING EDGE CASE: Verify sort_by_time is stable when input is already in order.

    Why this matters: Sorting an already-sorted list must produce the exact same
    order. This confirms the lambda key does not accidentally scramble correctly
    ordered tasks (a property called 'sort stability').
    """
    from pawpal_system import Scheduler
    scheduler = Scheduler()
    t1 = Task(title="Breakfast",  duration_minutes=15, preferred_time="07:00")
    t2 = Task(title="Medication", duration_minutes=10, preferred_time="10:30")
    t3 = Task(title="Dinner",     duration_minutes=20, preferred_time="18:00")
    sorted_tasks = scheduler.sort_by_time([t1, t2, t3])
    assert sorted_tasks[0].preferred_time == "07:00"
    assert sorted_tasks[1].preferred_time == "10:30"
    assert sorted_tasks[2].preferred_time == "18:00"


def test_sort_by_time_reverse_order():
    """
    SORTING EDGE CASE: Verify sort_by_time correctly reorders reverse-ordered input.

    Why this matters: Tasks are often added throughout the day (e.g. evening task
    created before a morning task). This confirms the sort fully reverses a
    worst-case input rather than only partially correcting it.
    """
    from pawpal_system import Scheduler
    scheduler = Scheduler()
    t1 = Task(title="Night walk",  duration_minutes=30, preferred_time="21:00")
    t2 = Task(title="Dinner",      duration_minutes=20, preferred_time="17:00")
    t3 = Task(title="Lunch treat", duration_minutes=10, preferred_time="12:00")
    t4 = Task(title="Breakfast",   duration_minutes=15, preferred_time="07:30")
    sorted_tasks = scheduler.sort_by_time([t1, t2, t3, t4])
    times = [t.preferred_time for t in sorted_tasks]
    assert times == ["07:30", "12:00", "17:00", "21:00"]


def test_sort_all_untimed_tasks():
    """
    SORTING EDGE CASE: Verify sort_by_time handles a list where ALL tasks are untimed.

    Why this matters: If every task has preferred_time=None, the lambda key assigns
    all tasks a sentinel tuple of (1, '99:99'). The function must not crash and
    must return all tasks -- none may be silently dropped.
    """
    from pawpal_system import Scheduler
    scheduler = Scheduler()
    t1 = Task(title="Free play",  duration_minutes=20, preferred_time=None)
    t2 = Task(title="Cuddle",     duration_minutes=15, preferred_time=None)
    t3 = Task(title="Enrichment", duration_minutes=30, preferred_time=None)
    sorted_tasks = scheduler.sort_by_time([t1, t2, t3])
    assert len(sorted_tasks) == 3
    assert all(t.preferred_time is None for t in sorted_tasks)


def test_as_needed_task_no_recurrence():
    """
    RECURRENCE EDGE CASE: Completing an 'as-needed' task must NOT create a successor.

    Why this matters: Only 'daily' and 'weekly' tasks should self-replicate.
    An 'as-needed' task (e.g. emergency vet visit) happens once. If it wrongly
    spawned a copy, pet.tasks would silently grow on every completion.

    How mark_complete works here:
      - Sets self.completed = True
      - Reads self.frequency -- sees "as-needed", not 'daily' or 'weekly'
      - Returns None instead of a new Task
      - Pet.mark_task_complete() checks 'if next_task is not None' before appending
    """
    pet = Pet(name="Biscuit", species="dog")
    one_off = Task(title="Emergency vet visit", duration_minutes=60, frequency="as-needed")
    pet.add_task(one_off)
    assert len(pet.tasks) == 1
    next_task = pet.mark_task_complete(one_off)
    assert next_task is None
    assert one_off.completed is True
    assert len(pet.tasks) == 1  # No ghost copy was added


def test_recurring_task_preserves_attributes():
    """
    RECURRENCE EDGE CASE: The spawned successor must inherit all original task attributes.

    Why this matters: mark_completed() manually constructs a brand-new Task object.
    If any attribute is accidentally omitted (priority, category, is_mandatory,
    preferred_time, pet_name), the clone becomes inconsistently configured.
    This test checks every attribute is faithfully carried over.
    """
    from datetime import date
    original = Task(
        title="Insulin injection",
        duration_minutes=5,
        priority="high",
        category="medication",
        is_mandatory=True,
        preferred_time="08:00",
        pet_name="Mochi",
        frequency="daily",
    )
    next_task = original.mark_complete(base_date=date(2026, 10, 19))
    assert next_task is not None
    assert next_task.title            == original.title
    assert next_task.duration_minutes == original.duration_minutes
    assert next_task.priority         == original.priority
    assert next_task.category         == original.category
    assert next_task.is_mandatory     == original.is_mandatory
    assert next_task.preferred_time   == original.preferred_time
    assert next_task.pet_name         == original.pet_name
    assert next_task.frequency        == original.frequency
    assert next_task.completed is False   # Successor starts fresh as pending
    assert next_task.due_date == "2026-10-20"


def test_conflict_detection_three_way():
    """
    CONFLICT EDGE CASE: Three tasks at the same time must generate pairwise warnings.

    Why this matters: detect_conflicts() uses a nested loop comparing every pair
    (i, j) where j > i. With 3 tasks at the same time there are 3 unique pairs:
      (task1, task2), (task1, task3), (task2, task3)
    The function must report ALL three, not just the first collision found.

    How the nested loop works:
      for i in range(len(timed_tasks)):             # i = 0, 1, 2
          for j in range(i + 1, len(timed_tasks)):  # j always > i, no duplicates
    With 3 items: pairs are (0,1), (0,2), (1,2) -- exactly C(3,2) = 3 comparisons.
    """
    from pawpal_system import Scheduler
    scheduler = Scheduler()
    t1 = Task(title="Dog walk",     duration_minutes=30, preferred_time="08:00", pet_name="Biscuit")
    t2 = Task(title="Cat medicine", duration_minutes=10, preferred_time="08:00", pet_name="Mochi")
    t3 = Task(title="Rabbit feed",  duration_minutes=15, preferred_time="08:00", pet_name="Biscuit")
    warnings = scheduler.detect_conflicts([t1, t2, t3])
    assert len(warnings) == 3
    assert all("Conflict at 08:00" in w for w in warnings)


def test_conflict_detection_no_timed_tasks():
    """
    CONFLICT EDGE CASE: Tasks without preferred_time must produce zero conflict warnings.

    Why this matters: detect_conflicts() first filters for tasks where
    preferred_time is set. If no tasks have times, the inner comparison loop
    never runs, and an empty list must be returned -- not a crash or false positive.
    """
    from pawpal_system import Scheduler
    scheduler = Scheduler()
    t1 = Task(title="Free play", duration_minutes=20, preferred_time=None)
    t2 = Task(title="Grooming",  duration_minutes=30, preferred_time=None)
    warnings = scheduler.detect_conflicts([t1, t2])
    assert warnings == []