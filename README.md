# 🐾 PawPal+ Pet Care Planner

PawPal+ is an intelligent pet care management and daily scheduling assistant built in Python and Streamlit. It helps busy pet owners balance multiple pets, medical routines, daily walks, and enrichment activities within realistic daily time constraints.

---

## 📖 Scenario & Problem

Pet owners often juggle diverse care responsibilities across multiple pets — from strict medication regimens (e.g., daily insulin or ear drops) to high-energy park runs and grooming. Balancing these activities against a finite daily time budget is stressful, leading to skipped tasks, double-bookings, and schedule breakdowns.

**PawPal+ solves this by acting as an intelligent scheduling assistant:**
- Centralizes multi-pet profiles, preferences, and task rosters.
- Prioritizes critical, mandatory care over optional enrichment.
- Detects scheduling collisions before they happen.
- Fits routines into the owner's available time and provides transparent reasoning for every decision.
- Automatically rolls recurring daily and weekly tasks forward into the next cycle.

---

## ✨ Features

| Feature | Method / Class | Description |
| :--- | :--- | :--- |
| **Intelligent Plan Generation** | `Scheduler.generate_plan()` | Allocates tasks sequentially starting at `08:00`, prioritizing mandatory/urgent items, respecting the daily time budget, and logging human-readable reasoning for every included or omitted task. |
| **Chronological Time Sorting** | `Scheduler.sort_by_time()` | Orders tasks chronologically using a tuple lambda key on `preferred_time` (`"HH:MM"`), placing flexible/untimed tasks cleanly at the end. |
| **Multi-Criteria Filtering** | `Scheduler.filter_tasks()` | Dynamically filters tasks by completion status (`completed=True/False`), specific pet (`pet_name`), or both combined without mutating original lists. |
| **Lightweight Conflict Detection** | `Scheduler.detect_conflicts()` | Scans tasks pairwise for identical start times across the same pet or different pets, raising descriptive warning banners without crashing execution. |
| **Automated Recurrence Engine** | `Task.mark_completed()`, `Pet.mark_task_complete()`, `Owner.mark_task_complete()` | When a daily or weekly task is marked complete, Python's `datetime.timedelta` calculates the next due date (+1 day or +7 days) and appends a fresh pending clone to the pet's roster. Non-recurring tasks (`as-needed`) complete without spawning. |
| **Multi-Pet Management** | `Owner.get_all_tasks()` | Consolidates tasks across all registered pets into a single pool for global scheduling while preserving individual pet ownership. |
| **Interactive Streamlit UI** | `app.py` | Full web application featuring live task filters, real-time conflict banners, visual metrics, schedule timelines, and one-click task completion. |

---

## 🚀 Getting Started

### Prerequisites & Installation

```bash
# Clone the repository and enter the directory
git clone https://github.com/YodaheZegeye/ai110-module2show-pawpal-starter.git
cd ai110-module2show-pawpal-starter

# Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

- **Streamlit Web UI**:
  ```bash
  streamlit run app.py
  ```
- **Terminal Demo Script**:
  ```bash
  python main.py
  ```
- **Automated Test Suite**:
  ```bash
  python -m pytest -v
  ```

---

## 📸 Demo Walkthrough

### 1. Main UI Features & User Actions

The PawPal+ interface is divided into logical, interactive sections:

1. **Sidebar — Owner Profile & Budget Configuration**:
   - Set the owner name and daily available time budget (e.g., 75 minutes).
   - Adjusting this slider immediately updates budget constraints for schedule generation.
2. **Left Column — Pet Management (`Manage Pets`)**:
   - Review registered pets, species, energy levels, preferences, and current task counts.
   - Use the **➕ Add a New Pet** expandable form to register new animals.
3. **Right Column — Task Management (`Add Pet Care Tasks`)**:
   - Assign tasks to any registered pet with title, duration (minutes), priority (`high`/`medium`/`low`), category, mandatory flag, preferred start time (`HH:MM`), and recurrence frequency (`daily`, `weekly`, or `as-needed`).
4. **Full Width — Task Dashboard & Real-Time Conflict Alerts**:
   - **Conflict Banners**: If two tasks share the exact same preferred time, an amber `st.warning` banner appears immediately at the top of the table.
   - **Filter Controls**: Select a specific pet or view all; filter by pending, completed, or all tasks.
   - **Chronological Table**: Tasks are displayed in chronological order using `Scheduler.sort_by_time()`.
   - **One-Click Completion**: Click **Complete** on any task to mark it done. If recurring, a success alert confirms the auto-generation of tomorrow's or next week's occurrence.
5. **Full Width — Plan Generation & Rationale**:
   - Set a target start time (default `08:00`) and click **⚡ Generate Schedule**.
   - Review scheduled timeline items, omitted tasks due to budget deficits, and the step-by-step reasoning log explaining why each decision was made.

---

### 2. Example User Workflow

1. **Configure Budget**: Set the daily budget to `75 min` in the sidebar.
2. **Add a Pet**: Add a cat named `"Mochi"` (Species: Cat, Energy: Low).
3. **Add Tasks with Conflicts**:
   - Add `"Morning park walk"` for Biscuit at `08:00` (35 min, High priority).
   - Add `"Administer allergy medication"` for Mochi at `08:00` (10 min, High priority, Mandatory).
4. **Observe Conflict Detection**: An immediate warning displays:
   `Warning: Conflict at 08:00! 'Morning park walk' and 'Administer allergy medication' are scheduled at the same time for different pets (Biscuit and Mochi).`
5. **Filter Tasks**: Use the dropdown to isolate `"Mochi"` — only Mochi's tasks appear. Switch back to `"All Pets"`.
6. **Generate Schedule**: Click **Generate Schedule**. Notice how the mandatory medication is prioritized first at `08:00`, followed by the walk at `08:10`.
7. **Complete a Recurring Task**: Click **Complete** on `"Morning park walk"` (Daily). A message confirms:
   `Completed 'Morning park walk' (Daily). Next occurrence auto-created for 2026-10-20.`

---

### 3. Sample CLI Output (`main.py`)

Running `python main.py` in the terminal exercises all algorithms end-to-end:

```text
================================================================
[PawPal+] Smart Scheduling, Sorting & Filtering Demo
================================================================
Owner: Yodahe | Available Time: 85 min
Total raw tasks entered (out of order): 6
  - [19:30] Evening park run (Biscuit) [Pending]
  - [07:15] Early breakfast feeding (Biscuit) [Done]
  - [08:00] Morning park walk (Biscuit) [Pending]
  - [14:00] Mid-day paw check & brushing (Biscuit) [Pending]
  - [08:00] Morning ear drops (Mochi) [Pending]
  - [15:30] Afternoon feather wand play (Mochi) [Pending]

----------------------------------------------------------------
🕒 1. Tasks Sorted Chronologically (sort_by_time)
----------------------------------------------------------------
  - 07:15 - Early breakfast feeding (Biscuit, 15 min)
  - 08:00 - Morning park walk (Biscuit, 30 min)
  - 08:00 - Morning ear drops (Mochi, 10 min)
  - 14:00 - Mid-day paw check & brushing (Biscuit, 20 min)
  - 15:30 - Afternoon feather wand play (Mochi, 25 min)
  - 19:30 - Evening park run (Biscuit, 30 min)

----------------------------------------------------------------
🔍 2. Filtering Tasks (filter_tasks)
----------------------------------------------------------------
• Active Pending Tasks (5):
    - Evening park run (Biscuit)
    - Morning park walk (Biscuit)
    - Mid-day paw check & brushing (Biscuit)
    - Morning ear drops (Mochi)
    - Afternoon feather wand play (Mochi)

• Mochi's Tasks (2):
    - Morning ear drops (Priority: high)
    - Afternoon feather wand play (Priority: medium)

----------------------------------------------------------------
📅 3. Generated Plan for Pending Tasks
----------------------------------------------------------------
Daily plan for All pets:
Time Budget: 85 min | Scheduled: 70 min | Remaining: 15 min
------------------------------------------------------------
  08:00 - Morning ear drops (10 min) [Mochi] [priority: high]
  08:10 - Evening park run (30 min) [Biscuit] [priority: high]
  08:40 - Morning park walk (30 min) [Biscuit] [priority: high]

Unscheduled Tasks (Exceeded constraints):
  - Afternoon feather wand play (25 min) [Mochi] - Exceeds remaining time budget by 10 min (needed 25 min, only 15 min left).
  - Mid-day paw check & brushing (20 min) [Biscuit] - Exceeds remaining time budget by 5 min (needed 20 min, only 15 min left).

Time Conflicts & Warnings:
  ! Warning: Conflict at 08:00! 'Morning park walk' and 'Morning ear drops' are scheduled at the same time for different pets (Biscuit and Mochi).

Scheduling Rationale:
  - [08:00] Scheduled 'Morning ear drops' (10 min) for Mochi: Fits within available time (10 min allocated, 75 min remaining). Mandatory item.
  - [08:10] Scheduled 'Evening park run' (30 min) for Biscuit: Fits within available time (30 min allocated, 45 min remaining). High priority.
  - [08:40] Scheduled 'Morning park walk' (30 min) for Biscuit: Fits within available time (30 min allocated, 15 min remaining). High priority.
  - [Omitted] 'Afternoon feather wand play' (25 min) for Mochi: Exceeds remaining time budget by 10 min (needed 25 min, only 15 min left).
  - [Omitted] 'Mid-day paw check & brushing' (20 min) for Biscuit: Exceeds remaining time budget by 5 min (needed 20 min, only 15 min left).

----------------------------------------------------------------
🔁 4. Recurring Tasks Auto-Generation (timedelta)
----------------------------------------------------------------
• Completed: 'Morning insulin' (Daily)
  -> Auto-generated next occurrence: due 2026-10-20 (completed=False)
• Completed: 'Weekly brush & flea wash' (Weekly)
  -> Auto-generated next occurrence: due 2026-10-26 (completed=False)

----------------------------------------------------------------
⚠️ 5. Lightweight Conflict Detection (detect_conflicts)
----------------------------------------------------------------
  Warning: Conflict at 08:00! 'Morning park walk' and 'Morning ear drops' are scheduled at the same time for different pets (Biscuit and Mochi).
================================================================
```

---

## 🏗️ Architecture & Domain Model

PawPal+ maintains a strict separation of concerns between entity data models and the scheduling logic:

- **`Task`**: Models atomic care activities with duration, priority (`high`/`medium`/`low`), mandatory flag, category, preferred time (`HH:MM`), recurrence frequency, due date, and completion status.
- **`Pet`**: Holds pet profiles (species, energy level, care preferences) and manages pet-scoped tasks via `add_task()` and `mark_task_complete()`.
- **`Owner`**: Represents the owner, tracks the daily time budget (`available_time_minutes`), and provides unified multi-pet access via `get_all_tasks()` and `mark_task_complete()`.
- **`Schedule`**: Encapsulates the generated outcome: confirmed timeline slots, omitted tasks, budget tracking (`remaining_time_minutes`), conflict warnings, and human-readable reasoning for every decision.
- **`Scheduler`**: The planning engine. Retrieves tasks directly from `Owner.get_all_tasks()`, prioritizes tasks by urgency, assigns progressive chronological time slots starting at `08:00`, detects collisions, and validates constraints.

The updated UML class diagram is maintained in [`diagrams/uml_final.mmd`](diagrams/uml_final.mmd).

---

## 📐 Algorithmic Details

### 1. Chronological Sorting (`Scheduler.sort_by_time()`)
- Uses Python's `sorted()` with a tuple key:
  ```python
  key=lambda t: (0, t.preferred_time) if (t.preferred_time and ":" in t.preferred_time) else (1, "99:99")
  ```
- Guaranteed stable 24-hour chronological ordering (`"07:15"` < `"08:00"` < `"14:00"`).
- Untimed/flexible tasks (`preferred_time=None`) cleanly group at the end without raising errors.

### 2. Multi-Criteria Filtering (`Scheduler.filter_tasks()`)
- Supports simultaneous or independent filtering by completion state (`completed=True/False`) and pet ownership (`pet_name="..."`).
- Always returns a new list of objects without mutating the underlying data.

### 3. Lightweight Conflict Detection (`Scheduler.detect_conflicts()`)
- Filters for tasks with valid `"HH:MM"` times.
- Runs pairwise comparisons ($O(N^2)$ across timed tasks) to detect exact time collisions.
- Differentiates whether the collision affects the **same pet** or **different pets**.
- Non-crashing: emits human-readable warning strings that attach to `Schedule.conflicts` and render as alert banners in the UI.

### 4. Recurrence Math (`Task.mark_completed()`)
- Uses Python's standard library `datetime.timedelta`:
  - `"daily"` $\rightarrow$ `date.today() + timedelta(days=1)`
  - `"weekly"` $\rightarrow$ `date.today() + timedelta(weeks=1)`
  - `"as-needed"` $\rightarrow$ returns `None` (non-recurring)
- Copies all task metadata (title, duration, priority, category, time, pet name) to the new instance with `completed=False`.

---

## 🧪 Testing PawPal+

### Running the Tests

```bash
python -m pytest -v
```

### What the Tests Cover

The automated test suite in [`tests/test_pawpal.py`](tests/test_pawpal.py) contains **17 unit tests** across four essential areas:

| Category | Tests | What They Verify |
| :--- | :--- | :--- |
| **Core Behavior** | `test_task_completion`, `test_task_addition` | `mark_complete()` toggles completed status; `add_task()` appends tasks to pet roster. |
| **Sorting Correctness** | `test_sort_by_time`, `test_sort_by_time_already_sorted`, `test_sort_by_time_reverse_order`, `test_sort_all_untimed_tasks` | Validates chronological ordering; confirms idempotency on sorted input; checks reverse-order sorting; verifies untimed tasks group at end. |
| **Recurrence Logic** | `test_recurring_daily_task`, `test_recurring_weekly_task`, `test_pet_mark_task_complete_recurrence`, `test_as_needed_task_no_recurrence`, `test_recurring_task_preserves_attributes` | Validates +1 day and +7 days `timedelta` calculations; ensures `as-needed` tasks do not recur; verifies cloned successors inherit all attributes. |
| **Conflict Detection** | `test_detect_conflicts_same_pet`, `test_detect_conflicts_different_pets`, `test_no_conflicts`, `test_conflict_detection_three_way`, `test_conflict_detection_no_timed_tasks` | Confirms warnings for same-pet and cross-pet collisions; verifies empty warning list when no collisions exist; checks 3-way pairwise detection ($C(3,2) = 3$ warnings); handles empty/untimed inputs. |

### Test Output

```text
============================= test session starts =============================
platform win32 -- Python 3.14.4, pytest-9.1.1, pluggy-1.7.0 -- C:\Users\yodah\Documents\Projects\ai110-module2show-pawpal-starter\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\yodah\Documents\Projects\ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collecting ... collected 17 items

tests/test_pawpal.py::test_task_completion PASSED                        [  5%]
tests/test_pawpal.py::test_task_addition PASSED                          [ 11%]
tests/test_pawpal.py::test_sort_by_time PASSED                           [ 17%]
tests/test_pawpal.py::test_filter_tasks PASSED                           [ 23%]
tests/test_pawpal.py::test_recurring_daily_task PASSED                   [ 29%]
tests/test_pawpal.py::test_recurring_weekly_task PASSED                  [ 35%]
tests/test_pawpal.py::test_pet_mark_task_complete_recurrence PASSED      [ 41%]
tests/test_pawpal.py::test_detect_conflicts_same_pet PASSED              [ 47%]
tests/test_pawpal.py::test_detect_conflicts_different_pets PASSED        [ 52%]
tests/test_pawpal.py::test_no_conflicts PASSED                           [ 58%]
tests/test_pawpal.py::test_sort_by_time_already_sorted PASSED            [ 64%]
tests/test_pawpal.py::test_sort_by_time_reverse_order PASSED             [ 70%]
tests/test_pawpal.py::test_sort_all_untimed_tasks PASSED                 [ 76%]
tests/test_pawpal.py::test_as_needed_task_no_recurrence PASSED           [ 82%]
tests/test_pawpal.py::test_recurring_task_preserves_attributes PASSED    [ 88%]
tests/test_pawpal.py::test_conflict_detection_three_way PASSED           [ 94%]
tests/test_pawpal.py::test_conflict_detection_no_timed_tasks PASSED      [100%]

============================= 17 passed in 0.03s ==============================
```

### Confidence Level

**⭐⭐⭐⭐⭐ (5 / 5)** — All 17 automated tests pass consistently across happy paths and complex edge cases (untimed tasks, reverse sorting, three-way collisions, attribute inheritance, and non-recurring tasks), providing high confidence in system stability and reliability.
