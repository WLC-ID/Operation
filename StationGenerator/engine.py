import copy
from collections import OrderedDict
import hashlib
import numpy as np

# def is_prime(n):
#     if n <= 1:
#         return False
#     if n % 2 == 0:
#         return n == 2

#     max_div = math.floor(math.sqrt(n))
#     for i in range(3, 1 + max_div, 2):
#         if n % i == 0:
#             return False
#     return True

# MAX_LEVEL = 15
# NUMBERS = [i for i in range(1, MAX_LEVEL+1)]
# PRIME_NUMBERS = list(filter(is_prime, NUMBERS))
def hashdigest(data):
    assert type(data) is dict or type(data) is OrderedDict
    
    hexDigest = hashlib.md5(yaml.dump(dict(data), sort_keys=False).encode('utf-8')).hexdigest()
    b36Digest = np.base_repr(int(hexDigest, 16), 36)
    return {'hex': hexDigest, 'base36': b36Digest}

class ItemLine:
    def __init__(self, material_name, starting_level, increment, max_amount, every_n_level = 1):
        assert material_name != None and increment != None and max_amount != None and starting_level != None
        assert every_n_level != None and type(every_n_level) is int and every_n_level > 0
        assert type(increment) is int and type(max_amount) is int and type(starting_level) is int
        assert len(material_name) > 0
        assert increment > 0 and max_amount > 0 and starting_level >= 0
        
        self.name = material_name
        self.increment = increment
        self.max_amount = max_amount
        self.starting_level = starting_level
        self.every_n_level = every_n_level
        self.max_level = 999999
        
    def count_to_n(self, level):
        assert level != None and type(level) is int
        if (level < self.starting_level):
            return 0
        if (level > self.max_level):
            return 0
        N = list(filter(self.is_now, range(self.starting_level, level+1)))
        return len(N)
    
    def is_now(self, level):
        assert level != None and type(level) is int
        if (level < self.starting_level or level > self.max_level):
            return False
        if (level == self.starting_level or self.every_n_level == 1):
            return True
        
        return (level-self.starting_level)% self.every_n_level == 0
        
    def get(self, level, minus=1):
        assert level != None and type(level) is int
        assert minus != None and type(minus) is int and minus >= 0
        if (level < self.starting_level or not self.is_now(level) or level > self.max_level):
            return 0
        
        x = self.count_to_n(level)
        count = self.increment * (x-minus)
        if level == self.starting_level and minus != 0:
            count = 1
        return min(count,self.max_amount)

    def set_max_level(self, level):
        assert level != None and type(level) is int
        self.max_level = level
        return self
        
    def format_nimbus(self, level, minus=1):
        assert level != None and type(level) is int
        return "nimbus{" + f"currency_id=\"{self.name}\",amount={self.get(level,minus)}" + "}"

class Recipe:
    def __init__(self, gen, rpgId, rpgType, level, offset):
        assert gen != None and type(gen) is RecipeGenerator
        assert offset != None and type(offset) is int and offset >= 0
        assert rpgId != None and type(rpgId) is str and len(rpgId) > 0
        assert rpgType != None and type(rpgType) is str and len(rpgType) > 0
        assert level != None and type(level) is int and level > 0
        
        self.output = Factory.output(rpgId, level-offset, rpgType)
        self.virtual = []
        self.ingredients = []
        self.name = rpgId
        self.rpgType = rpgType
        self.level = level
        self.gen = gen
        self.offset = offset
        self.key = rpgId + "_" + str(format(level-offset, '02'))
        self.init()
    
    def init(self):
        if (self.level > 1):
            self.ingredients.append(Factory.rpg(self.name, self.level-1-self.offset, self.rpgType))
        elif (self.level == 1):
            self.ingredients.append(Factory.vanilla("book", 1))
    
    def setup(self):
        x = self.level
        for item in self.gen.items:
            assert item != None and type(item) is ItemLine
            if (item.is_now(x)):
                self.virtual.append(item.format_nimbus(x))
        for item in self.gen.dungeon:
            assert item != None and type(item) is ItemLine
            if (item.is_now(x)):
                self.virtual.append(item.format_nimbus(x,0))
    
    def format(self):
        return (self.key, {
            'output': self.output,
            'conditions': self.virtual,
            'ingredients': self.ingredients
        })

class Factory:
    def output(prefix, level, rpgType):
        assert prefix != None and type(prefix) is str and len(prefix) > 0
        assert level != None and type(level) is int
        assert rpgType != None and type(rpgType) is str and len(rpgType) > 0
        return {
            "type": rpgType,
            "id": prefix + "_" + str(format(level, '02')),
            "amount": 1
        }
    
    def rpg(prefix, level, rpgType):
        assert prefix != None and type(prefix) is str and len(prefix) > 0
        assert level != None and type(level) is int
        assert rpgType != None and type(rpgType) is str and len(rpgType) > 0
        return "mmoitem{" + f"type={rpgType},id={prefix}_{str(format(level, '02'))},amount=1" + "}"
    
    def vanilla(material, amount):
        assert material != None and type(material) is str and len(material) > 0
        assert amount != None and type(amount) is int
        return "vanilla{" + f"type={material},amount={amount}" + "}"
    
    def itemLine(obj):
        assert obj != None and type(obj) is dict
        for each in ['name', 'increment', 'max', 'start', 'every']:
            assert each in obj.keys()
            
        result = ItemLine(obj['name'], obj['start'], obj['increment'], obj['max'], obj['every'])
        
        if 'stop' in obj.keys():
            assert obj['stop'] != None and type(obj['stop']) is int
            result.set_max_level(obj['stop'])
        return result

    def itemLineTemplate(obj, name):
        assert obj != None and type(obj) is dict
        assert name != None and type(name) is str and len(name) > 0
        
        objCopied = copy.deepcopy(obj)
        objCopied['name'] = name
        return Factory.itemLine(objCopied)

import os, json, yaml

class RecipeGenerator:
    
    def __init__(self, file_dir):
        assert file_dir != None and type(file_dir) is str and len(file_dir) > 0
        file_dir = "./data/" + file_dir
        if not file_dir.endswith(".json"):
            file_dir += ".json"
        assert os.path.exists(file_dir)
        
        with open(file_dir, 'r') as f:
            self.data = json.load(f)
        
        self.items = []
        self.dungeon = []
        assert self.data['level'] != None and type(self.data['level']) is dict
        assert self.data['level']['offset'] != None and type(self.data['level']['offset']) is int
        assert self.data['level']['max'] != None and type(self.data['level']['max']) is int
        self.offset = self.data['level']['offset']
        self.max = self.offset+self.data['level']['max']
        
        assert self.data['info'] != None and type(self.data['info']) is dict
        assert self.data['info']['name'] != None and type(self.data['info']['name']) is str and len(self.data['info']['name']) > 0
        assert self.data['info']['type'] != None and type(self.data['info']['type']) is str and len(self.data['info']['type']) > 0
        
        self.name = self.data['info']['name']
        self.rpgType = self.data['info']['type']
        
        self.access('eventual', self.items)
        self.access('base', self.items)
        self.access('dungeon', self.dungeon)
        self.access('compulsory', self.items)
    
    def access(self, key, target):
        assert target != None and type(target) is list
        assert key in self.data.keys() and self.data[key] != None and type(self.data[key]) is list
        for each in self.data[key]:
            assert each != None and type(each) is dict
            if key == 'eventual':
                each['start'] += self.offset
                each['stop'] += self.offset
            target.append(Factory.itemLine(each))
            
    def run(self):
        result = {}
        for lvl in range(1+self.offset, self.max+1):
            recipe = Recipe(self, self.name, self.rpgType, lvl, self.offset)
            recipe.setup()
            k, obj = recipe.format()
            result[k] = obj
        
        result = {'recipes': result}
        dg = hashdigest(result)
        with open(f'generated-{dg["base36"]}.yml', 'w') as f:
            yaml.dump(result, f, sort_keys=False)
        print("Saved to generated-%s.yml" % dg["base36"])