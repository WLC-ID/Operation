import os
import hashlib
import json
import re
import yaml
import numpy as np

DIRECTORY = "./generated/" + input("Directory: ")
with open("./compiler-config.json", "r") as f:
    mapping = json.load(f)

DATA = dict()
for each in mapping.keys():
    DATA[mapping[each]] = {
        "target": each,
        "content": ""
    }

for dirpath, _, filenames in os.walk(DIRECTORY):
    if ("compiled" in dirpath):
        continue
    for filename in filenames:
        if (len(filename) < 2 or filename.endswith(".yml") == False):
            break
        clazz = filename[0] + filename[1]
        clazz = clazz.upper()
        if (clazz not in DATA.keys()):
            print(f"Classification {clazz} not found in mapping.")
            continue
        filepath = f"{dirpath}/{filename}"
        content = ""
        with open(filepath, "r") as f:
            for line in f:
                if line.startswith("# Template:") or line.startswith("# Generated at"):
                    pattern = re.compile(r"Digest:\s(.+?)\.\sBase36")
                    m = pattern.search(line)
                    content += "# " + m.group(1) + "\n"
                else:
                    content += line
        DATA[clazz]["content"] += content

HexDigest = hashlib.md5(yaml.dump(DATA).encode('utf-8')).hexdigest()
Digest = np.base_repr(int(HexDigest, 16), 36)

COMPILED = f"{DIRECTORY}/compiled/{Digest}"
if not os.path.exists(COMPILED):
    os.makedirs(COMPILED)

for each in DATA.keys():
    with open(f"{COMPILED}/{DATA[each]['target']}", "w") as f:
        f.write(DATA[each]["content"])
print(f"Result has been saved to {COMPILED}")