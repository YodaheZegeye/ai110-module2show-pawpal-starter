import streamlit as st
from pawpal_system import Owner, Pet, Task, Schedule, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("🐾 PawPal+ Pet Care Planner")

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
    biscuit.add_task(Task(title="Morning park walk", duration_minutes=35, priority="high", category="walk"))
    biscuit.add_task(Task(title="Brush coat & check paws", duration_minutes=20, priority="low", category="grooming"))

    mochi = Pet(
        name="Mochi",
        species="cat",
        energy_level="low",
        preferences=["Quiet feeding spot"]
    )
    mochi.add_task(Task(title="Administer allergy medication", duration_minutes=10, priority="high", category="medication", is_mandatory=True))
    mochi.add_task(Task(title="Interactive laser & feather play", duration_minutes=20, priority="medium", category="enrichment"))

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
            with c2:
                category = st.selectbox("Category", ["walk", "feeding", "medication", "grooming", "enrichment", "other"])
                is_mandatory = st.checkbox("Mandatory (non-negotiable)", value=False)
            
            submit_task = st.form_submit_button("Add Task")

            if submit_task:
                if task_title.strip():
                    new_task = Task(
                        title=task_title.strip(),
                        duration_minutes=int(duration),
                        priority=priority,
                        category=category,
                        is_mandatory=is_mandatory
                    )
                    # Locate the pet and call Pet.add_task()
                    target_pet = next(p for p in owner.pets if p.name == target_pet_name)
                    target_pet.add_task(new_task)
                    st.success(f"Added task '{new_task.title}' for {target_pet.name}!")
                    st.rerun()
                else:
                    st.error("Task title cannot be blank.")

# --- 5. Current Tasks Table ---
st.divider()
st.subheader("📝 All Current Tasks Across Pets")
all_tasks = owner.get_all_tasks()

if all_tasks:
    tasks_data = [t.to_dict() for t in all_tasks]
    st.dataframe(tasks_data, use_container_width=True)
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
        scheduler = Scheduler()
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

        # Display Time Conflicts & Warnings if any
        if current_schedule.conflicts:
            st.markdown("#### ⚠️ Time Conflicts Detected")
            for c in current_schedule.conflicts:
                st.warning(c)

        # Display Reasoning Breakdown
        with st.expander("🧠 Scheduler Decision Rationale"):
            for r in current_schedule.reasoning:
                st.markdown(f"- {r}")

        with st.expander("📋 Raw Text Schedule Output"):
            st.code(current_schedule.get_formatted_plan(), language="text")

