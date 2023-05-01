import hashlib
import numpy as np
from collections import OrderedDict
import yaml
import copy
import csv
import re
import datetime
from formula import *
import os
import json

def var_template(var_name):
    result = ""
    splitted = var_name.split(".")
    for o in splitted:
            result += "['" + o + "']"
    return "y" + result

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

def process_lambda(obj, directory, fx, level):
    if ('ability@' in directory):
        directory = directory.replace('ability@','ability.ability')
    process_template(obj, directory, fx(level, obj['base']))
    
def hashdigest(data):
    assert type(data) is dict or type(data) is OrderedDict
    
    hexDigest = hashlib.md5(yaml.dump(dict(data), sort_keys=False).encode('utf-8')).hexdigest()
    b36Digest = np.base_repr(int(hexDigest, 16), 36)
    return {'hex': hexDigest, 'base36': b36Digest}

class Generator:
    def __init__(self):
        self.template_file_name = "!multiply-table.yml"
        self.modifier_folder = lambda rarity,item: f"./item/{rarity}/{item}"
        self.lambda_folder = lambda rarity,item: f"./lambda/{rarity}/{item}"
        self.result_folder =  lambda rarity: f"./generated/{rarity}"
        
    def __load__(self):
        data = []
        with open(self.template_file_name, "r") as f:
            data = yaml.safe_load(f)
            data = OrderedDict(data)
        return data
    
    def __target_load__(self, dir):
        assert dir != None and len(dir) > 0
        
        data = []
        with open(dir, "r") as f:
            data = yaml.safe_load(f)
            data = OrderedDict(data)
        return data
        
    def __digest__(self, data):
        return hashdigest(data)
    
    def __parse_rarity__(self, data):
        result = data[self.template_key]['base']['tier']
        if (result == None or len(result) == 0):
            print("Rarity not found.")
            print(f"Found: {result}")
            return
        return result.lower()
    
    def __validate_data__(self, data):
        if len(data.keys()) < 1:
            print("Please put level 1 as a template.")
            print(f"Found: {list(data.keys())}")
            return False
        return True
    
    def __template_metadata__(self):
        splitted = self.template_key.split("_")
        if (len(splitted) != 3):
            print("Format: XXX_XXX_XXX.")
            print(f"Found: {self.template_key}")
            return None
        prefix = splitted[0] + "_" + splitted[1] + "_"
        print(f"Found: {prefix}")
        return {'prefix': prefix, 'class': splitted[0], 'id': splitted[1], 'level': splitted[2]}
    
    def __run_modifier__(self,data):
        assert self.template_metadata != None
        assert self.template_rarity != None and len(self.template_rarity) > 0
        filename = self.template_metadata['class'] + "_" + self.template_metadata['id'] + ".csv"
        modifierDir = self.modifier_folder(self.template_rarity, filename)
        print(f"Processing {modifierDir}")
        modifierData = []
        try:
            with open(modifierDir, "r") as f:
                modifierFile = csv.DictReader(f)
                for each in modifierFile:
                    modifierData.append(each)
        except FileNotFoundError:
            with open(f"./item/" + self.template_rarity + ".csv", "r") as f:
                modifierFile = csv.DictReader(f)
                for each in modifierFile:
                    modifierData.append(each)
        for each in modifierData:
            ITEM_NAME = self.template_metadata['prefix'] + format(int(each['level']), '02')
            result = copy.deepcopy(data[self.template_key])
            result['level'] = int(each['level'])
            for dir in each.keys():
                if (dir == 'level'):
                    continue
                process_template(result, dir, each[dir])
            data[ITEM_NAME] = result
        
    def __run_lambda__(self,data):
        assert self.template_metadata != None
        assert self.template_rarity != None and len(self.template_rarity) > 0
        filename = self.template_metadata['class'] + "_" + self.template_metadata['id'] + ".csv"
        lambdaDir = self.lambda_folder(self.template_rarity, filename)
        print(f"Processing {lambdaDir}")
        lambdaData = []
        with open(lambdaDir, "r") as f:
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
                
    def run(self):
        self.__run__(self.__load__)
        
    def run_target(self, dir):
        def fn():
            return self.__target_load__(dir)
        self.__run__(fn)
    
    def batch_run(self, dir):
        assert dir != None and len(dir) > 0
        now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.result_folder =  lambda rarity: f"./generated/{now}/{rarity}"
        for dirpath, _, filenames in os.walk(dir):
            for filename in filenames:
                if (filename.endswith(".yml") == False):
                    continue
                self.run_target(os.path.join(dirpath, filename))
        
    def __run__(self, loader):
        data = loader()
        templateDigest = self.__digest__(data)
        if not self.__validate_data__(data):
            return
        keys = list(data.keys())
        N = len(keys)
        if (N == 1):
            self.template_key = keys[0]
        elif (N < 1):
            return
        else:
            level1 = ""
            for each in keys:
                if (each.endswith("_01")):
                    level1 = each
                    break
                else:
                    del data[each]
            if len(level1) == 0:
                print("Please put level 1 as a template.")
                print(f"Found: {list(data.keys())}")
                return
            self.template_key = level1
        data[self.template_key]['level'] = 1
        self.template_rarity = self.__parse_rarity__(data)
        self.template_metadata = self.__template_metadata__()
        if (self.template_metadata == None):
            return
        self.identifier = f"{self.template_metadata['class']}_{self.template_metadata['id']}"
        self.__run_modifier__(data)
        self.__run_lambda__(data)
        
        for each in data:
            del data[each]['level']
        
        resultDigest = self.__digest__(data)
        result_file = self.result_folder(self.template_rarity)
        if not os.path.exists(result_file):
            os.makedirs(result_file)
        with open(f"{result_file}/{self.identifier}-{resultDigest['base36']}.yml", "w") as f:
            f.write(f"# Template: {self.identifier}_XXX. Digest: {templateDigest['hex']}. Base36: {templateDigest['base36']}\n")
            f.write(f"# Generated at {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}. Digest: {resultDigest['hex']}. Base36: {resultDigest['base36']}.\n")
            yaml.dump(dict(data), f, sort_keys=False)
            print("Saved to " + result_file)

class Compiler:
    def __init__(self, target_dir):
        assert target_dir != None and len(target_dir) > 0
        self.target_dir = f"./generated/{target_dir}"
        self.config_file = f"./compiler-config.json"
        self.compile_target = lambda digest: f"./generated/compiled/{target_dir}/{digest}"
        with open(self.config_file, "r") as f:
            self.config = json.load(f)
        self.buffer = dict()
        for each in self.config.keys():
            self.buffer[self.config[each]] = {
                "target": each,
                "content": "",
                "digest": ""
            }
    
    def run(self):
        if (not os.path.exists(self.target_dir)):
            print(f"Directory {self.target_dir} is not found.")
            return
        for dirpath, _, filenames in os.walk(self.target_dir):
            if ("compiled" in dirpath):
                continue
            for filename in filenames:
                if (len(filename) < 2 or filename.endswith(".yml") == False):
                    break
                clazz = filename[0] + filename[1]
                clazz = clazz.upper()
                if (clazz not in self.buffer.keys()):
                    print(f"Classification {clazz} not found in mapping.")
                    continue
                filepath = f"{dirpath}/{filename}"
                content = ""
                with open(filepath, "r") as f:
                    for line in f:
                        if line.startswith("# Template:"):
                            pattern = re.compile(r"Digest:\s(.+?)\.\sBase36")
                            m = pattern.search(line)
                            content += "# " + m.group(1) + "\n"
                            self.buffer[clazz]['digest'] += m.group(1) + "@"
                        elif line.startswith("# Generated at"):
                            pattern = re.compile(r"Digest:\s(.+?)\.\sBase36")
                            m = pattern.search(line)
                            content += "# " + m.group(1) + "\n"
                            self.buffer[clazz]['digest'] += m.group(1) + ";"
                        else:
                            content += line
                self.buffer[clazz]["content"] += content
        
        comparer = dict()
        for each in self.buffer.keys():
            comparer[each] = self.buffer[each]['digest']
        digest = hashdigest(comparer)
        compile_dir = self.compile_target(digest['base36'])
        if not os.path.exists(compile_dir):
            os.makedirs(compile_dir)
        
        now = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        for each in self.buffer.keys():
            with open(f"{compile_dir}/{self.buffer[each]['target']}", "w") as f:
                f.write(f"# Compiled at {now}. Digest: {digest['hex']}. Base36: {digest['base36']}.\n\n")
                f.write(self.buffer[each]['content'])
        
        print(f"Result has been saved to {compile_dir}")

class Validator:
    def __init__(self, target_dir):
        assert target_dir != None and len(target_dir) > 0
        self.target_dir = f"./generated/{target_dir}"
        assert os.path.exists(self.target_dir)
    
    def run(self):
        ok = True
        for dirpath, _, filenames in os.walk(self.target_dir):
            if ("compiled" in dirpath):
                continue
            for filename in filenames:
                if not("-" in filename):
                    continue
                splitted = filename.split("-")
                real = splitted[1].replace(".yml","")
                with open(f"{dirpath}/{filename}", "r") as f:
                    data = yaml.safe_load(f)
                digest = hashdigest(data)
                b36 = digest['base36']
                if b36 != real:
                    print(f"MISMATCH\t{filename}\tFound: {real}\tExpected: {b36}")
                    ok = False
                else:
                    print(f"OK\t\t{filename}")
        if ok:
            print("All files are valid.")