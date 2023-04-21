import math
import json
import yaml
from settings import format_material, format_rpg, construct_output
from collections import OrderedDict
import time

current_time_unix = int(time.time())

MAX_LEVEL = int(input("MAX LEVEL: "))
if (MAX_LEVEL < 1):
    exit(0)
RPG_ID = input("RPG ID PREFIX: ").upper()
TYPE = input("TYPE: ").upper()
BASE_1 = input("BASE ITEM 1 CURRENCY ID: ")
BASE_2 = input("BASE ITEM 2 CURRENCY ID: ")

def is_prime(n):
    if n <= 1:
        return False
    if n % 2 == 0:
        return n == 2

    max_div = math.floor(math.sqrt(n))
    for i in range(3, 1 + max_div, 2):
        if n % i == 0:
            return False
    return True

materialCollection = []
for i in range (1, MAX_LEVEL+1):
    if is_prime(i):
        materialCollection.append(
            {
                "number": i,
                "material": ""
            }
        )

materialName = {}
with open("item.json", "r") as f:
    materialName = json.load(f)

for each in materialCollection:
    numKey = str(each['number'])
    if (numKey in materialName.keys()):
        each['material'] = materialName[numKey]
    else:
        print(f"Please input material name for multiply of {each['number']}: ", end="")
        matName = input()
        each['material'] = matName
        materialName[numKey] = matName

tMatCol = {}
primeNumber = set()
for each in materialCollection:
    tMatCol[each['number']] = {"material": each['material'], "count": 0}
    primeNumber.add(each['number'])

with open("item.json", "w") as f:
    json.dump(materialName, f, indent="\t")
    
result = []
for i in range(1,MAX_LEVEL+1):
    current = OrderedDict()
    currentRPG = RPG_ID + "_" + str(format(i, '02'))
    output = construct_output(TYPE, RPG_ID, i)
    current = {
        "id": currentRPG,
        "output": output
    }
    conditions = []
    if (i == 1):
        conditions.append("nimbus{currency_id=\"impure_mithril_ingot\",amount=1}")
    conditions.append(format_material(BASE_1, i-1))
    conditions.append(format_material(BASE_2, i-1))
    for each in primeNumber:
        if (i % each == 0):
            conditions.append(format_material(tMatCol[each]['material'], tMatCol[each]['count']))
            tMatCol[each]['count'] += 1
    
    current['conditions'] = conditions
    
    if (i > 1):
        current['ingredients'] = [format_rpg(TYPE, RPG_ID, i-1)]
    elif (i == 1):
        current['ingredients'] = ['vanilla{type=dirt,amount=1}', 'vanilla{type=netherite_ingot,amount=1}']
        
    result.append(current)
transposedResult = {}
for each in result:
    id = each['id']
    del each['id']
    transposedResult[id] = each
transposedResult2 = {"recipes":transposedResult}

with open("generated-" + str(current_time_unix % 1000000) + ".yml", "w") as f:
    yaml.dump(transposedResult2, f, sort_keys=False)