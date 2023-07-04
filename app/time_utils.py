import datetime

def ts_to_utc(ts):
    return ts

def rfc_3339_to_local_string(string):
    dt = datetime.datetime.fromisoformat(string)
    local = dt.astimezone()
    return local.strftime("%c")