import pendulum

def ts_to_utc(ts):
    return ts

def rfc_3339_to_local_string(string):
    print(string)
    dt = pendulum.parse(string)
    local = dt.in_timezone("local")
    return local.strftime("%c")