"""
tests/test_pawpal.py

Unit tests for PawPal+ core classes.
Tests task completion status and pet task addition.
"""

import pytest
from pawpal_system import Task, Pet


def test_task_completion():
    """Verify that calling mark_complete() changes the task's completion status."""
    task = Task(title="Morning walk", duration_minutes=20, priority="high")
    
    # Verify initial status is False
    assert task.completed is False
    
    # Mark task complete
    task.mark_complete()
    
    # Verify status changed to True
    assert task.completed is True


def test_task_addition():
    """Verify that adding a task to a Pet increases that pet's task count."""
    pet = Pet(name="Biscuit", species="dog")
    
    # Initial task count should be 0
    assert len(pet.tasks) == 0
    
    # Add a task
    walk_task = Task(title="Park stroll", duration_minutes=30, priority="medium")
    pet.add_task(walk_task)
    
    # Task count should now be 1
    assert len(pet.tasks) == 1
    assert pet.tasks[0].title == "Park stroll"
    assert pet.tasks[0].pet_name == "Biscuit"
    
    # Add a second task
    feeding_task = Task(title="Evening dinner", duration_minutes=10, priority="high")
    pet.add_task(feeding_task)
    
    # Task count should now be 2
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
    # Filter by completion
    pending = scheduler.filter_tasks(all_tasks, completed=False)
    assert len(pending) == 2
    assert t1 not in pending

    # Filter by pet
    biscuit_tasks = scheduler.filter_tasks(all_tasks, pet_name="Biscuit")
    assert len(biscuit_tasks) == 2
    assert all(t.pet_name == "Biscuit" for t in biscuit_tasks)

    # Filter by both
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



