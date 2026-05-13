from datetime import datetime
from shared.datetime_utils import parse_datetime

def is_live(fixture: dict) -> bool:
    status = fixture.get('status', '').lower()
    return status in ['live', 'inprogress', 'playing', '1st', '2nd', '3rd']
    
def is_finished(fixture: dict) -> bool:
    status = fixture.get('status', '').lower()
    return status in ['finished', 'fulltime', 'ended', 'ft']

if __name__ == "__main__":
    print("SCRIPT OK")
