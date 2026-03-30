from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import List, Optional


@dataclass
class Task:
    _description: str
    _time: datetime
    _frequency: str
    _duration_minutes: int
    _priority: int  # higher = more important
    _is_complete: bool = False

    def mark_complete(self) -> None:
        self._is_complete = True

    def description(self) -> str:
        return self._description

    def time(self) -> datetime:
        return self._time

    def frequency(self) -> str:
        return self._frequency

    def duration_minutes(self) -> int:
        return self._duration_minutes

    def priority(self) -> int:
        return self._priority

    def is_complete(self) -> bool:
        return self._is_complete

    def end_time(self) -> datetime:
        """Compute end time using duration."""
        return self._time + timedelta(minutes=self._duration_minutes)


@dataclass
class Pet:
    _name: str
    _species: str
    _tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self._tasks.append(task)

    def get_tasks(self) -> List[Task]:
        return list(self._tasks)

    def name(self) -> str:
        return self._name

    def species(self) -> str:
        return self._species


@dataclass
class Owner:
    _name: str
    _pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self._pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        tasks: List[Task] = []
        for pet in self._pets:
            tasks.extend(pet.get_tasks())
        return tasks

    def name(self) -> str:
        return self._name

    def pets(self) -> List[Pet]:
        return list(self._pets)


@dataclass
class Scheduler:
    _owner: Owner

    def get_today_schedule(
        self,
        target_date: date,
        available_minutes: Optional[int] = None,
    ) -> List[Task]:
        """
        Return tasks for target_date.
        - Filters by calendar date.
        - Sorts by time, then priority (higher first).
        - If available_minutes is given, only includes tasks
          until that time budget is used up.
        """
        # Filter tasks for the given date
        day_tasks: List[Task] = []
        for task in self._owner.get_all_tasks():
            if task.time().date() == target_date:
                day_tasks.append(task)

        # Sort by time then priority (descending)
        sorted_tasks = self.sort_by_time_and_priority(day_tasks)

        if available_minutes is None:
            return sorted_tasks

        # Respect the time budget
        chosen: List[Task] = []
        remaining = available_minutes
        for task in sorted_tasks:
            if task.duration_minutes() <= remaining:
                chosen.append(task)
                remaining -= task.duration_minutes()
            else:
                # no more time available for further tasks
                break
        return chosen

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        return sorted(tasks, key=lambda t: t.time())

    def sort_by_time_and_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort by time, then priority (higher priority first for same time)."""
        return sorted(tasks, key=lambda t: (t.time(), -t.priority()))

    def check_conflicts(self, tasks: List[Task]) -> List[Task]:
        """
        Simple conflict detection: tasks that start at the exact same time.
        (You can later upgrade this to use start/end intervals.)
        """
        if not tasks:
            return []

        sorted_tasks = self.sort_by_time(tasks)
        conflicts: List[Task] = []

        for i in range(len(sorted_tasks) - 1):
            current = sorted_tasks[i]
            nxt = sorted_tasks[i + 1]
            if current.time() == nxt.time():
                if current not in conflicts:
                    conflicts.append(current)
                if nxt not in conflicts:
                    conflicts.append(nxt)

        return conflicts