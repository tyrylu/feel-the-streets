import inspect
import re
import inflection
from sqlalchemy import inspect as sa_inspect
from shared.models import Base
import shared.models as models
from .humanization_utils import underscored_to_words

model_display_strings = {}

def all_model_columns(entity):
    seen_columns = set()
    for table in sa_inspect(entity).tables:
        for column in table.columns:
            if column not in seen_columns:
                seen_columns.add(column)
                yield column

def get_column_display_name(column):
    return underscored_to_words(column.name)

def get_relationship_of(entity, column):
    relation_attr_name = column.name.replace("_id", "")
    relation_attr = getattr(entity, relation_attr_name)
    return relation_attr
    
def get_related_class(entity, column):
    relation_attr = get_relationship_of(entity, column)
    return relation_attr.property.mapper.class_

def get_foreign_display_name(klass):
    return re.sub(r"([a-z\d])([A-Z])([a-z\d])", lambda m: "%s %s%s"%(m.group(1), m.group(2).lower(), m.group(3)), klass.__name__)

def _all_models():
    for thing in models.__dict__.values():
        if inspect.isclass(thing) and issubclass(thing, Base):
            yield thing

def _populate_display_strings():
    for model in _all_models():
        model_display_strings[get_foreign_display_name(model)] = model

def get_model_class_display_strings():
    return list(model_display_strings.keys())

def lookup_model_class_by_display_string(string):
    return model_display_strings[string]

_populate_display_strings()