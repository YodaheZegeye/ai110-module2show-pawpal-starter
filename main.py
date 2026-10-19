"""
main.py

Terminal test harness for PawPal+.
Verifies multi-pet setup, task assignment, and scheduler output.
"""

import sys

# Ensure UTF-8 stdout encoding if possible on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    print("=" * 64)
    print("[PawPal+] Daily Care Planning System - Terminal Demo")
    print("=" * 64)

    # 1. Create an Owner with a daily time constraint (e.g., 75 minutes)
    owner = Owner(name="Yodahe", available_time_minutes=75)

    # 2. Create at least two pets
    biscuit = Pet(
        name="Biscuit",
        species="dog",
        energy_level="high",
        preferences=["loves fetch", "needs morning outdoor time"]
    )
    mochi = Pet(
        name="Mochi",
        species="cat",
        energy_level="low",
        preferences=["quiet feeding area", "gentle grooming"]
    )

    # 3. Add tasks with different durations, priorities, and categories
    biscuit.add_task(
        Task(
            title="Morning park walk",
            duration_minutes=35,
            priority="high",
            category="walk",
            preferred_time="08:00"
        )
    )
    biscuit.add_task(
        Task(
            title="Brush coat & check paws",
            duration_minutes=20,
            priority="low",
            category="grooming"
        )
    )

    mochi.add_task(
        Task(
            title="Administer allergy medication",
            duration_minutes=10,
            priority="high",
            category="medication",
            is_mandatory=True
        )
    )
    mochi.add_task(
        Task(
            title="Interactive laser & feather play",
            duration_minutes=20,
            priority="medium",
            category="enrichment"
        )
    )

    # 4. Associate pets with the owner
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    print(f"Owner: {owner.name} | Total Daily Time Budget: {owner.available_time_minutes} min")
    print(f"Registered Pets: {len(owner.pets)} ({', '.join(p.name for p in owner.pets)})")
    print(f"Total Tasks Across Pets: {len(owner.get_all_tasks())}")
    print("-" * 64)

    # 5. Generate schedule through Scheduler (retrieves tasks via owner.get_all_tasks())
    scheduler = Scheduler()
    schedule = scheduler.generate_plan(owner=owner, start_time="08:00")

    # 6. Print Today's Schedule cleanly formatted
    print("\n" + schedule.get_formatted_plan())
    print("\n" + "=" * 64)


if __name__ == "__main__":
    main()
