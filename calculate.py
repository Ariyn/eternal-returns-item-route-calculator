import json
import codecs
import sys
import os
# import math
# import enum
# from json import JSONEncoder, JSONDecoder 
from item import Item, load_all, categories, abilities

# locations = {}
# animals = {}
# categories = {}
# abilities = {}
items = {}
items_by_name = {}
items_by_level = {0:[], 1:[], 2:[], 3:[], 4:[]}
items_by_category = {}

#     @staticmethod
#     def load(item_dict):
#         self = Item()
#         self.name = item_dict["name"]
#         self.name_english = item_dict["name_english"]
#         self.code = item_dict["code"]
#         self.category = item_dict["category"]
#         self.level = item_dict["level"]
#         self.is_makable = item_dict["is_makable"]
#         self.receipe_code = item_dict["receipe_code"]
#         self.abilities = item_dict["abilities"]
#         self.description = item_dict["description"]

#         self.locations = []
#         for l in item_dict["locations"]:
#             self.locations.append(LocationDrop(locations[l["code"]], self, l["amount"]))

#         # droppable_animals = []
#         # for h in self.hunts:
#         #     droppable_animals.append({
#         #         "code": h.animal.code,
#         #         "name": h.animal.name,
#         #         "amount": h.amount,
#         #         "ratio": DropRatioMap[h.ratio],
#         #     })

#         # abilities = []
#         # for a in self.abilities:
#         #     abilities.append({
#         #         "type": a.typ,
#         #         "effect": a.effect,
#         #     })

#         return self

# def load_locations():
#     global locations
#     buffer = codecs.open("locations.json", "r", "utf-8").read()
#     location_names = json.loads(buffer)

#     for index, name in enumerate(location_names):
#         locations[index+1] = Location(name, index+1)

# def load_animals():
#     global animals
#     buffer = codecs.open("animals.json", "r", "utf-8").read()
#     animal_names = json.loads(buffer)

#     for index, name in enumerate(animal_names):
#         animals[index] = Animal(name, index)

# def load_abilities():
#     global abilities
#     buffer = codecs.open("abilities.json", "r", "utf-8").read()
#     ability_names = json.loads(buffer)

#     for index, name in ability_names.items():
#         abilities[index] = name

# def load_categories():
#     global categories
#     buffer = codecs.open("categories.json", "r", "utf-8").read()
#     category_names = json.loads(buffer)

#     for index, name in category_names.items():
#         categories[int(index)] = name
#         items_by_category[name] = []

# def animal_index(item_code, v):
#     indexs = []

#     rate = DropRatio.Green
#     if item_code in [302111, 401103]:
#         rate = DropRatio.Blue
#     elif item_code == 302324:
#         return [AnimalDrop(animals[6], ratio=DropRatio.Blue)]
#     elif item_code == 401403:
#         return [AnimalDrop(animals[6], ratio=DropRatio.Blue), AnimalDrop(animals[5], ratio=DropRatio.Green)]
#     elif item_code == 401401:
#         return [AnimalDrop(animals[6], ratio=DropRatio.Blue), AnimalDrop(animals[5], ratio=DropRatio.Green)]

#     for i in range(0, len(animals)):
#         if v & (1 << i) != 0:
#             indexs.append(AnimalDrop(animals[i], ratio=rate))

#     return indexs

def load_mapped_items():
    global items
    global items_by_name
    global items_by_category

    buffer = codecs.open(os.path.join(sys.path[0], "data/mapped_items.json"), "r", "utf-8").read()
    mapped_items = json.loads(buffer)

    for item in mapped_items:
        item = Item.load(item)
        items[item.code] = item
        items_by_name[item.name] = item

    for cat in categories.values():
        items_by_category[cat] = []

def map_items():
    for item in items.values():
        items_by_level[item.level].append(item)
        items_by_category[item.category].append(item)

        if item.receipe_code != []:
            item.receipe_items = [items[item.receipe_code[0]], items[item.receipe_code[1]]]

        for l in item.locations:
            l.location.items.append(item)

def print_item_tree(name):
    item = None
    try:
        item = items_by_name[name].__dict__
    except KeyError:
        import sys
        print(f"존재하지 않는 아이템입니다. - {name}", file=sys.stderr)
        return

    item_name = item['name']
    print(f"{item_name} Lv.{item['level']} [{item['category']}]")

    ability_text = []
    for ability in item['abilities']:
        ability_text.append(f"{abilities[ability['type']]} {ability['effect']}")
    print(f"{', '.join(ability_text)}{item['description']}")

    print()

    for subitem in item['receipe_items']:
        print_subitem_tree(subitem.__dict__['name'])


def print_subitem_tree(name):
    item = items_by_name[name].__dict__

    location_text = ''
    if item['level'] == 0 and item['locations']:
        location_list = []
        for loc in item['locations']:
            location_list.append(loc.location.name)
        location_text = f" ({', '.join(location_list)})"

    print(f"{item['name']} Lv.{item['level']}{location_text}")

    if 'receipe_items' in item:
        for subitem in item['receipe_items']:
            print_subitem_tree(subitem.__dict__['name'])

    # for l in locations.values():
    #     print(l)
    #     print(l.items)
    #     print()

def main():
    load_all()
    # load_locations()
    # load_animals()
    # load_categories()
    # load_abilities()
    load_mapped_items()
    map_items()

    # for i in items_by_category["활"]:
    #     print(i, i.code)

    # print(items[114501].get_receipe())
    #print(items[201404].__dict__)
    str = input('아이템을 입력하시오 :')
    
    print_item_tree(str)

if __name__ == "__main__":
    main()