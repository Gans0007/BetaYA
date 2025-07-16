from dataclasses import dataclass

@dataclass
class Habit:
    id: int
    user_id: int
    name: str
    days: int
    description: str
    done_days: int
    is_challenge: int
    confirm_type: str
    created_at: str
    is_active: int

