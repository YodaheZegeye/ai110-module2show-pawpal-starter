"""
main.py

Terminal test harness for PawPal+.
Demonstrates:
1. Adding tasks out of chronological order.
2. Sorting tasks by time using Scheduler.sort_by_time().
3. Filtering tasks by completion status and pet name using Scheduler.filter_tasks().
4. Generating and displaying the constrained daily care schedule.
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
    print("[PawPal+] Smart Scheduling, Sorting & Filtering Demo")
    print("=" * 64)

    # 1. Create an Owner and Pets
    owner = Owner(name="Yodahe", available_time_minutes=85)
    biscuit = Pet(name="Biscuit", species="dog", energy_level="high")
    mochi = Pet(name="Mochi", species="cat", energy_level="low")

    # 2. Add tasks intentionally OUT OF CHRONOLOGICAL ORDER
    # Notice the mixed times: 19:30, 07:15, 14:00, 08:00, and one completed
    biscuit.add_task(
        Task(
            title="Evening park run",
            duration_minutes=30,
            priority="high",
            category="walk",
            preferred_time="19:30"
        )
    )
    biscuit.add_task(
        Task(
            title="Early breakfast feeding",
            duration_minutes=15,
            priority="high",
            category="feeding",
            preferred_time="07:15",
            completed=True  # Already finished!
        )
    )
    biscuit.add_task(
        Task(
            title="Morning park walk",
            duration_minutes=30,
            priority="high",
            category="walk",
            preferred_time="08:00"  # Clashes with Mochi's 08:00 ear drops!
        )
    )
    biscuit.add_task(
        Task(
            title="Mid-day paw check & brushing",
            duration_minutes=20,
            priority="low",
            category="grooming",
            preferred_time="14:00"
        )
    )

    mochi.add_task(
        Task(
            title="Morning ear drops",
            duration_minutes=10,
            priority="high",
            category="medication",
            is_mandatory=True,
            preferred_time="08:00"
        )
    )
    mochi.add_task(
        Task(
            title="Afternoon feather wand play",
            duration_minutes=25,
            priority="medium",
            category="enrichment",
            preferred_time="15:30"
        )
    )

    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    scheduler = Scheduler()
    all_tasks = owner.get_all_tasks()

    print(f"Owner: {owner.name} | Available Time: {owner.available_time_minutes} min")
    print(f"Total raw tasks entered (out of order): {len(all_tasks)}")
    for t in all_tasks:
        status = "Done" if t.completed else "Pending"
        print(f"  - [{t.preferred_time or 'No Time'}] {t.title} ({t.pet_name}) [{status}]")

    # --- Feature 1: Chronological Sorting by Preferred Time ---
    print("\n" + "-" * 64)
    print("🕒 1. Tasks Sorted Chronologically (sort_by_time)")
    print("-" * 64)
    sorted_by_time = scheduler.sort_by_time(all_tasks)
    for t in sorted_by_time:
        print(f"  - {t.preferred_time} - {t.title} ({t.pet_name}, {t.duration_minutes} min)")

    # --- Feature 2: Filtering Logic ---
    print("\n" + "-" * 64)
    print("🔍 2. Filtering Tasks (filter_tasks)")
    print("-" * 64)
    
    # Filter only pending tasks (excluding completed)
    pending_tasks = scheduler.filter_tasks(all_tasks, completed=False)
    print(f"• Active Pending Tasks ({len(pending_tasks)}):")
    for t in pending_tasks:
        print(f"    - {t.title} ({t.pet_name})")

    # Filter tasks specifically for Mochi
    mochi_tasks = scheduler.filter_tasks(all_tasks, pet_name="Mochi")
    print(f"\n• Mochi's Tasks ({len(mochi_tasks)}):")
    for t in mochi_tasks:
        print(f"    - {t.title} (Priority: {t.priority})")

    # --- Feature 3: Schedule Generation ---
    print("\n" + "-" * 64)
    print("📅 3. Generated Plan for Pending Tasks")
    print("-" * 64)
    schedule = scheduler.generate_plan(tasks=pending_tasks, available_time_minutes=owner.available_time_minutes)
    print(schedule.get_formatted_plan())

    # --- Feature 4: Recurring Tasks (Auto-spawning next occurrence) ---
    print("\n" + "-" * 64)
    print("🔁 4. Recurring Tasks Auto-Generation (timedelta)")
    print("-" * 64)
    daily_task = Task(title="Morning insulin", duration_minutes=10, frequency="daily")
    weekly_task = Task(title="Weekly brush & flea wash", duration_minutes=30, frequency="weekly")

    next_daily = daily_task.mark_complete()
    next_weekly = weekly_task.mark_complete()

    print(f"• Completed: '{daily_task.title}' (Daily)")
    print(f"  -> Auto-generated next occurrence: due {next_daily.due_date} (completed={next_daily.completed})")
    print(f"• Completed: '{weekly_task.title}' (Weekly)")
    print(f"  -> Auto-generated next occurrence: due {next_weekly.due_date} (completed={next_weekly.completed})")

    # --- Feature 5: Lightweight Conflict Detection ---
    print("\n" + "-" * 64)
    print("⚠️ 5. Lightweight Conflict Detection (detect_conflicts)")
    print("-" * 64)
    detected_conflicts = scheduler.detect_conflicts(all_tasks)
    if detected_conflicts:
        for warning in detected_conflicts:
            print(f"  {warning}")
    else:
        print("  No time conflicts detected.")
    print("=" * 64)


if __name__ == "__main__":
    main()
