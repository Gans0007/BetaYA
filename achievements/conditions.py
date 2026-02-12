# achievements/conditions.py

def gte(value, target):
    return value is not None and value >= target


def lte(value, target):
    return value is not None and value <= target


def exists(value, target=None):
    return value is not None
