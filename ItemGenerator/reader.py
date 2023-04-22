from collections import OrderedDict
import yaml
import copy
import csv
import time

current_time_unix = int(time.time())
FILTER = input("Filter: ")
FILE = input("CSV File: ")
if (FILE.endswith('.csv') == False):
    FILE += ".csv"
print(f"Processing {FILE}")
with open(FILE, "r") as f:
    csvFile = csv.reader(f)
    header = next(csvFile)
    
OBJ_TEMPLATE = OrderedDict()
OBJ_TEMPLATE['level'] = None
for each in header:
    OBJ_TEMPLATE[each] = None

DATAFILE = input("Data File: ")
if (DATAFILE.endswith('.yml') == False):
    DATAFILE += ".yml"
print(f"Processing {DATAFILE}")
with open(DATAFILE, "r") as f:
    data = yaml.safe_load(f)
    data = OrderedDict(data)
    
result = []
for key in data.keys():
    if (key.startswith(FILTER) == False):
        continue
    current = copy.deepcopy(OBJ_TEMPLATE)
    level = int(key.split("_")[2])
    current['level'] = level
    cursor = data[key]['base']
    for each in current.keys():
        directory = each.split(".")
        cursorcursor = cursor
        N = len(directory)
        for num, section in enumerate(directory,start=1):
            if (section == 'level'):
                continue
            if (type(cursorcursor) is list):
                section = int(section)
            
            if (num != N):
                cursorcursor = cursorcursor[section]
            else:
                if (each in current.keys()):
                    current[each] = cursorcursor[section]
                break
    result.append(dict(current))
    
with open(FILE, "w") as f:
    writer = csv.DictWriter(f, fieldnames=result[0].keys(),lineterminator='\n')
    writer.writeheader()
    for each in result:
        writer.writerow(each)