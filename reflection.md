# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

 My initial design uses a simple object-oriented structure with four core classes: Owner, Pet, Task, Scheduler; to separate data from logic. 
 - The Owner class has the attributes name and a list of pets. It uses the methods add_pet() to link a new pet to the user, and get_all_tasks() to aggregate every task across all owned pets.

 - The Pet class represents an individual animal, with attributes like name, species, and a list of its specific Task objects. It has the method add_task() to assign a new chore directly to that pet.

- The Task class tracks a single chore's attributes (description, time, frequency) and an is_complete boolean flag. It uses the method mark_complete() to update the task's status to finished.

-The Scheduler Class holds attribute Owner and methods get_today_schedule(), sort_by_time() to order the aggregated tasks chronologically, and check_conflicts() to scan the schedule and flag any tasks occurring at the exact same time.

- What classes did you include, and what responsibilities did you assign to each?

The Owner class holds a list of Pet objects, and each Pet manages its own list of Task chores. I built a separate Scheduler class to act as the logic engine; instead of storing data, it takes the Owner object, aggregates all pet tasks, sorts them by time, and flags any scheduling conflicts.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

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

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

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
