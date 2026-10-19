# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

### Core User Actions
Based on the scenario described in `README.md`, PawPal+ enables the user to perform three core actions:

1. **Add and Manage Pet & Owner Information**: The user can input owner details and create pet profiles (including name, species, care preferences, and daily time constraints).
2. **Add and Customize Pet Care Tasks**: The user can define and organize care tasks (e.g., morning walks, feedings, medication schedules, and grooming) with associated details such as duration, priority level, preferred start time, and recurrence frequency.
3. **Generate and View Today's Daily Plan**: The user can generate a personalized daily schedule based on constraints and task priorities, allowing them to view today's tasks and see the reasoning behind the planned order.

### Initial UML Architecture & Responsibilities
The initial UML design follows a separation of concerns by isolating data models (using Python dataclasses) from business logic (the scheduling engine):

- **`Pet`**: Holds pet profile data including name, species, energy level, and care preferences. Responsible for managing pet-specific tasks and formatting pet summaries.
- **`Owner`**: Represents the pet parent. Responsible for holding daily time availability constraints (in minutes), managing one or more associated pets, and exposing a consolidated task pool via `get_all_tasks()`.
- **`Task`**: Represents an individual care activity (e.g., walking, feeding, administering medication). Responsible for storing duration, priority level, category, preferred time, recurrence frequency, due date, and mandatory status, and providing a numeric priority score for sorting.
- **`Schedule`**: Holds the final plan output for the day. Responsible for tracking scheduled tasks, unscheduled tasks, total duration, remaining budget, conflict warnings, and step-by-step reasoning for the schedule.
- **`Scheduler`**: Acts as the central planning engine. Responsible for sorting tasks based on priority and constraints, evaluating if tasks fit within the owner's remaining time budget, assigning time slots, detecting same-time collisions, and generating transparent reasoning for why tasks were selected or omitted.

**b. Design changes**

- **Did your design change during implementation?**  
  Yes, the design evolved significantly across Phases 2, 3, and 4 to meet real-world scheduling needs.

- **Key changes and rationale:**
  1. **Linked Tasks to Specific Pets (`Task.pet_name`)**:  
     *Why*: While `Owner` could hold multiple pets, `Task` initially lacked a direct reference to a pet. Adding `pet_name` ensures that tasks can be unambiguously associated with, filtered for, and displayed by individual pets in multi-pet households.
  2. **Multi-Pet Task Aggregation (`Owner.get_all_tasks()`)**:  
     *Why*: To cleanly satisfy multi-pet households, each `Pet` manages its own list of tasks, and `Owner` exposes `get_all_tasks()`. The `Scheduler` queries `owner.get_all_tasks()` directly, allowing seamless task organization and prioritization across multiple pets without tight coupling between the scheduler and individual pet lists.
  3. **Added Time Budget & Conflict Tracking to `Schedule` (`Schedule.available_time_minutes`, `Schedule.conflicts`)**:  
     *Why*: The initial `Schedule` only tracked `total_duration_minutes`. Adding `available_time_minutes` allows the scheduler to explain omitted tasks clearly (e.g., *"Excluded 'Park Visit' (40 min) because only 15 min remained of the 60 min budget"*), while `conflicts` preserves time warnings for UI presentation.
  4. **Recurrence Engine Integration (`Task.mark_completed()`, `Pet.mark_task_complete()`, `Owner.mark_task_complete()`)**:  
     *Why*: In real life, pet care is ongoing. Marking a daily walk complete shouldn't delete the routine; it should spawn tomorrow's instance. Adding date math via `timedelta` across the Task/Pet/Owner hierarchy enables automatic recurrence.
  5. **Lightweight Conflict Detection (`Scheduler.detect_conflicts()`)**:  
     *Why*: To prevent double-booking without crashing the application, a non-crashing collision detector was added to alert owners when tasks share the identical minute.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- **Constraints considered**:
  - *Time Availability*: The owner's hard daily limit on pet care minutes (`available_time_minutes`).
  - *Medical / Mandatory Status*: Tasks flagged with `is_mandatory=True` (e.g. daily insulin or eye drops) receive top weighting (+100 score boost).
  - *Priority Level*: Tasks are categorized as `high` (30 pts), `medium` (20 pts), or `low` (10 pts) priority.
  - *Cadence / Recurrence*: Tasks recur on either a `daily` (+1 day) or `weekly` (+7 days) schedule calculated via Python's `timedelta`.
  - *Completion Status*: Completed tasks are filtered out of active scheduling so they do not consume daily budget.
  - *Preferred Time*: Tasks specify optional `HH:MM` timestamps used for chronological sorting and conflict detection.
- **Priority hierarchy rationale**:
  - Medical and mandatory tasks matter most because omitting critical pet care has direct physical health consequences.
  - High-priority essential care (such as outdoor relief walks) comes next, followed by enrichment and low-priority grooming.
  - When priority scores tie, longer task duration acts as a tie-breaker to greedily fit larger commitments into available owner minutes.

**b. Tradeoffs**

1. **Greedy Priority-First Ordering vs. Optimal Knapsack Packing**:
   - *The Tradeoff*: The scheduler sorts tasks in descending order of priority score rather than solving a 0/1 knapsack dynamic programming problem to mathematically maximize total minutes spent.
   - *Why it's reasonable*: In real pet care, completing an essential 35-minute park walk or medication is far more important than squeezing in three trivial 10-minute brushings simply to hit 100% budget utilization. A priority-first approach produces predictable, trustworthy routines that prioritize health over arbitrary time-packing.

2. **Exact Time Collision Detection vs. Continuous Interval Overlap Checking**:
   - *The Tradeoff*: The `detect_conflicts()` algorithm checks for exact start-time collisions (`t1.preferred_time == t2.preferred_time`) rather than blocking any overlapping time intervals based on duration.
   - *Why it's reasonable*:
     - *Simplicity & Performance*: Exact matching is simple to understand, runs in $O(N^2)$ without complex interval tree structures or third-party dependencies, and catches the primary user mistake (scheduling two pets for care at the identical minute, such as 08:00 AM).
     - *Owner Multi-Tasking Flexibility*: In reality, pet care tasks often overlap in parallel without issue (e.g., Biscuit eating breakfast while the owner administers Mochi's eye drops). Hard-blocking entire time spans would create false-positive conflicts and unnecessarily prevent owners from scheduling routines that they can easily manage concurrently.

---

## 3. AI Collaboration

**a. How you used AI**

- **Usage across stages**:
  - *Phase 1 (UML & System Modeling)*: Used AI to brainstorm domain boundaries, define class responsibilities (`Pet`, `Owner`, `Task`, `Schedule`, `Scheduler`), and draft Mermaid.js class diagrams.
  - *Phase 2 (Class Skeletons & Core Logic)*: Prompted AI to generate dataclasses, implement multi-pet retrieval via `Owner.get_all_tasks()`, and build greedy scheduling logic with transparent rationale.
  - *Phase 3 (Algorithmic Enhancements)*: Collaborated with AI to write `Scheduler.sort_by_time()` using lambda tuple keys, `Scheduler.filter_tasks()`, `datetime.timedelta` recurrence logic, and pairwise conflict detection.
  - *Phase 4 (Testing & Verification)*: Used AI to brainstorm edge cases (untimed tasks, reverse inputs, three-way collisions, attribute inheritance) and scaffold a 17-test `pytest` suite.
  - *Phase 5 (UI Integration & Polish)*: Paired with AI to connect backend methods to Streamlit components (`st.dataframe`, `st.warning`, filter selectboxes, and recurrence completion buttons).

- **Which AI coding assistant features were most effective?**
  - *Multi-file editing / replace tools*: Allowed seamless, simultaneous updates across `pawpal_system.py`, `app.py`, and `main.py` when introducing new attributes like `preferred_time` and `frequency`.
  - *Terminal command execution (`run_command`)*: Running `pytest` and `main.py` directly within the agent loop allowed instant verification of code changes, catching bugs (like Windows console character encoding) immediately.
  - *Targeted algorithmic brainstorming*: Asking AI for specific patterns (e.g., *"How to use a tuple lambda key in `sorted()` to put `None` values last without crashing"*) gave high-signal, idiomatic solutions much faster than generic searches.

- **Example of an AI suggestion rejected or modified**:
  - *Knapsack / Overlap Complexity*: During algorithmic planning, the AI initially suggested a complex interval-tree overlap algorithm and a 0/1 knapsack dynamic programming solver for schedule packing. I **rejected** this in favor of a simpler exact-time conflict warning and priority-greedy packing. The AI's proposal would have prevented multi-tasking (e.g., cat eating while dog is brushed) and sacrificed high-priority tasks to fill 100% of the minute budget with low-priority filler. Keeping it lightweight kept the code human-readable and aligned with real pet owner needs.
  - *Breaking Method Name Alias*: When the AI generated test stubs referencing `mark_complete()` while the original class had `mark_completed()`, instead of breaking existing code or doing an invasive refactor, I added an alias `mark_complete = mark_completed` so both interfaces work seamlessly.

- **How separate chat sessions helped stay organized**:
  - Dividing work into distinct phases (Phase 1: Architecture, Phase 2: Core Logic, Phase 3: Algorithms, Phase 4: Testing, Phase 5: UI) in clean contexts prevented context pollution. In the testing session, the AI wasn't distracted by Streamlit UI styling; in the algorithm session, it focused purely on algorithmic clarity and edge cases. This kept prompt tokens focused and prevented regression in already-completed modules.

- **Being the "Lead Architect" when collaborating with AI**:
  - AI is an extraordinarily fast implementer and brainstorming partner, but it lacks intrinsic domain common sense. As the lead architect, my job was to:
    1. Define the system boundaries and constraints upfront.
    2. Enforce separation of concerns (keeping UI out of dataclasses, keeping scheduling out of entity models).
    3. Push back on unnecessary complexity (over-engineered algorithms).
    4. Rigorously verify behavior through automated tests and interactive runs rather than trusting generated code blindly.

---

## 4. Testing and Verification

**a. What you tested**

- **Behaviors tested across 17 automated tests**:
  1. *Core Entity Behavior*: Task completion toggling and appending tasks to pet rosters.
  2. *Chronological Sorting*: Verifying `sort_by_time()` correctly sequences 24-hour time strings (`"07:15"` < `"08:00"` < `"14:00"`), handles already-sorted input idempotently, sorts reversed inputs accurately, and places untimed tasks (`preferred_time=None`) at the end.
  3. *Recurrence Logic*: Confirming daily tasks advance by +1 day and weekly tasks advance by +7 days via `timedelta`; verifying `as-needed` tasks do not spawn successors; and confirming all metadata (priority, duration, mandatory flag) is cloned properly into the successor.
  4. *Multi-Criteria Filtering*: Verifying filtering by pet name, by completion state, and combined criteria.
  5. *Conflict Detection*: Testing same-pet collisions, cross-pet collisions, conflict-free schedules, 3-way simultaneous collisions ($C(3,2) = 3$ pairwise warnings), and handling of task lists with zero timed tasks.

- **Why these tests were important**:
  - Schedulers fail silently; a bug in time calculation or sorting key doesn't crash the program, it just produces a subtly wrong schedule. Automated tests guaranteed that edge cases (like untimed tasks or three tasks sharing one minute) behave deterministically.

**b. Confidence**

- **Confidence Level**: **⭐⭐⭐⭐⭐ (5 / 5)**
  - All 17 unit tests pass with zero errors in 0.03s. The integration was verified through both the interactive Streamlit UI and the terminal `main.py` harness.
- **Edge cases to test next with more time**:
  1. *Month/Year Boundary Recurrence*: Testing recurrence math on leap days (February 29) and New Year's Eve (December 31 $\rightarrow$ January 1).
  2. *Invalid Time String Formats*: Passing malformed strings like `"8:00"` (single digit), `"25:00"`, or `"noon"` to test defensive parsing in `_advance_time()` and `sort_by_time()`.
  3. *Zero-Duration and Massive-Duration Tasks*: Handling 0-minute tasks or tasks exceeding 1440 minutes (24 hours).

---

## 5. Reflection

**a. What went well**

- **Clean Architecture & Separation of Concerns**: Isolating the data models (`Task`, `Pet`, `Owner`) from the outcome (`Schedule`) and the logic engine (`Scheduler`) made the code intuitive, easy to test, and effortless to integrate into both Streamlit and CLI interfaces.
- **Transparent Reasoning**: The scheduler doesn't just produce a timetable; it logs human-readable rationale explaining *why* each task was included or omitted, building user trust.
- **Test-Driven Reliability**: Developing a robust 17-test suite caught subtle edge cases early and gave total confidence during UI refactoring.

**b. What you would improve**

- **Duration-Aware Conflict Detection**: While exact-time detection is lightweight, an optional "duration overlap" view could flag when a 45-minute walk at 08:00 physically prevents an owner from doing a 15-minute grooming session scheduled at 08:30.
- **Persistent Storage**: Currently, the app relies on Streamlit's `session_state`. Adding SQLite or JSON file persistence would allow pet owners to save their profiles across browser sessions.
- **Multiple Caregivers**: Extending the model to support multiple owners/caregivers (e.g., two partners sharing dog-walking duties) would make PawPal+ even more practical for families.

**c. Key takeaway**

- The biggest lesson was learning to act as the **lead architect** rather than a passive recipient of AI output. AI generates code at tremendous speed, but maintaining architectural integrity requires human direction: setting clear contracts, questioning over-engineered suggestions, enforcing separation of concerns, and writing comprehensive tests to verify correctness.
