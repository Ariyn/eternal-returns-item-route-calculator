import json
import codecs
import math
import enum
from json import JSONEncoder, JSONDecoder 

locations = {}
animals = {}
categories = {}
abilities = {}
items = {}
items_by_level = {0:[], 1:[], 2:[], 3:[], 4:[]}
items_by_category = {}

class DropRatio(enum.Enum):
    Green = enum.auto()
    Blue = enum.auto()
    Red = enum.auto()

DropRatioMap = {
    DropRatio.Green: 75,
    DropRatio.Blue: 50,
    DropRatio.Red: 0,
}

class Location:
    def __init__(self, name, code):
        self.name = name
        self.code = code
        self.items = []
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return f"<({self.code}){self.name}>"

class LocationDrop:
    def __init__(self, location, item, amount):
        self.location = location
        self.amount = amount
        self.item = item
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return f"[{self.location.name} - {self.item.name} - {self.amount}개]"

class Animal:
    def __init__(self, name, code):
        self.name = name
        self.code = code
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return f"<({self.code}){self.name}>"

class AnimalDrop:
    def __init__(self, animal, amount=0, ratio=DropRatio.Red):
        self.animal = animal
        self.amount = amount
        self.ratio = ratio
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        if self.amount != 0:
            return f"[{self.animal.name} - {self.amount}개]"
        else:
            return f"[{self.animal.name} - {DropRatioMap[self.ratio]}%]"

class Ability:
    def __init__(self, typ, effect):
        self.typ = typ
        self.effect = effect

class Item:
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return f"<{self.name}>"

    def __init__(self, item_code="", item=""):
        self.receipe_items = []

        if item_code == "":
            return
        self.name = item[0][0]
        self.name_english = item[0][1]

        self.code = int(item_code)
        self.category = categories[self.code//1000]
        self.level = item[1]
        
        self.is_makable = False
        self.receipe_code = []

        if type(item[2]) == list:
            self.is_makable = True
            self.receipe_code = item[2]
        
        self.abilities = self.parse_ability(item[3])
        self.locations = []
        self.hunts = []

        for i in item[4]:
            if i[0] >= 0:
                self.locations.append(LocationDrop(locations[i[0]], i, i[1]))
            else:
                self.hunts = animal_index(self.code, i[1])
        self.init_dict()
    
    def parse_ability(self, ability):
        abilities = []
        for s in ability.split(",")[:-1]:
            v = s.split(" ")
            abilities.append(Ability(v[0], v[1]))

        return abilities

    def init_dict(self):
        droppable_locations = []
        for l in self.locations:
            droppable_locations.append({
                "code": l.location.code,
                "name": l.location.name,
                "amount": l.amount,
            })

        droppable_animals = []
        for h in self.hunts:
            droppable_animals.append({
                "code": h.animal.code,
                "name": h.animal.name,
                "amount": h.amount,
                "ratio": DropRatioMap[h.ratio],
            })

        abilities = []
        for a in self.abilities:
            abilities.append({
                "type": a.typ,
                "effect": a.effect,
            })

        self.__dict__ = {
            "name":self.name,
            "name_english":self.name_english,
            "code":self.code,
            "category":self.category,
            "level":self.level,
            "is_makable":self.is_makable,
            "receipe_code":self.receipe_code,
            "locations": droppable_locations,
            "animals":droppable_animals,
            "abilities": abilities,
        }
    
    def get_receipe(self, depth=0):
        receipes = set()
        if self.receipe_items != []:
            item_1 = self.receipe_items[0].get_receipe(depth=depth+1)
            item_2 = self.receipe_items[1].get_receipe(depth=depth+1)

            receipes = receipes | item_1 | item_2
        else:
            receipes = set([self])
        
        # if depth == 0:
        #     distinct_locations = []
        #     names = []
        #     for l in locations:
        #         if l.location.name in names:
        #             continue
                
        #         names.append(l.location.name)
        #         distinct_locations.append(l)

        #     locations = distinct_locations
        return receipes
    
    @staticmethod
    def load(item_dict):
        self = Item()
        self.name = item_dict["name"]
        self.code = item_dict["code"]
        self.category = item_dict["category"]
        self.level = item_dict["level"]
        self.is_makable = item_dict["is_makable"]
        self.receipe_code = item_dict["receipe_code"]

        self.locations = []
        for l in item_dict["locations"]:
            self.locations.append(LocationDrop(locations[l["code"]], self, l["amount"]))

        # droppable_animals = []
        # for h in self.hunts:
        #     droppable_animals.append({
        #         "code": h.animal.code,
        #         "name": h.animal.name,
        #         "amount": h.amount,
        #         "ratio": DropRatioMap[h.ratio],
        #     })

        # abilities = []
        # for a in self.abilities:
        #     abilities.append({
        #         "type": a.typ,
        #         "effect": a.effect,
        #     })

        return self

def load_locations():
    global locations
    buffer = codecs.open("locations.json", "r", "utf-8").read()
    location_names = json.loads(buffer)

    for index, name in enumerate(location_names):
        locations[index+1] = Location(name, index+1)

def load_animals():
    global animals
    buffer = codecs.open("animals.json", "r", "utf-8").read()
    animal_names = json.loads(buffer)

    for index, name in enumerate(animal_names):
        animals[index] = Animal(name, index)

def load_abilities():
    global abilities
    buffer = codecs.open("abilities.json", "r", "utf-8").read()
    ability_names = json.loads(buffer)

    for index, name in ability_names.items():
        abilities[index] = name

def load_categories():
    global categories
    buffer = codecs.open("categories.json", "r", "utf-8").read()
    category_names = json.loads(buffer)

    for index, name in category_names.items():
        categories[int(index)] = name
        items_by_category[name] = []

def animal_index(item_code, v):
    indexs = []

    rate = DropRatio.Green
    if item_code in [302111, 401103]:
        rate = DropRatio.Blue
    elif item_code == 302324:
        return [AnimalDrop(animals[6], ratio=DropRatio.Blue)]
    elif item_code == 401403:
        return [AnimalDrop(animals[6], ratio=DropRatio.Blue), AnimalDrop(animals[5], ratio=DropRatio.Green)]
    elif item_code == 401401:
        return [AnimalDrop(animals[6], ratio=DropRatio.Blue), AnimalDrop(animals[5], ratio=DropRatio.Green)]

    for i in range(0, len(animals)):
        if v & (1 << i) != 0:
            indexs.append(AnimalDrop(animals[i], ratio=rate))

    return indexs

def load_mapped_items():
    global items
    buffer = codecs.open("mapped_items.json", "r", "utf-8").read()
    mapped_items = json.loads(buffer)

    for item in mapped_items:
        item = Item.load(item)
        items[item.code] = item

def map_items():
    for item in items.values():
        items_by_level[item.level].append(item)
        items_by_category[item.category].append(item)

        if item.receipe_code != []:
            item.receipe_items = [items[item.receipe_code[0]], items[item.receipe_code[1]]]

        for l in item.locations:
            l.location.items.append(item)

    # for l in locations.values():
    #     print(l)
    #     print(l.items)
    #     print()

def main():
    load_locations()
    load_animals()
    load_categories()
    load_abilities()
    load_mapped_items()

    map_items()

    for i in items_by_category["활"]:
        print(i, i.code)

    print(items[114501].get_receipe())

if __name__ == "__main__":
    main()