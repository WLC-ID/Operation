import yaml
import copy
import csv
import hashlib
import numpy as np
from collections import OrderedDict
from formula import *
import re
import datetime

TEMPLATE_FILE = "multiply-table.yml"
# TEMPLATE_FILE = input("Template File: ")
# if (TEMPLATE_FILE.endswith(".yml") == False):
#     TEMPLATE_FILE += ".yml"
# print(f"Processing {TEMPLATE_FILE}")

with open(TEMPLATE_FILE, "r") as f:
    data = yaml.safe_load(f)
    data = OrderedDict(data)
templateHexDigest = hashlib.md5(data.__str__().encode('utf-8')).hexdigest()
templateDigest = np.base_repr(int(templateHexDigest, 16), 36)

if len(data.keys()) != 1:
    print("Please put level 1 as a template.")
    print(f"Found: {list(data.keys())}")
    exit(0)

TEMPLATE = list(data.keys())[0]
data[TEMPLATE]['level'] = 1
RARITY = data[TEMPLATE]['base']['tier']
if (RARITY == None or len(RARITY) == 0):
    print("Rarity not found.")
    print(f"Found: {RARITY}")
    exit(0)
RARITY = RARITY.lower()
    
TEMPLATE_SPLIT = TEMPLATE.split("_")
if (len(TEMPLATE_SPLIT) != 3):
    print("Format: XXX_XXX_XXX.")
    print(f"Found: {TEMPLATE}")
    exit(0)
TEMPLATE_PREFIX = TEMPLATE_SPLIT[0] + "_" + TEMPLATE_SPLIT[1] + "_"
print(f"Found: {TEMPLATE_PREFIX}")

def var_template(var_name):
    result = ""
    splitted = var_name.split(".")
    NOI = len(splitted) - 1
    for o in splitted:
            result += "['" + o + "']"
    return "y" + result

def process_lambda(obj, directory, fx, level):
    if ('ability@' in directory):
        directory = directory.replace('ability@','ability.ability')
    process_template(obj, directory, fx(level, obj['base']))

def process_template(result, directory, value):
    cursor = result['base']
    if ('ability@' in directory):
        directory = directory.replace('ability@','ability.ability')
    sections = directory.split(".")
    N = len(sections)
    for num, section in enumerate(sections,1):
        if (type(cursor) is dict and section not in cursor.keys()):
            print(f"Result: Invalid directory '{directory}'.")
            exit(0)
        elif (type(cursor) is list and int(section) >= len(cursor)):
            print(f"Result: Invalid index '{directory}'.")
            exit(0)
        
        if (type(cursor) is list):
            section = int(section)

        if (num == N):
            if (type(cursor[section]) is not type(value)):
                if (type(cursor[section]) is int):
                    value = int(value)
                elif (type(cursor[section]) is float):
                    value = float(value)
                else:
                    print(f"Result: Type mismatch on '{directory}'. Expected: {type(cursor[section])}. Found: {type(value)}")
                    exit(0)
            
            cursor[section] = value
            continue
        if (type(cursor) is dict):
            cursor = cursor[section]

FILENAME = TEMPLATE_SPLIT[0] + "_" + TEMPLATE_SPLIT[1] + ".csv"
MODIFIERDATA = "./item/" + RARITY + "/" + FILENAME
print(f"Processing {MODIFIERDATA}")
modifierData = []
try:
    with open(MODIFIERDATA, "r") as f:
        modifierFile = csv.DictReader(f)
        for each in modifierFile:
            modifierData.append(each)
except FileNotFoundError:
    with open(f"./item/" + RARITY + ".csv", "r") as f:
        modifierFile = csv.DictReader(f)
        for each in modifierFile:
            modifierData.append(each)
for each in modifierData:
    ITEM_NAME = TEMPLATE_PREFIX + format(int(each['level']), '02')
    result = copy.deepcopy(data[TEMPLATE])
    result['level'] = int(each['level'])
    for dir in each.keys():
        if (dir == 'level'):
            continue
        process_template(result, dir, each[dir])
    data[ITEM_NAME] = result

LAMBDADATA = "./lambda/" + RARITY + "/" + FILENAME
if (LAMBDADATA.endswith('.csv') == False):
    LAMBDADATA += ".csv"
print(f"Processing {LAMBDADATA}")
lambdaData = []
with open(LAMBDADATA, "r") as f:
    lambdaFile = csv.DictReader(f)
    for each in lambdaFile:
        lambdaData.append(each)
for l in lambdaData:
    if (l['function'].startswith('lambda x,y: ') == False):
        l['function'] = 'lambda x,y: ' + l['function']
    if ('$' in l['function']):
        segment = re.findall('{(.*?)}', l['function'])
        for s in segment:
            s2 = re.findall('\$(.*?)\$', s)
            if (len(s2) > 0):
                for s3 in s2:
                    s3r = var_template(s3)
                    l['function'] = l['function'].replace('$'+s3+'$', s3r, 1)
        print(l['function'])
    if ('ability@' in l['function']):
        l['function'] = l['function'].replace('ability@','ability\'][\'ability')
    fx = eval(l['function'])
    l['function'] = fx
for each in data:
    for l in lambdaData:
        process_lambda(data[each], l['directory'], l['function'], data[each]['level'])

for each in data:
    del data[each]['level']

flattened = dict(data)
hexdigest = hashlib.md5(flattened.__str__().encode('utf-8')).hexdigest()
digest = np.base_repr(int(hexdigest, 16), 36)
RESULT_FILE = f"./generated/{TEMPLATE_SPLIT[0]}_{TEMPLATE_SPLIT[1]}-{digest}.yml"
with open(RESULT_FILE, "w") as f:
    f.write(f"# Template: {TEMPLATE_SPLIT[0]}_{TEMPLATE_SPLIT[1]}_XXX. Digest: {templateHexDigest}. Base36: {templateDigest}\n")
    f.write(f"# Generated at {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}. Digest: {hexdigest}. Base36: {digest}.\n")
    yaml.dump(flattened, f, sort_keys=False)
    print("Saved to " + RESULT_FILE)