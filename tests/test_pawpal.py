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
