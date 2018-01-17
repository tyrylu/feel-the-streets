from pathlib import Path
import click
from .model import Model
from ..database_updater.generation_record import GenerationRecord
from .enum import Enum
from .. import cli
from .utils import is_valid_identifier

def process_missing_enum_members(record):
    for enum_name, missing_values in record.missing_enum_members.items():
        if not missing_values: continue
        enum_class = Enum(enum_name)
        print("Adding missing members to the %s enum."%enum_name)
        for value in missing_values:
            print("Adding value %s occurring %s times."%(value.member, value.occurrences))
            try:
                enum_class.add_member(value.member)
                missing_values.remove(value)
            except ValueError as exc:
                print(exc)
        enum_class.save()

def select_from_choices(message, choices, wants_index=False):
    print(message)
    for i, choice in enumerate(choices):
        print("%s - %s"%(i + 1, choice))
    resp = input("Your choice: ")
    try:
        choice = int(resp)
    except Exception as ex:
        print("Please input an integer.")
        return select_from_choices(message, choices, wants_index)
    if choice < 1 or choice > len(choices):
        print("Invalid range.")
        return select_from_choices(message, choices, wants_index)
    if wants_index:
        return choice - 1
    return choices[choice - 1]

def view_property_values(missing):
    num = input("How many values do you want to see? ")
    try:
        num = int(num)
    except:
        return view_property_values(missing)
    for val in missing.values[:(num + 1)]:
        print(val)

def is_int(val):
    try:
        int(val)
        return True
    except:
        return False

def is_float(val):
    try:
        float(val)
        return True
    except:
        return False

def infer_type_from_values(values):
    if any(" " in v for v in values):
        return "UnicodeText"
    elif all(is_int(v) for v in values):
        return "Integer"
    elif all(is_float(v) for v in values):
        return "Float"
    elif all(v in {"no", "yes"} for v in values):
        return "Boolean"
        
def do_create_enum(destination, values):
    name = input("Enter the enum name: ")
    if not name:
        return None
    try:
        Enum.create_in(destination, name, values)
        return "IntEnum(%s)"%name
    except ValueError:
        print("Could not create an enum given the values provided.")
        return None

def do_use_enum(values):
    name = input("Enum name: ")
    if not name:
        return None
    try:
        enum = Enum(name)
    except:
        print("Unknown enum.")
        return do_use_enum(values)
    for value in values:
        enum.add_member(value)
    enum.save()
    return "IntEnum(%s)"%name

def get_final_type_name(suggested_type_name, model, missing):
    type_name = click.prompt("Type of the database column (or ce if you want to create an enum from the values, or ue if you want to add the values to an existing enum)", default=suggested_type_name)
    if type_name == "ce":
        type_name = do_create_enum(model, set(missing.values))
    elif type_name == "ue":
        type_name = do_use_enum(missing.values)
    if not type_name:
        return get_final_type_name(suggested_type_name, model, missing)
    return type_name

def do_add_property(model, missing):
    if is_valid_identifier(missing.property_name):
        default_name = missing.property_name
    else:
        default_name = None
    column_name = click.prompt("Name of the database column", default=default_name)
    suggested_type_name = infer_type_from_values(missing.values)
    if suggested_type_name is None:
        candidate_enums = Enum.with_member_names(set(missing.values))
        if len(candidate_enums) == 1:
            suggested_type_name = "IntEnum(%s)"%candidate_enums[0]
        elif len(candidate_enums) > 1:
            suggested_type_name = "IntEnum(%s)"%select_from_choices("Please select the enum which you want", candidate_enums)
        else:
            suggested_type_name = "UnicodeText"
    type_name = get_final_type_name(suggested_type_name, model, missing)
    model.add_property(missing.property_name, column_name, type_name)
    if type_name.startswith("IntEnum"):
        enum_name = type_name[8:-1]
        enum = Enum(enum_name)
        if model._model_file.name != enum._file.name:
            if not enum.shared:
                print("Making the enum %s shared..."%enum_name)
                enum.make_shared()
            print("Adding shared import of the %s enum... "%enum_name, end="")
            if model.add_shared_enum_import(enum_name):
                print("success.")
            else:
                print("Not needed.")
    return True
    
    
def process_property_addition(model, missing):
    print("Adding the %s property with %s occurrences."%(missing.property_name, len(missing.values)))
    action = input("What do you want to do? (a)dd, (s)kip, (v)iew values, (n)ext entity: ")
    if action == "s":
        return False
    elif action == "v":
        view_property_values(missing)
        return process_property_addition(model, missing)
    elif action == "a":
        return do_add_property(model, missing)
    elif action == "n":
        return None
    else:
        print("Unknown choice.")
        return process_property_addition(model, missing)

def process_missing_properties(record):
    for entity_name, missing_properties in record.missing_properties.items():
        print("Processing entity %s."%entity_name)
        model = Model(entity_name)
        for missing in missing_properties:
            result = process_property_addition(model, missing)
            if result:
                missing_properties.remove(missing)
            elif result is None:
                break
        model.save()

@cli.command()
def enhance_model():
    records = list(Path.cwd().glob("*.grd"))
    names = [p.name for p in records]
    path_idx = select_from_choices("Select the generation record file to use", names, True)
    record_name = records[path_idx]
    record = GenerationRecord.from_pickle(record_name)
    process_missing_enum_members(record)
    record.save_to_pickle(record_name)
    process_missing_properties(record)
    record.save_to_pickle(record_name)