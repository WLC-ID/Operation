import os
import hashlib
import yaml
import numpy as np

DIRECTORY = "./generated/" + input("Directory: ")
for dirpath, _, filenames in os.walk(DIRECTORY):
    if ("compiled" in dirpath):
        continue
    for filename in filenames:
        if not("-" in filename):
            continue
        splitted = filename.split("-")
        hash = splitted[1].replace(".yml","")
        with open(f"{dirpath}/{filename}", "r") as f:
            data = yaml.safe_load(f)
        hexdigest = hashlib.md5(yaml.dump(data, sort_keys=False).encode('utf-8')).hexdigest()
        b36 = np.base_repr(int(hexdigest, 16), 36)
        if b36 != hash:
            print(f"Hash mismatch: {filename}. Found: {b36}. Expected: {hash}")