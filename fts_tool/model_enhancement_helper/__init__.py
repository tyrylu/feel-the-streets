from pathlib import Path
import click
from .model import Model
from ..database_updater.generation_record import GenerationRecord
from .enum import Enum
from .. import cli

def process_missing_enum_members(record):
    for enum_name, missing_values in record.missing_enum_members.items():
        enum_class = Enum(enum_name)
        print("Adding missing members to the %s enum."%enum_name)
        for value in missing_values:
            print("Adding value %s occurring %s times."%(value.member, value.occurrences))
            try:
                enum.add_member(value.member)
            except ValueError:
                print("Failed, mist likely is not a valid python identifier.")
        enum.save()

def select_from_choices(message, choices, wants_index=False):
    print(message)
    for i, choice in enumerate(choices):
        print("%s - %s"%(i + 1, choice))
    resp = input("Your choice: ")
    try:
        choice = int(choice)
    except:
        print("Please input an integer.")
        return select_from_choices(message, choices, wants_index)
    if choice < 1 or choice > len(choices):
        print("Invalid range.")
        return select_from_choices(message, choices, wants_index)
    if wants_index:
        return choice - 1
    else:
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
        return Ttrue
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
        
def do_add_property_addition(model, missing):
    if is_valid_identifier(missing.property_name):
        default_name = missing.member_name
    else:
        default_name = None
    column_name = click.prompt("Name of the database column", default=default_name)
    suggested_type_name = infer_type_from_values(missing.values)
    if suggested_type_name is None:
        candidate_enums = Enum.with_member_names(set(missing.values))
        if len(candidate_enums) == 1:
            suggested_type_name = "IntEnum(%s)"%candidate_enum_names[0]
        elif len(candidate_enums) > 1:
            suggested_type_name = "IntEnum(%s)"%select_from_choices("Please select the enum which you want")
        else:
            suggested_type_name = "UnicodeText"
    type_name = click.prompt("Type of the database column", default=suggested_type_name)
    model.add_property(missing.member_name, column_name, type_name)
    
    
def process_property_addition(model, missing):
    print("Adding the %s property with %s occurrences."%(missing.property, missing.occurrences))
    action = input("What do you want to do? (a)dd, (s)kip, (v)iew values: ")
    if action == "s":
        return
    elif action == "v":
        view_property_values(missing)
        return process_property_addition(model, missing)
    elif action == "a":
        return do_add_property(model, missing)
    else:
        print("Unknown choice.")
        return process_property_addition(model, missing)

def process_missing_properties(record):
    for entity_name, missing_properties in record.missing_properties.items():
        print("Processing entity %s."%entity_name)
        model = Model(entity_name)
        for missing in missing_properties:
            process_property_addition(model, missing)
        model.save()

@cli.command()
def enhance_model():
    records = Path.cwd().glob("*.grd")
    names = [p.name for p in records]
    path_idx = select_from_choices("Select the generation record file to use", names, True)
    record = GenerationRecord.from_pickle(records[path_idx])
    process_missing_enum_members(record)
    process_missing_properties(record)