from shared.entities import OSMEntity

class EntityRegistry:
    def __init__(self):
        self._discriminator_to_class = {}
        self._fill()

    def _fill(self, parent_class=OSMEntity, add_parent=False):
        if add_parent:
            self._discriminator_to_class[parent_class.__name__] = parent_class
        for subclass in parent_class.__subclasses__():
            self._fill(subclass, True)

    def lookup_entity_class_by_discriminator(self, discriminator):
        return self._discriminator_to_class[discriminator]

    @property
    def known_entity_classes(self):
        return self._discriminator_to_class.values()
    
    def all_discriminators_for_subclasses_of(self, parent):
        results = []
        for discriminator, class_ in self._discriminator_to_class.items():
            if class_ is parent:
                results.append(discriminator)
        for subclass in parent.__subclasses__():
            results += self.all_discriminators_for_subclasses_of(subclass)
        return results