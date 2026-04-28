from datetime import datetime, date, timedelta
from pawpal_system import Owner, Task, Pet, Scheduler

def test_task_completion():
    """Verify that calling mark_complete() actually changes the task's status."""
    task = Task("Morning Walk", datetime.now(), "Daily", 30, 5)
    assert not task.is_complete()
    task.mark_complete()
    assert task.is_complete()

def test_task_addition():
    """Verify that adding a task to a Pet increases that pet's task count."""
    pet = Pet("Fido", "Dog")
    assert len(pet.get_tasks()) == 0
    new_task = Task("Morning Walk", datetime.now(), "Daily", 30, 5)
    pet.add_task(new_task)
    assert len(pet.get_tasks()) == 1

def test_scheduler_sorts_tasks_chronologically():
    """Sorting Correctness: Verify tasks are sorted by time correctly."""
    owner = Owner("Alex")
    scheduler = Scheduler(owner)
    pet = Pet("Fido", "Dog")
    owner.add_pet(pet)
    now = datetime.now()

    # Create tasks out of order
    t1 = Task("Lunch", now + timedelta(hours=2), "Once", 15, 2)
    t2 = Task("Breakfast", now, "Once", 30, 3)
    t3 = Task("Dinner", now + timedelta(hours=4), "Once", 45, 1)

    pet.add_task(t1)
    pet.add_task(t2)
    pet.add_task(t3)

    # Use your custom sorting method
    sorted_tasks = scheduler.sort_by_time_and_priority(owner.get_all_tasks())

    # Breakfast should be sorted to the very front
    assert sorted_tasks[0].description() == "Breakfast"
    assert sorted_tasks[-1].description() == "Dinner"

def test_daily_task_recurrence_creates_next_day_task():
    """Recurrence Logic: marking a daily task complete should create a new task for the following day."""
    owner = Owner("Alex")
    scheduler = Scheduler(owner)
    pet = Pet("Fido", "Dog")
    owner.add_pet(pet)
    
    start_time = datetime(2024, 1, 1, 8, 0)
    daily_task = Task("Daily Walk", start_time, "Daily", 30, 5)
    pet.add_task(daily_task)

    # Use your system's mark_task_complete method
    new_task = scheduler.mark_task_complete(daily_task)

    # Original task should be complete
    assert daily_task.is_complete()

    # A new task should exist for the next day, same time
    assert new_task is not None
    assert new_task.time() == start_time + timedelta(days=1)
    
    # Verify the new task was actually attached to the pet
    assert new_task in pet.get_tasks()

def test_scheduler_detects_conflicting_tasks():
    """Conflict Detection: Verify that the Scheduler flags overlapping times."""
    owner = Owner("Alex")
    scheduler = Scheduler(owner)
    pet = Pet("Fido", "Dog")
    owner.add_pet(pet)
    
    start_time = datetime(2024, 1, 1, 9, 0)

    # Task 1 starts at 9:00 and lasts 30 mins (ends 9:30)
    task1 = Task("Morning Walk", start_time, "Once", 30, 3)
    
    # Task 2 starts at 9:15, which overlaps with Task 1!
    task2 = Task("Vet Visit", start_time + timedelta(minutes=15), "Once", 60, 5)

    pet.add_task(task1)
    pet.add_task(task2)

    # Pass the tasks to your conflict checker
    conflicts = scheduler.check_conflicts(owner.get_all_tasks())

    # It should flag both tasks as being in conflict
    assert len(conflicts) == 2
    assert task1 in conflicts
    assert task2 in conflicts

def test_sorting_priority_tiebreaker():
    """Sorting Correctness: Verify tasks at the same time are sorted by priority."""
    owner = Owner("Alex")
    scheduler = Scheduler(owner)
    
    same_time = datetime(2024, 1, 1, 12, 0)
    
    # Create tasks at the EXACT same time, but different priorities
    t1 = Task("Low Priority Task", same_time, "Once", 30, 1)
    t2 = Task("High Priority Task", same_time, "Once", 30, 5)
    t3 = Task("Medium Priority Task", same_time, "Once", 30, 3)

    # Scramble the input list
    tasks = [t1, t2, t3]
    
    # Sort them
    sorted_tasks = scheduler.sort_by_time_and_priority(tasks)

    # High priority should win the tie-breaker and be first
    assert sorted_tasks[0].description() == "High Priority Task"
    assert sorted_tasks[1].description() == "Medium Priority Task"
    assert sorted_tasks[2].description() == "Low Priority Task"

def test_time_budget_greedy_allocation():
    """Time Budget: Verify the scheduler stops adding tasks when the budget runs out."""
    owner = Owner("Alex")
    scheduler = Scheduler(owner)
    pet = Pet("Fido", "Dog")
    owner.add_pet(pet)
    
    target_date = date(2024, 1, 1)
    
    # 3 tasks totaling 105 minutes
    t1 = Task("Task 1", datetime.combine(target_date, datetime.min.time()).replace(hour=8), "Once", 30, 5)
    t2 = Task("Task 2", datetime.combine(target_date, datetime.min.time()).replace(hour=9), "Once", 45, 5)
    t3 = Task("Task 3", datetime.combine(target_date, datetime.min.time()).replace(hour=10), "Once", 30, 5)
    
    pet.add_task(t1)
    pet.add_task(t2)
    pet.add_task(t3)

    # Give a budget of only 60 minutes. 
    # It should take Task 1 (30m), leaving 30m. 
    # It tries to take Task 2 (45m), but it doesn't fit, so the greedy algorithm breaks.
    schedule = scheduler.get_today_schedule(target_date, available_minutes=60)

    assert len(schedule) == 1
    assert schedule[0].description() == "Task 1"

def test_filter_tasks_by_pet_name():
    """Filtering: Verify that the scheduler correctly isolates tasks for a specific pet."""
    owner = Owner("Alex")
    scheduler = Scheduler(owner)
    
    fido = Pet("Fido", "Dog")
    whiskers = Pet("Whiskers", "Cat")
    owner.add_pet(fido)
    owner.add_pet(whiskers)

    fido.add_task(Task("Fido Walk", datetime.now(), "Once", 30, 5))
    whiskers.add_task(Task("Whiskers Brush", datetime.now(), "Once", 15, 3))
    whiskers.add_task(Task("Whiskers Play", datetime.now(), "Once", 20, 4))

    all_tasks = owner.get_all_tasks()
    
    # Filter for Whiskers only
    whiskers_tasks = scheduler.filter_tasks(all_tasks, pet_name="Whiskers")

    assert len(whiskers_tasks) == 2
    assert all("Whiskers" in task.description() for task in whiskers_tasks)