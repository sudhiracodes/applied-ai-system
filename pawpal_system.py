from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List

@dataclass
class Task:
    _description: str
    _time: datetime
    _frequency: str
    _is_complete: bool = False

    def mark_complete(self) -> None:
        pass

    def description(self) -> str:
        pass

    def time(self) -> datetime:
        pass

    def frequency(self) -> str:
        pass

    def is_complete(self) -> bool:
        pass


@dataclass
class Pet:
    _name: str
    _species: str
    _tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def get_tasks(self) -> List[Task]:
        pass

    def name(self) -> str:
        pass

    def species(self) -> str:
        pass


@dataclass
class Owner:
    _name: str
    _pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_all_tasks(self) -> List[Task]:
        pass

    def name(self) -> str:
        pass

    def pets(self) -> List[Pet]:
        pass


@dataclass
class Scheduler:
    _owner: Owner

    def get_today_schedule(self, date: date) -> List[Task]:
        pass

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        pass

    def check_conflicts(self, tasks: List[Task]) -> List[Task]:
        pass