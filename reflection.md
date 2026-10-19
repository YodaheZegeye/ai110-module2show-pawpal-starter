# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

### Core User Actions
Based on the scenario described in `README.md`, PawPal+ enables the user to perform three core actions:

1. **Add and Manage Pet & Owner Information**: The user can input owner details and create pet profiles (including name, species, care preferences, and daily time constraints).
2. **Add and Customize Pet Care Tasks**: The user can define and organize care tasks (e.g., morning walks, feedings, medication schedules, and grooming) with associated details such as duration and priority level.
3. **Generate and View Today's Daily Plan**: The user can generate a personalized daily schedule based on constraints and task priorities, allowing them to view today's tasks and see the reasoning behind the planned order.

### Initial UML Architecture & Responsibilities
The initial UML design follows a separation of concerns by isolating data models (using Python dataclasses) from business logic (the scheduling engine):

- **`Pet`**: Holds pet profile data including name, species, energy level, and care preferences. Responsible for formatting pet summaries and tracking specific care needs.
- **`Owner`**: Represents the pet parent. Responsible for holding daily time availability constraints (in minutes) and managing one or more associated pets.
- **`Task`**: Represents an individual care activity (e.g., walking, feeding, administering medication). Responsible for storing duration, priority level, category, and mandatory status, and providing a numeric priority score for sorting.
- **`Schedule`**: Holds the final plan output for the day. Responsible for tracking scheduled tasks, unscheduled tasks, total duration, and step-by-step reasoning for the schedule.
- **`Scheduler`**: Acts as the central planning engine. Responsible for sorting tasks based on priority and constraints, evaluating if tasks fit within the owner's remaining time budget, assigning time slots, and generating transparent reasoning for why tasks were selected or omitted.

**b. Design changes**

- **Did your design change during implementation?**  
  Yes, the design evolved during the architectural review of the class skeleton in `pawpal_system.py`.

- **Key changes and rationale:**
  1. **Linked Tasks to Specific Pets (`Task.pet_name`)**:  
     *Why*: While `Owner` could hold multiple pets, `Task` initially lacked a direct reference to a pet. Adding `pet_name` ensures that tasks can be unambiguously associated with and filtered for individual pets in multi-pet households.
  2. **Added Time Budget Tracking to `Schedule` (`Schedule.available_time_minutes`)**:  
     *Why*: The initial `Schedule` only tracked `total_duration_minutes`. Adding `available_time_minutes` allows the scheduler to explain omitted tasks clearly (e.g., *"Excluded 'Park Visit' (40 min) because only 15 min remained of the 60 min budget"*).
  3. **Added Timeline Progression (`start_time: str = "08:00"`)**:  
     *Why*: The starter scenario in `README.md` requires displaying a chronological daily plan (e.g., `08:00 — Morning walk`). Supporting a base start time enables the scheduler to compute sequential start times for each scheduled task rather than just summing durations.
  4. **Multi-Pet Task Aggregation (`Owner.get_all_tasks()` & `Pet.tasks`)**:  
     *Why*: To cleanly satisfy multi-pet households, each `Pet` manages its own list of tasks, and `Owner` exposes `get_all_tasks()`. The `Scheduler` queries `owner.get_all_tasks()` directly, allowing seamless task organization and prioritization across multiple pets.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- **Usage across stages**:
  - *Brainstorming & UML Modeling*: Used AI to decompose the PawPal+ scenario into cohesive domain classes (`Pet`, `Owner`, `Task`, `Schedule`, `Scheduler`), draft Mermaid.js class diagrams, and map relationships.
  - *Skeleton Generation & Review*: Had AI create clean Python dataclass skeletons, followed by an architectural critique that identified the need for multi-pet task aggregation (`Owner.get_all_tasks()`), schedule budget tracking, and timeline calculation.
  - *Implementation & Testing*: Guided AI to implement scheduling logic with greedy duration packing and priority weighting, write terminal harnesses (`main.py`), and generate automated unit tests (`tests/test_pawpal.py`).
- **Most helpful prompts & techniques**:
  - Targeted structural questions like *"How should the Scheduler retrieve all tasks from the Owner's pets to support multi-pet scheduling?"*
  - Asking for readable, formatted terminal strings rather than dumping raw Python object dictionaries.

**b. Judgment and verification**

- **Moments of critical evaluation and adjustment**:
  - *Method Naming & API Compatibility*: When drafting unit tests, the prompt specified `mark_complete()` while the skeleton had `mark_completed()`. Rather than creating breaking changes, I ensured both methods were supported via an alias.
  - *Windows Terminal Encoding Resolution*: When `main.py` was first executed, the raw emoji (`🐾`) and em-dashes triggered a Windows `cp1252` `UnicodeEncodeError`. Instead of ignoring it or running only in bash, I adjusted the output formatting to use clean ASCII characters and added `sys.stdout.reconfigure(encoding="utf-8")` to guarantee cross-platform compatibility.
  - *Multi-Pet Grading Compliance*: Verified that `Scheduler.generate_plan()` delegates task retrieval to `Owner.get_all_tasks()` rather than scheduling single pets in isolation, preserving the multi-pet requirement.
- **Verification strategy**:
  - Verified logic execution visually using `python main.py` to confirm timeline slots, priority ordering, and budget deficit calculations.
  - Ran `python -m pytest` in `.venv` to systematically confirm unit tests passed with 100% success.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
