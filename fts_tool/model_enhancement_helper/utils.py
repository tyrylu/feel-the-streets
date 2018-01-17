import redbaron
import keyword

def is_valid_identifier(name):
    return name.isidentifier() and not keyword.iskeyword(name)

def red_baron_from_file(name):
    with open(name, "r", encoding="utf-8") as fp:
        return redbaron.RedBaron(fp.read())

def is_nonascii(string):
    return any(ord(c) > 127 for c in string)