import yaml
import copy
import csv
import time
from collections import OrderedDict

current_time_unix = int(time.time())

TEMPLATE_FILE = input("Template File: ")
if (TEMPLATE_FILE.endswith(".yml") == False):
    TEMPLATE_FILE += ".yml"
print(f"Processing {TEMPLATE_FILE}")

with open(TEMPLATE_FILE, "r") as f:
    data = yaml.safe_load(f)
    data = OrderedDict(data)

if len(data.keys()) != 1:
    print("Please put level 1 as a template.")
    print(f"Found: {list(data.keys())}")
    exit(0)

TEMPLATE = list(data.keys())[0]
data[TEMPLATE]['level'] = 1
TEMPLATE_SPLIT = TEMPLATE.split("_")
if (len(TEMPLATE_SPLIT) != 3):
    print("Format: XXX_XXX_XXX.")
    print(f"Found: {TEMPLATE}")
    exit(0)
TEMPLATE_PREFIX = TEMPLATE_SPLIT[0] + "_" + TEMPLATE_SPLIT[1] + "_"
print(f"Found: {TEMPLATE_PREFIX}")

def process_lambda(obj, directory, fx, level):
    process_template(obj, directory, fx(level, obj['base']))

def process_template(result, directory, value):
    cursor = result['base']
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

MODIFIERDATA = input("Modifier File: ")
if (len(MODIFIERDATA) > 0):
    if (MODIFIERDATA.endswith('.csv') == False):
        MODIFIERDATA += ".csv"
    print(f"Processing {MODIFIERDATA}")
    modifierData = []
    with open(MODIFIERDATA, "r") as f:
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

LAMBDADATA = input("Lambda File: ")
if (len(LAMBDADATA) > 0):
    if (LAMBDADATA.endswith('.csv') == False):
        LAMBDADATA += ".csv"
    print(f"Processing {LAMBDADATA}")
    lambdaData = []
    with open(LAMBDADATA, "r") as f:
        lambdaFile = csv.DictReader(f)
        for each in lambdaFile:
            lambdaData.append(each)
    for l in lambdaData:
        fx = eval(l['function'])
        l['function'] = fx
    for each in data:
        for l in lambdaData:
            process_lambda(data[each], l['directory'], l['function'], data[each]['level'])

for each in data:
    del data[each]['level']

with open("generated-" + str(current_time_unix % 1000000) + ".yml", "w") as f:
    yaml.dump(dict(data), f, sort_keys=False)