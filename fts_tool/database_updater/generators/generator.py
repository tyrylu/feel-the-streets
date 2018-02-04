from enum import Enum
from datetime import datetime
import logging
from .utils import *
from .converters import *
from shared.validated_quantity import Quantity

log = logging.getLogger(__name__)

class Generator:
    instance_order = 0
    def __init__(self):
        Generator.instance_order += 1
        self.order = Generator.instance_order
        self._generates = None
        self._renames = {}
        self._unprefixes = []
        self._replaces_property_value = []

    def generates(self, entity_class):
        self._generates = entity_class

    def renames(self, old_name, new_name):
        self._renames[old_name] = new_name

    def unprefixes(self, root):
        self._unprefixes.append(root)

    def replaces_property_value(self, property, string, replacement):
        self._replaces_property_value.append((property, string, replacement))
    
    def generate_from(self, entity_spec, record):
        if not self._generates:
            raise RuntimeError('Generated class not specified.')
        self._set_common_attrs(entity_spec)
        props = entity_spec.tags
        props = self._prepare_properties(entity_spec, props, record)
        if not self._check_required(props, record):
            return None
        return props

    def _prepare_properties(self, entity_spec, props, record):
        props = self._lowercase_props(props)
        props = self._do_renames(props)
        props = self._do_unprefixes(props)
        props = self._do_replaces(props)
        props = self._do_conversions(props, record)
        return props

    def _lowercase_props(self, props):
        ret = {}
        for prop, val in props.items():
            ret[prop.lower()] = val
        return ret

    def _do_renames(self, props):
        for old_name, new_name in self._renames.items():
            props = rename_dict_key(props, old_name, new_name)
        return props

    def _do_unprefixes(self, props):
        for prop in self._unprefixes:
             props = unprefix_properties(props, prop)
        return props

    def _do_replaces(self, props):
        for prop, string, replacement in self._replaces_property_value:
            if prop in props:
                props[prop] = props[prop].replace(string, replacement)
        return props

    def _do_conversions(self, props, record):
        for field in self._generates.__fields__.values():
            if field.name in props:
                value = props[field.name]
                if field.type_ is bool:
                    value = convert_boolean(self._generates.__name__, field.name, value, record)
                elif issubclass(field.type_, Enum):
                    value = convert_enum(field.name, value, field.type_, record)
                elif field.type_ is float:
                    value = convert_float(self._generates.__name__, field.name, value, record)
                elif field.type_ is int:
                    value = convert_integer(self._generates.__name__, field.name, value, record)
                elif field.type_ is datetime:
                    value = convert_datetime(self._generates.__name__, field.name, value, record)
                elif field.type_ is Quantity:
                    value = convert_dimensional_float(self._generates.__name__, field.name, value, record)
                
                if value:
                    props[field.name] = value
                else:
                    del props[field.name]
        return props
    
    def _check_required(self, props, record):
        for field in self._generates.__fields__.values():
            if field.required and field.name not in props:
                record.add_missing_required_property(self._generates.__qualname__, field.name)
                return False
        return True

    def _check_unknowns(self, props, record):
        field_names = set(self._generates.__fields__.keys())
        for prop, val in props.items():
            if prop not in field_names:
                record.add_missing_property(self._generates.__name__, prop, val, self.order)
    
    def _set_common_attrs(self, osm_object):
        props = osm_object.tags
        props['osm_id'] = osm_object.id
        props["osm_type"] = osm_object.type
        props["version"] = osm_object.version
        props["changeset"] = osm_object.changeset
        props["timestamp"] = osm_object.timestamp
        props["user"] = osm_object.user
        props["uid"] = osm_object.uid


    @staticmethod
    def accepts(props):
        return False