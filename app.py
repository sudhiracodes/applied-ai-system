import streamlit as st
from datetime import datetime, date
import pandas as pd
from pawpal_system import Owner, Pet, Task, Scheduler
import json
import google.generativeai as genai

# --- 1. Session State Initialization ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner("PawPal User")

owner = st.session_state.owner
scheduler = Scheduler(owner)

# --- 2. App Header ---
st.title("🐾 PawPal+ Smart Scheduler")
st.write("Plan your pet care tasks with priority and time constraints.")

# --- 3. Sidebar: Add Pets ---
with st.sidebar:
    st.header("1. Add a Pet")
    with st.form("add_pet_form"):
        pet_name = st.text_input("Pet Name")
        pet_species = st.text_input("Species (Dog, Cat, etc.)")
        submit_pet = st.form_submit_button("Add Pet")
        
        if submit_pet and pet_name:
            new_pet = Pet(pet_name, pet_species)
            owner.add_pet(new_pet)
            st.success(f"{pet_name} added!")
    st.divider()
    st.header("🔑 AI Setup")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)

# --- 4. Main Body: Add Tasks ---
st.header("2. Schedule a Task")
# --- AI AGENTIC WORKFLOW ---
st.subheader("🤖 AI Assistant")
ai_prompt = st.text_area("Describe the task (e.g., 'Schedule a high priority 30-min walk for Leo at 5 PM')")

if st.button("Generate Task with AI"):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar first!")
    elif not owner.pets():
        st.error("Please add a pet in the sidebar first!")
    else:
        pet_names = [pet.name() for pet in owner.pets()]
        try:
            # 1. Setup the LLM
            model = genai.GenerativeModel('gemini-2.5-flash')
            
        #    # 2. System Prompt to enforce JSON schema matching your dataclass
        #     system_instruction = f"""
        #     You are a pet scheduling assistant. Extract the task details from the user's prompt.
        #     The user owns these pets: {pet_names}. You MUST assign the task to one of these pets.
        #     Output ONLY raw JSON, no markdown, no code blocks.
        #     Format exactly like this:
        #     {{
        #         "pet_name": "string",
        #         "task_desc": "string",
        #         "start_time": "HH:MM",
        #         "duration": int (minutes),
        #         "priority": int (1-5),
        #         "frequency": "Once" | "Daily" | "Weekly",
        #         "confidence_score": float (0.0 to 1.0 indicating how clear the user's prompt was)
        #     }}
        #     """
           # 2. System Prompt to enforce JSON schema matching your dataclass
            system_instruction = f"""
            You are a pet scheduling assistant. Extract the task details from the user's prompt.
            The user owns these pets: {pet_names}. You MUST assign the task to one of these pets.
            Output ONLY raw JSON, no markdown, no code blocks.
            Format exactly like this:
            {{
                "planning_steps": "List step-by-step how you decided on the pet, time, and priority based on the prompt.",
                "pet_name": "string",
                "task_desc": "string",
                "start_time": "HH:MM",
                "duration": int (minutes),
                "priority": int (1-5),
                "frequency": "Once" | "Daily" | "Weekly",
                "confidence_score": float (0.0 to 1.0)
            }}
            """
            
            # 3. Call the Agent
            response = model.generate_content(system_instruction + "\nUser Prompt: " + ai_prompt)
            
            # Clean up the response in case the LLM adds markdown backticks
            cleaned_response = response.text.replace('```json', '').replace('```', '').strip()
            task_data = json.loads(cleaned_response)
            
            # 4. Parse the data into your existing structures
            from datetime import time # Ensure this is imported at the top of your file
            hour, minute = map(int, task_data["start_time"].split(':'))
            ai_time = time(hour, minute)
            full_datetime = datetime.combine(date.today(), ai_time)
            
            # 5. Create the Task object
            ai_task = Task(
                task_data["task_desc"], 
                full_datetime, 
                task_data["frequency"], 
                task_data["duration"], 
                task_data["priority"]
            )
            
            # 6. Guardrail: Conflict Detection before saving
            selected_pet = next(p for p in owner.pets() if p.name().lower() == task_data["pet_name"].lower())
            
            # Temporarily add to check conflicts
            temp_schedule = scheduler.get_today_schedule(date.today()) + [ai_task]
            conflicts = scheduler.check_conflicts(temp_schedule)
            
            if conflicts:
                st.warning(f"⚠️ AI caught a conflict! '{ai_task.description()}' overlaps with an existing task. Please adjust the time.")
            else:
                selected_pet.add_task(ai_task)
                confidence_pct = int(task_data.get("confidence_score", 1.0) * 100)
                # --- NEW: Observable Intermediate Steps ---
                with st.expander("🧠 View AI Decision-Making Chain"):
                    st.write(task_data.get("planning_steps", "No planning steps provided."))
                st.success(f"✅ AI successfully scheduled: {ai_task.description()} for {selected_pet.name()} at {task_data['start_time']}!(AI Confidence: {confidence_pct}%)")
                
        except Exception as e:
            st.error(f"The AI encountered an error processing that request. Try rephrasing. (Error: {e})")

st.divider()
st.subheader("Or add manually:")

if not owner.pets():
    st.info("👈 Please add a pet in the sidebar first!")
else:
    pet_names = [pet.name() for pet in owner.pets()]
    with st.form("add_task_form"):
        selected_pet_name = st.selectbox("Select Pet", pet_names)
        task_desc = st.text_input("Task Description")
        
        col1, col2 = st.columns(2)
        with col1:
            task_time = st.time_input("Start Time")
            task_freq = st.selectbox("Frequency", ["Once", "Daily", "Weekly"])
        with col2:
            task_duration = st.number_input("Duration (minutes)", min_value=1, value=15)
            task_priority = st.slider("Priority (1-5, 5 is highest)", 1, 5, 3)
            
        submit_task = st.form_submit_button("Add Task")
        
        if submit_task and task_desc:
            # Convert Streamlit time to a full datetime object for today
            full_datetime = datetime.combine(date.today(), task_time)
            
            # Find the correct pet and add the task
            selected_pet = next(p for p in owner.pets() if p.name() == selected_pet_name)
            new_task = Task(task_desc, full_datetime, task_freq, task_duration, task_priority)
            selected_pet.add_task(new_task)
            st.success("Task scheduled!")

# --- 5. Display Schedule with Time Budget ---
st.header("3. Today's Plan")

budget_toggle = st.checkbox("Enable Time Budget?")
budget_mins = None
if budget_toggle:
    budget_mins = st.number_input("How many minutes do you have today?", min_value=10, value=60)

# Optional filter by pet
pet_filter_options = ["All Pets"] + [pet.name() for pet in owner.pets()]
selected_filter = st.selectbox("Filter by pet", pet_filter_options)


# Run Algorithms
today = date.today()

if selected_filter == "All Pets":
    base_tasks = owner.get_all_tasks()
else:
    selected_pet = next(p for p in owner.pets() if p.name() == selected_filter)
    base_tasks = selected_pet.get_tasks()

# Use Scheduler to build today's schedule (already sorted by time/priority)
scheduled_tasks = scheduler.get_today_schedule(today, budget_mins, tasks=base_tasks)

# You can optionally re-apply sorting here to be explicit:
scheduled_tasks = scheduler.sort_by_time_and_priority(scheduled_tasks)

# Check for conflicts among the scheduled tasks
conflicts = scheduler.check_conflicts(scheduled_tasks)

# Present conflict warnings in a helpful, detailed way
if conflicts:
    st.warning(
        "Some tasks have overlapping times. Please review the conflicts below.",
        icon="⚠️",
    )

    # Build a small table that shows conflicting tasks clearly
    conflict_rows = []
    for t in conflicts:
        # Try to infer pet name (for All Pets view) by searching owner's pets
        pet_name = None
        for p in owner.pets():
            if t in p.get_tasks():
                pet_name = p.name()
                break

        conflict_rows.append(
            {
                "Pet": pet_name or "Unknown",
                "Task": t.description(),
                "Start": t.time().strftime("%Y-%m-%d %H:%M"),
                "End": t.end_time().strftime("%Y-%m-%d %H:%M"),
                "Priority": t.priority(),
            }
        )

    st.table(pd.DataFrame(conflict_rows))

# Show a success/info panel for the main schedule
if not scheduled_tasks:
    st.info("No tasks scheduled for today with the current filters and time budget.")
else:
    st.success("Here is your scheduled plan for today:")

    rows = []
    for t in scheduled_tasks:
        # Try to show pet name for context
        pet_name = None
        for p in owner.pets():
            if t in p.get_tasks():
                pet_name = p.name()
                break

        rows.append(
            {
                "Pet": pet_name or "Unknown",
                "Task": t.description(),
                "Start": t.time().strftime("%Y-%m-%d %H:%M"),
                "End": t.end_time().strftime("%Y-%m-%d %H:%M"),
                "Duration (min)": t.duration_minutes(),
                "Priority": t.priority(),
                "Completed": "✅" if t.is_complete() else "",
            }
        )

    st.table(pd.DataFrame(rows))