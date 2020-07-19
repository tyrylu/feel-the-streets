import configparser

def ini_file_to_dict(ini_file_path):
    parser = configparser.ConfigParser()
    parser.read(ini_file_path)
    result = {}
    for section, values in parser.items():
        result[section] = {}
        result[section].update(values)
    return result

def dict_to_ini_file(ini_dict, dest_file):
    parser = configparser.ConfigParser()
    for section, values in ini_dict.items():
        parser.add_section(section)
        parser[section].update({k: str(v) for k, v in values.items()})
    with open(dest_file, "w", encoding="utf-8") as fp:
        parser.write(fp)
