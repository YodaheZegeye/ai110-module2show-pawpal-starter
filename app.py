import streamlit as st
from pawpal_system import Owner, Pet, Task, Schedule, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("🐾 PawPal+ Pet Care Planner")

# Shared Scheduler instance for sorting, filtering, and conflict detection
scheduler = Scheduler()

# --- 1. Session State Initialization ("App Memory") ---
if "owner" not in st.session_state:
    default_owner = Owner(name="Yodahe", available_time_minutes=75)

    # Pre-populate with starter pets so the app is immediately testable
    biscuit = Pet(
        name="Biscuit",
        species="dog",
        energy_level="high",
        preferences=["Morning outdoor walk", "Loves fetch"]
    )
    biscuit.add_task(Task(title="Morning park walk", duration_minutes=35, priority="high", category="walk", preferred_time="08:00", frequency="daily"))
    biscuit.add_task(Task(title="Brush coat & check paws", duration_minutes=20, priority="low", category="grooming", preferred_time="14:00", frequency="weekly"))

    mochi = Pet(
        name="Mochi",
        species="cat",
        energy_level="low",
        preferences=["Quiet feeding spot"]
    )
    mochi.add_task(Task(title="Administer allergy medication", duration_minutes=10, priority="high", category="medication", is_mandatory=True, preferred_time="08:00", frequency="daily"))
    mochi.add_task(Task(title="Interactive laser & feather play", duration_minutes=20, priority="medium", category="enrichment", preferred_time="15:30"))

    default_owner.add_pet(biscuit)
    default_owner.add_pet(mochi)
    st.session_state.owner = default_owner

if "schedule" not in st.session_state:
    st.session_state.schedule = None

owner = st.session_state.owner

# --- 2. Owner & Budget Configuration ---
with st.sidebar:
    st.header("👤 Owner Profile & Constraints")
    owner_name = st.text_input("Owner Name", value=owner.name)
    owner.name = owner_name

    available_time = st.number_input(
        "Daily Care Time Budget (minutes)",
        min_value=5,
        max_value=600,
        value=owner.get_available_time(),
        step=5,
        help="Maximum minutes you have available for pet care today."
    )
    owner.set_available_time(available_time)

    st.metric("Today's Time Budget", f"{owner.get_available_time()} min")
    st.caption("Tasks exceeding this budget will be highlighted and explained by the Scheduler.")

col_left, col_right = st.columns([1, 1])

# --- 3. Pet Management Section ---
with col_left:
    st.subheader("🐶 Manage Pets")

    # Display registered pets
    if owner.pets:
        for p in owner.pets:
            st.info(f"**{p.name}** ({p.species.capitalize()}, {p.energy_level} energy) — *{len(p.tasks)} tasks assigned*")
    else:
        st.warning("No pets registered yet. Add one below!")

    # Add Pet Form
    with st.expander("➕ Add a New Pet", expanded=False):
        with st.form("add_pet_form"):
            new_pet_name = st.text_input("Pet Name", placeholder="e.g., Luna")
            new_species = st.selectbox("Species", ["dog", "cat", "bird", "rabbit", "other"])
            new_energy = st.selectbox("Energy Level", ["high", "medium", "low"], index=1)
            new_pref = st.text_input("Care Preferences (comma-separated)", placeholder="e.g., likes quiet walks, allergic to chicken")
            submit_pet = st.form_submit_button("Add Pet to Owner")

            if submit_pet:
                if new_pet_name.strip():
                    prefs = [p.strip() for p in new_pref.split(",") if p.strip()]
                    new_pet = Pet(
                        name=new_pet_name.strip(),
                        species=new_species,
                        energy_level=new_energy,
                        preferences=prefs
                    )
                    # Class method call to connect UI data to backend
                    owner.add_pet(new_pet)
                    st.success(f"Added {new_pet.name} to {owner.name}'s profile!")
                    st.rerun()
                else:
                    st.error("Pet name cannot be blank.")

# --- 4. Task Management Section ---
with col_right:
    st.subheader("📋 Add Pet Care Tasks")

    if not owner.pets:
        st.info("Add a pet first before adding tasks.")
    else:
        pet_options = [p.name for p in owner.pets]
        with st.form("add_task_form"):
            target_pet_name = st.selectbox("Assign to Pet", pet_options)
            task_title = st.text_input("Task Title", placeholder="e.g., Evening medication")

            c1, c2 = st.columns(2)
            with c1:
                duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20, step=5)
                priority = st.selectbox("Priority", ["high", "medium", "low"], index=1)
                preferred_time = st.text_input(
                    "Preferred Time (HH:MM)",
                    placeholder="e.g., 08:00",
                    help="24-hour format. Leave blank for flexible scheduling."
                )
            with c2:
                category = st.selectbox("Category", ["walk", "feeding", "medication", "grooming", "enrichment", "other"])
                is_mandatory = st.checkbox("Mandatory (non-negotiable)", value=False)
                frequency = st.selectbox("Frequency", ["daily", "weekly", "as-needed"], index=0)

            submit_task = st.form_submit_button("Add Task")

            if submit_task:
                if task_title.strip():
                    clean_time = preferred_time.strip() if preferred_time.strip() else None
                    new_task = Task(
                        title=task_title.strip(),
                        duration_minutes=int(duration),
                        priority=priority,
                        category=category,
                        is_mandatory=is_mandatory,
                        preferred_time=clean_time,
                        frequency=frequency,
                    )
                    # Locate the pet and call Pet.add_task()
                    target_pet = next(p for p in owner.pets if p.name == target_pet_name)
                    target_pet.add_task(new_task)
                    st.success(f"Added task '{new_task.title}' for {target_pet.name}!")
                    st.rerun()
                else:
                    st.error("Task title cannot be blank.")

# --- 5. Current Tasks — Sorted & Filtered ---
st.divider()
st.subheader("📝 All Current Tasks Across Pets")

all_tasks = owner.get_all_tasks()

if all_tasks:
    # --- Conflict Detection Banner (always visible) ---
    conflict_warnings = scheduler.detect_conflicts(all_tasks)
    if conflict_warnings:
        st.markdown("#### ⚠️ Scheduling Conflicts Detected")
        for warn in conflict_warnings:
            st.warning(warn, icon="⚠️")

    # --- Filter Controls ---
    filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 2])
    with filter_col1:
        pet_names = ["All Pets"] + [p.name for p in owner.pets]
        selected_pet = st.selectbox("Filter by Pet", pet_names, key="filter_pet")
    with filter_col2:
        status_options = ["All", "Pending Only", "Completed Only"]
        selected_status = st.selectbox("Filter by Status", status_options, key="filter_status")

    # Apply Scheduler.filter_tasks()
    pet_filter = None if selected_pet == "All Pets" else selected_pet
    status_filter = None
    if selected_status == "Pending Only":
        status_filter = False
    elif selected_status == "Completed Only":
        status_filter = True

    filtered_tasks = scheduler.filter_tasks(all_tasks, completed=status_filter, pet_name=pet_filter)

    # Apply Scheduler.sort_by_time() for chronological display
    sorted_tasks = scheduler.sort_by_time(filtered_tasks)

    with filter_col3:
        st.caption(f"Showing **{len(sorted_tasks)}** of {len(all_tasks)} tasks — sorted chronologically by `sort_by_time()`")

    # Build the display table from sorted/filtered results
    if sorted_tasks:
        table_data = []
        for t in sorted_tasks:
            status_icon = "✅" if t.completed else "⏳"
            priority_badge = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}.get(t.priority, t.priority)
            table_data.append({
                "Time": t.preferred_time or "Flexible",
                "Task": t.title,
                "Pet": t.pet_name or "Unassigned",
                "Duration": f"{t.duration_minutes} min",
                "Priority": priority_badge,
                "Frequency": t.frequency.capitalize() if t.frequency else "—",
                "Mandatory": "Yes" if t.is_mandatory else "No",
                "Status": status_icon,
            })
        st.dataframe(table_data, use_container_width=True, hide_index=True)
    else:
        st.info("No tasks match the current filter criteria.")

    # --- Mark Complete Buttons with Recurrence ---
    st.markdown("#### ✔️ Mark Tasks Complete")
    st.caption("Completing a recurring task automatically creates the next occurrence via `timedelta`.")

    pending_tasks = scheduler.filter_tasks(all_tasks, completed=False)
    if pending_tasks:
        for i, task in enumerate(pending_tasks):
            col_btn, col_desc = st.columns([1, 4])
            with col_btn:
                if st.button(f"Complete", key=f"complete_{i}_{task.title}", use_container_width=True):
                    next_task = owner.mark_task_complete(task)
                    if next_task:
                        st.session_state[f"recurrence_msg_{i}"] = (
                            f"✅ Completed **'{task.title}'** ({task.frequency}). "
                            f"Next occurrence auto-created for **{next_task.due_date}**."
                        )
                    else:
                        st.session_state[f"recurrence_msg_{i}"] = (
                            f"✅ Completed **'{task.title}'** (no recurrence — {task.frequency})."
                        )
                    st.rerun()
            with col_desc:
                time_label = f"[{task.preferred_time}]" if task.preferred_time else "[Flexible]"
                freq_label = f" · {task.frequency.capitalize()}" if task.frequency else ""
                st.markdown(f"{time_label} **{task.title}** — *{task.pet_name}* ({task.duration_minutes} min){freq_label}")

            # Show recurrence feedback if it was just completed
            if f"recurrence_msg_{i}" in st.session_state:
                st.success(st.session_state.pop(f"recurrence_msg_{i}"))
    else:
        st.success("🎉 All tasks are complete! No pending items.")
else:
    st.info("No tasks recorded yet.")

# --- 6. Schedule Generation & Results ---
st.divider()
st.subheader("📅 Generate Daily Care Schedule")
st.caption("The Scheduler retrieves all tasks from Owner.get_all_tasks(), evaluates priorities, and fits them into today's time budget.")

sched_col1, sched_col2 = st.columns([1, 3])
with sched_col1:
    start_time_input = st.text_input("Start Time", value="08:00")
    if st.button("⚡ Generate Schedule", type="primary", use_container_width=True):
        # Backend connection: Scheduler reads directly from Owner
        st.session_state.schedule = scheduler.generate_plan(
            owner=owner,
            start_time=start_time_input
        )
        st.success("Daily plan generated!")

with sched_col2:
    current_schedule = st.session_state.schedule
    if current_schedule is not None:
        # Display key metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Budget", f"{current_schedule.available_time_minutes} min")
        m2.metric("Scheduled", f"{current_schedule.total_duration_minutes} min")
        m3.metric("Remaining", f"{current_schedule.remaining_time_minutes} min")
        m4.metric("Tasks (Fit / Omitted)", f"{len(current_schedule.scheduled_tasks)} / {len(current_schedule.unscheduled_tasks)}")

        # Display Scheduled Timeline
        st.markdown("#### ✅ Today's Scheduled Timeline")
        if current_schedule.scheduled_tasks:
            for item in current_schedule.scheduled_tasks:
                badge = "🔴 High" if item["priority"] == "high" else ("🟡 Medium" if item["priority"] == "medium" else "🟢 Low")
                st.markdown(
                    f"**`{item['time_slot']}`** — **{item['title']}** ({item['duration_minutes']} min) · *Pet: {item['pet_name']}* · Priority: {badge}"
                )
        else:
            st.warning("No tasks could be scheduled within the time budget.")

        # Display Omitted Tasks if any
        if current_schedule.unscheduled_tasks:
            st.markdown("#### ⚠️ Omitted Tasks (Exceeded Budget)")
            for item in current_schedule.unscheduled_tasks:
                st.error(
                    f"**{item['title']}** ({item['duration_minutes']} min) for *{item['pet_name']}* — {item['reason']}"
                )

        # Display Time Conflicts & Warnings from the generated schedule
        if current_schedule.conflicts:
            st.markdown("#### ⚠️ Time Conflicts in Generated Plan")
            for c in current_schedule.conflicts:
                st.warning(c, icon="⚠️")

        # Display Reasoning Breakdown
        with st.expander("🧠 Scheduler Decision Rationale"):
            for r in current_schedule.reasoning:
                st.markdown(f"- {r}")

        with st.expander("📋 Raw Text Schedule Output"):
            st.code(current_schedule.get_formatted_plan(), language="text")
