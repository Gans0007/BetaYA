from dataclasses import dataclass

@dataclass
class Habit:
    id: int
    name: str
    done_days: int
    days: int
    confirm_type: str
