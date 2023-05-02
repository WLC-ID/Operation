import yaml

with open("table.yml", "r", encoding='utf-8') as f:
    data = yaml.safe_load(f)
    
root = list(data.keys())[0]
multiplier = float(input("Multiplier: "))
for n in data[root]['items'].keys():
    target = data[root]['items'][n]
    target['buyPrice'] = round(target['sellPrice'] * multiplier,2)
    
with open("generated.yml", "w", encoding='utf-8') as f:
    yaml.dump(data, f, sort_keys=True)