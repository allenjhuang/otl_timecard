from datetime import datetime

def get_current_time(format):
    return datetime.now().strftime(format)
