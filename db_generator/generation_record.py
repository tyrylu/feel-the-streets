import attr

@attr.s
class MissingRequiredProperty:
    entity = attr.ib()
    property_name = attr.ib()
    occurrences = attr.ib(default=1)
@attr.s
class MissingProperty:
    entity = attr.ib()
    property_name = attr.ib()
    values = attr.ib(default=attr.Factory(list))

@attr.s
class MissingEnumMember:
    enum = attr.ib()
    member = attr.ib()
    occurrences = attr.ib(default=1)

@attr.s
class TypeViolation:
    entity = attr.ib()
    property_name = attr.ib()
    type = attr.ib()
    values = attr.ib(default=attr.Factory(list))
@attr.s
class GenerationRecord:
    total_entities = attr.ib(default=0)
    processed_entities = attr.ib(default=0)
    missing_properties = attr.ib(default=attr.Factory(list))
    missing_required_properties = attr.ib(default=attr.Factory(list))
    missing_enum_members = attr.ib(default=attr.Factory(list))
    type_violations = attr.ib(default=attr.Factory(list))

    def add_missing_property(self, entity, property, value):
        occurrence = self._lookup_missing_property(entity, property)
        if occurrence:
            occurrence.values.append(value)
        else:
            inst = MissingProperty(entity=entity, property_name=property)
            inst.values.append(value)
            self.missing_properties.append(inst)

    def _lookup_in_list_or_none(self, list, predicate):
        candidates = [inst for inst in list if predicate(inst)]
        if candidates:
            return candidates[0]
        else:
            return None

    def _lookup_missing_property(self, entity, property):
        return self._lookup_in_list_or_none(self.missing_properties, lambda mp: mp.property_name == property and mp.entity == entity)

    def add_missing_enum_member(self, enum, member):
        occurrence = self._lookup_missing_enum_member(enum, member)
        if occurrence:
            occurrence.occurrences += 1
        else:
            self.missing_enum_members.append(MissingEnumMember(enum=enum, member=member))

    def _lookup_missing_enum_member(self, enum, member):
        return self._lookup_in_list_or_none(self.missing_enum_members, lambda mi: mi.member == member and mi.enum == enum)

    def add_type_violation(self, entity, property, value, type=None):
        occurrence = self._lookup_type_violation(entity, property)
        if occurrence:
            occurrence.values.append(value)
        else:
            inst = TypeViolation(entity=entity, property_name=property, type=type)
            inst.values.append(value)
            self.type_violations.append(inst)

    def _lookup_type_violation(self, entity, property):
        return self._lookup_in_list_or_none(self.type_violations, lambda tv: tv.entity == entity and tv.property_name == property)

    def add_missing_required_property(self, entity, property):
        occurrence = self._lookup_missing_required_property(entity, property_name)
        if occurrence:
            occurrence.occurrences += 1
        else:
            self.missing_required_properties.append(MissingRequiredProperty(entity=entity, property_name=property))

    def _lookup_missing_required_property(self, entity, property):
        return self._lookup_in_list_or_none(self.missing_required_properties, lambda mi: mi.property == property and mi.entity == entity)
    def save_to_file(self, name):
        fp = open(name, "w", encoding="utf-8")
        fp.write("Out of %s processed features, %s were mapped to database entities.\n"%(self.total_entities, self.processed_entities))
        fp.write("* %s missing properties\n"%len(self.missing_properties))
        for missing in self.missing_properties:
            fp.write("** Entity %s is missing the property %s, appears %s times.\n"%(missing.entity, missing.property_name, len(missing.values)))
            fp.write("Values: %s\n"%", ".join('"%s"'%val for val in missing.values))
        fp.write("* %s missing enum members\n"%len(self.missing_enum_members))
        for missing in self.missing_enum_members:
            fp.write("** Enum %s is missing member %s, appears %s times.\n"%(missing.enum, missing.member, missing.occurrences))
        fp.write("* %s type violations\n"%len(self.type_violations))
        for violation in self.type_violations:
            fp.write("** The property %s of entity %s is probably not of the type %s, appears %s times\n"%(violation.property_name, violation.entity, violation.type, len(violation.values)))
            fp.write("Not matching values: %s\n"%", ".join('"%s"'%val for val in violation.values))
        fp.write("* %s Missing required properties\n"%len(self.missing_required_properties))
        for required in self.missing_required_properties:
            fp.write("Property %s is probably not required on entity %s, appears %s times.\n"%(required.property_name, required.entity, required.occurrences))
        fp.close()