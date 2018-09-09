from pathlib import Path
import re
import oyaml

class_declaration = re.compile(r"class ([a-zA-Z0-9_]+)(\(([a-zA-Z0-9_.]+)\)){0,1}:")


entities = {}
enums = {}
seen = set()
for file in Path(r"shared\entities").glob("*.py"):
    current_class = None
    for line in file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        match = class_declaration.match(line)
        if match:
            current_class = match.group(1)
            if current_class in seen:
                print("Class %s defined multiple times."%current_class)
            else:
                seen.add(current_class)
            if match.group(3) and match.group(3) == "enum.Enum":
                enums[current_class] = {}
            else:
                entities[current_class] = {}
                if match.group(3):
                    entities[current_class]["inherits"] = match.group(3)
                entities[current_class]["fields"] = {}
        else:
            tokens = line.strip().split(" ")
            if ":" in tokens[0] and len(tokens) > 1:
                field_name = tokens[0][:-1]
                entities[current_class]["fields"][field_name] = {"type": tokens[1]}
                if len(tokens) == 2:
                    entities[current_class]["fields"][field_name]["required"] = True
                elif tokens[3] != "None":
                    entities[current_class]["fields"][field_name]["default"] = tokens[3]
            elif len(tokens) == 3:
                if current_class not in enums: continue
                try:
                    val = int(tokens[2])
                    enums[current_class][tokens[0]] = val
                except ValueError: pass

entities_str = oyaml.dump(entities)
enums_str = oyaml.dump(enums, default_flow_style=False)
Path("entities.yaml").write_text(entities_str)
Path("enums.yaml").write_text(enums_str)