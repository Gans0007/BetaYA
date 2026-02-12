# achievements/registry.py

from .conditions import gte, lte, exists

OPERATORS = {
    "gte": gte,
    "lte": lte,
    "exists": exists,
}
