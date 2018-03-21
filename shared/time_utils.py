import datetime
import dateutil.tz

def ts_to_utc(ts):
    return datetime.datetime.utcfromtimestamp(ts).timestamp()

def utc_timestamp_to_local_string(ts):
    dt = datetime.datetime.fromtimestamp(ts)
    dt = dt.replace(tzinfo=dateutil.tz.tzutc())
    local = dt.astimezone(dateutil.tz.tzlocal())
    return local.strftime("%c")