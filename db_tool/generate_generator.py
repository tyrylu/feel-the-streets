import os
import inflection
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader(searchpath="."), trim_blocks=True, lstrip_blocks=True)
entity_class = input("Entity class to generate: ")
superclass = input("Superclass (empty for Generator): ")
if not superclass:
    superclass = "Generator"
acceptance_check = input("Generator acceptance condition: ")
generator_module = entity_class.lower()
generator_class = "%sGenerator"%entity_class
if superclass == "Generator":
    superclass_module = "generator"
else:
    superclass_module = inflection.underscore(superclass.replace("Generator", ""))
    acceptance_check = "%s.accepts(props) and %s"%(superclass, acceptance_check)
template = env.get_template("generator.tpl")
rendered = template.render(entity_class=entity_class, superclass=superclass, superclass_module=superclass_module, acceptance_check=acceptance_check, generator_module=generator_module, generator_class=generator_class)
with open(os.path.join("generators", "%s.py"%generator_module), "w") as fp:
    fp.write(rendered)
with open(os.path.join("generators", "__init__.py"), "a") as fh:
    fh.write("\nfrom .%s import %s"%(generator_module, generator_class))