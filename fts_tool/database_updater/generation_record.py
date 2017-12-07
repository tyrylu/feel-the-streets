import pickle
import attr
from collections import defaultdict

def make_factory(callable, *args):
    def caller():
        return callable(*args)
    return caller

@attr.s
class MissingRequiredProperty:
    entity = attr.ib()
    property_name = attr.ib()
    occurrences = attr.ib(default=1)

@attr.s
class MissingProperty:
    property_name = attr.ib()
    values = attr.ib(default=attr.Factory(list))
    entity_orders = attr.ib(default=attr.Factory(list))

@attr.s
class MissingEnumMember:
    member = attr.ib()
    occurrences = attr.ib(default=1)

@attr.s
class TypeViolation:
    property_name = attr.ib()
    type = attr.ib()
    values = attr.ib(default=attr.Factory(list))
@attr.s
class GenerationRecord:
    total_entities = attr.ib(default=0)
    processed_entities = attr.ib(default=0)
    missing_properties = attr.ib(default=attr.Factory(make_factory(defaultdict, list)))
    missing_required_properties = attr.ib(default=attr.Factory(list))
    missing_enum_members = attr.ib(default=attr.Factory(make_factory(defaultdict, list)))
    type_violations = attr.ib(default=attr.Factory(make_factory(defaultdict, list)))

    def add_missing_property(self, entity, property, value, entity_order):
        occurrence = self._lookup_missing_property(entity, property)
        if occurrence:
            occurrence.values.append(value)
            occurrence.entity_orders.append(entity_order)
        else:
            inst = MissingProperty(property_name=property)
            inst.values.append(value)
            inst.entity_orders.append(entity_order)
            self.missing_properties[entity].append(inst)

    def _lookup_in_list_or_none(self, list, predicate):
        candidates = [inst for inst in list if predicate(inst)]
        if candidates:
            return candidates[0]

    def _lookup_missing_property(self, entity, property):
        return self._lookup_in_list_or_none(self.missing_properties[entity], lambda mp: mp.property_name == property)

    def add_missing_enum_member(self, enum, member):
        occurrence = self._lookup_missing_enum_member(enum, member)
        if occurrence:
            occurrence.occurrences += 1
        else:
            self.missing_enum_members[enum].append(MissingEnumMember(member=member))

    def _lookup_missing_enum_member(self, enum, member):
        return self._lookup_in_list_or_none(self.missing_enum_members[enum], lambda mi: mi.member == member)

    def add_type_violation(self, entity, property, value, type=None):
        occurrence = self._lookup_type_violation(entity, property)
        if occurrence:
            occurrence.values.append(value)
        else:
            inst = TypeViolation(property_name=property, type=type)
            inst.values.append(value)
            self.type_violations[entity].append(inst)

    def _lookup_type_violation(self, entity, property):
        return self._lookup_in_list_or_none(self.type_violations[entity], lambda tv: tv.property_name == property)

    def add_missing_required_property(self, entity, property_name):
        occurrence = self._lookup_missing_required_property(entity, property_name)
        if occurrence:
            occurrence.occurrences += 1
        else:
            self.missing_required_properties.append(MissingRequiredProperty(entity=entity, property_name=property_name))

    def _lookup_missing_required_property(self, entity, property):
        return self._lookup_in_list_or_none(self.missing_required_properties, lambda mi: mi.property_name == property and mi.entity == entity)
    def save_to_file(self, name):
        self.sort_by_occurrences()
        fp = open(name, "w", encoding="utf-8")
        fp.write("Out of %s processed features, %s were mapped to database entities.\n"%(self.total_entities, self.processed_entities))
        fp.write("* missing properties of %s entities\n"%len(self.missing_properties))
        for entity, missings in self.missing_properties.items():
            fp.write("** %s\n"%entity)
            for missing in missings:
                fp.write("*** missing property %s, appears %s times.\n"%(missing.property_name, len(missing.values)))
                fp.write("Values: %s\n"%", ".join('"%s"'%val for val in missing.values))
                fp.write("Occurs for entities %s.\n"%", ".join(str(o) for o in missing.entity_orders))
        fp.write("* %s enums has missing members\n"%len(self.missing_enum_members))
        for enum, missings in self.missing_enum_members.items():
            fp.write("** %s\n"%enum)
            for missing in missings:
                fp.write("*** missing member %s, appears %s times.\n"%(missing.member, missing.occurrences))
        fp.write("* Type violations for %s entities\n"%len(self.type_violations))
        for entity, violations in self.type_violations.items():
            fp.write("** %s\n"%entity)
            for violation in violations:
                fp.write("*** Property %s is probably not of the type %s, appears %s times\n"%(violation.property_name, violation.type, len(violation.values)))
                fp.write("Not matching values: %s\n"%", ".join('"%s"'%val for val in violation.values))
        fp.write("* %s Missing required properties\n"%len(self.missing_required_properties))
        for required in self.missing_required_properties:
            fp.write("Property %s is probably not required on entity %s, appears %s times.\n"%(required.property_name, required.entity, required.occurrences))
        fp.close()

    def save_to_pickle(self, pickle_path):
        self.sort_by_occurrences()
        with open(pickle_path, "wb") as fp:
            pickle.dump(self, fp)

    @staticmethod
    def from_pickle(self, pickle_path):
        with open(pickle_path, "rb") as fp:
            return pickle.load(fp)
    
    def sort_by_occurrences(self):
        for missings in self.missing_properties.values():
            missings.sort(key=lambda occ: len(occ.values), reverse=True)
        for missings in self.missing_enum_members.values():
            missings.sort(key=lambda occ: occ.occurrences, reverse=True)