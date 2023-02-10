from datetime import datetime
from dateutil.parser import parse as dtparser


def difference_from_now(dt: str):
    now = datetime.utcnow()
    _dt = dtparser(dt, ignoretz=True)
    diff = now - _dt
    return diff

