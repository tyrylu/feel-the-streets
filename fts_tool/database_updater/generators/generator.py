import logging, pdb
from sqlalchemy import Boolean, DateTime, Float, Integer, inspect
from .utils import *
from .converters import *
from shared.sa_types import IntEnum, DimensionalFloat

log = logging.getLogger(__name__)

class Generator:
    instance_order = 0
    def __init__(self):
        Generator.instance_order += 1
        self.order = Generator.instance_order
        self._generates = None
        self._removes = []
        self._renames = {}
        self._unprefixes = []
        self._replaces_property_value = []
        self.removes('source', True)
        self.removes('ref', True)
        self.removes_subtree('dibavod')
        self.removes_subtree('name')
        self.removes('created_by')

    def generates(self, entity_class):
        self._generates = entity_class

    def removes(self, property, including_subtree=False):
        self._removes.append((property, True, including_subtree))

    def removes_subtree(self, root_property, including_root=False):
        self._removes.append((root_property, including_root, True))

    def renames(self, old_name, new_name):
        self._renames[old_name] = new_name

    def unprefixes(self, root):
        self._unprefixes.append(root)

    def replaces_property_value(self, property, string, replacement):
        self._replaces_property_value.append((property, string, replacement))
    
    def generate_from(self, entity_spec, record):
        if not self._generates:
            raise RuntimeError('Generated class not specified.')
        props = entity_spec.tags
        props = self._prepare_properties(entity_spec, props, record)
        return self._create_entity(props, record)

    def _prepare_properties(self, entity_spec, props, record):
        props = self._prepare_basic_props(entity_spec, props)
        props = self._lowercase_props(props)
        props = self._do_renames(props)
        props = self._do_unprefixes(props)
        props = self._do_replaces(props)
        props = self._do_removals(props)
        props = self._do_conversions(props, record)
        return props

    def _lowercase_props(self, props):
        ret = {}
        for prop, val in props.items():
            ret[prop.lower()] = val
        return ret

    def _do_removals(self, props):
        for prop, remove_root, remove_subtree in self._removes:
            if remove_root:
                val = props.pop(prop, None)
                if val:
                    pass

            if remove_subtree:
                props = remove_subproperties(props, prop)
        return props

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

    def _create_entity(self, props, record):
        if not self._check_required(props, record):
            return None
        props = self._remove_unknowns(props, record)
        return self._generates(**props)

    def _prepare_basic_props(self, entity, props):
        props['osm_id'] = entity.id
        props["osm_type"] = entity.type
        props["version"] = entity.version
        props["changeset"] = entity.changeset
        props["timestamp"] = entity.timestamp
        props["user"] = entity.user
        props["uid"] = entity.uid
        return props

    def _do_conversions(self, props, record):
        for col in inspect(self._generates).columns:
            if col.name == "geometry": continue
            if col.name in props:
                value = props[col.name]
                if isinstance(col.type, Boolean):
                    value = convert_boolean(self._generates.__name__, col.name, value, record)
                elif isinstance(col.type, IntEnum):
                    value = convert_enum(col.name, value, col.type._enum_class, record)
                elif isinstance(col.type, Float):
                    value = convert_float(self._generates.__name__, col.name, value, record)
                elif isinstance(col.type, Integer):
                    value = convert_integer(self._generates.__name__, col.name, value, record)
                elif isinstance(col.type, DateTime):
                    value = convert_datetime(self._generates.__name__, col.name, value, record)
                elif isinstance(col.type, DimensionalFloat):
                    value = convert_dimensional_float(self._generates.__name__, col.name, value, record)
                
                if value:
                    props[col.name] = value
                else:
                    del props[col.name]
        return props
    def _check_required(self, props, record):
        for column in inspect(self._generates).columns:
            if column.name in {"discriminator", "address_id", "geometry", "id"}: continue
            if not column.nullable and column.name not in props:
                record.add_missing_required_property(self._generates.__qualname__, column.name)
                return False
        return True

    def _remove_unknowns(self, props, record):
        unknown = []
        for prop, val in props.items():
            if prop == "address": continue
            if prop not in inspect(self._generates).columns:
                record.add_missing_property(self._generates.__name__, prop, val, self.order)
                unknown.append(prop)
        for prop in unknown:
            del props[prop]
        return props