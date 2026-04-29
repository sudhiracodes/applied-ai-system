# PawPal+ AI Agent

### Original Project Context
This project is an evolution of my Module 1-3 project, **PawPal+**. The original PawPal+ was an intelligent pet care scheduling application featuring a deterministic Python backend capable of time-based sorting, priority management, and scheduling conflict detection. 

### Title and Summary
**PawPal+ AI Agentic Workflow**
This system upgrades the original PawPal+ pet care scheduler with an AI-driven Agentic Workflow. Instead of manually filling out rigid task forms, users can describe their pet's day in messy, natural language. The AI acts as an intelligent parser that extracts the user's intent, formats it into strict JSON, and passes it to the backend. This matters because it bridges the gap between natural human communication and strict, type-safe backend microservices.

### Architecture Overview
*(See `assets/architecture.png` for the system diagram)*
The system utilizes a wrapper architecture:
1. **Input:** The user types a natural language request in the Streamlit UI.
2. **Agentic Processing:** The Gemini 2.5 Flash LLM acts as the agent, parsing the text and extracting a strict JSON schema that perfectly matches the Python `Task` dataclass.
3. **Evaluation/Guardrails:** The parsed Python object is fed directly into the existing `Scheduler.check_conflicts()` method.
4. **Output:** The system evaluates the rule set. It either successfully schedules the task, or rejects it with a conflict warning, keeping the human in the loop to review the AI's decision.

![Architecture](/assets/architecture.png)

### Setup Instructions
1. Clone this repository to your local machine: `git clone <your-repo-url>`
2. Navigate into the directory: `cd applied-ai-system-final`
3. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Sample Interactions

**Scenario 1: Successful Scheduling**
* **User Input:** *"Schedule a high priority 45-min walk for Leo at 5 PM."*
* **AI Output:** Successfully parses to `{"pet_name": "Leo", "task_desc": "walk", "start_time": "17:00", "duration": 45, "priority": 5, "frequency": "Once"}`. The backend validates it and adds it to the UI.

![Scenario 1](/assets/scene1.png)

**Scenario 2: Conflict Detection (Guardrail Triggered)**
* **User Input:** *"Book a vet visit for Leo at 5 PM."* (Assuming the walk from Scenario 1 is already scheduled).
* **AI Output:** The AI parses the JSON, but the Python backend catches the overlapping time. The UI displays: *"⚠️ AI caught a conflict! 'vet visit' overlaps with an existing task. Please adjust the time."*

![Scenario 2](/assets/scene2.png)

### Design Decisions

I chose to implement an **Agentic Workflow** acting as a parser layer above my existing deterministic logic. A major trade-off here was relying on the LLM's speed and natural language capabilities over absolute predictability. To mitigate the risk of the LLM hallucinating bad data, I hard-coded the system prompt to demand pure JSON, and wrapped the output in the original Python conflict-detection guardrails. This ensures the AI's outputs are safely validated by hard code before ever reaching the database or schedule.

### Testing Summary

The system's reliability was tested using two methods:

1. **Automated Unit Tests:** The core backend sorting, priority, and conflict logic is verified by an existing Pytest suite.
2. **Error Handling & Guardrails:** I tested the AI integration by feeding it conflicting schedule times and malformed text. The Python `try/except` blocks successfully caught LLM formatting errors, and the hard-coded `check_conflicts` logic successfully prevented the AI from double-booking time slots.

### Testing and Reliability Summary
The system's reliability is validated using automated tests, error logging, and AI confidence scoring. 

**Summary:** 8 out of 8 backend unit tests passed. During human evaluation, the AI parsed valid inputs with an average confidence score of 0.95. The AI's confidence dropped to 0.6 when implicit contexts (like missing durations) were provided. Overall accuracy and system stability improved to 100% after wrapping the LLM parser in strict JSON guardrails and passing the output through the backend `check_conflicts` logic to intercept hallucinations.

To run the file and just see a quick summary:
```bash
pytest test_pawpal.py
```

### Stretch Feature: Agentic Workflow Enhancement (+2 Points)
**Observable Intermediate Steps:** To enhance the agentic workflow, the AI is explicitly prompted to generate a `planning_steps` chain before finalizing the task data. This multi-step reasoning forces the LLM to explain how it deduced the target pet, calculated the time, and inferred the priority level. This decision-making chain is fully observable to the user via a dropdown expander in the UI prior to the success confirmation.
**Tradeoffs & Future Work:** Implementing this observable reasoning chain introduces a minimal latency delay during task generation, as the LLM must generate more tokens before finalizing the JSON. Future iterations will focus on optimizing this prompt for speed, as well as integrating a voice-to-text transcription feature to allow for true hands-free scheduling.

### Reflection

This project taught me that while AI is incredibly powerful at deciphering human intent, it requires strict architectural boundaries. Letting an LLM output directly to a database or user interface is risky; however, using an LLM to parse intent and then handing that data off to traditional, strongly-typed Python logic creates a robust, professional-grade application.

### Portfolio Artifact & Reflection
**GitHub Repository:** https://github.com/sudhiracodes/applied-ai-system

**Loom Walkthrough:**  https://www.loom.com/share/2449d20d191b4bd18f5ca6ea54354850

**What this project says about me as an AI Engineer:**
Building the PawPal+ AI Agentic Workflow demonstrates my core approach as AI engineer,  generative AI should enhance a system's user experience without compromising its structural integrity. By designing an architecture where a Gemini LLM acts as an intelligent intent-parser that feeds into strongly-typed Python microservices, we were able to build applications that balance the fluid flexibility of modern AI with the strict reliability, guardrails, and automated testing required in production software.