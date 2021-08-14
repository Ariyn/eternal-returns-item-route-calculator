import json
import codecs
import sys
import os
from item import Item, load_all, categories, abilities

items = {}
items_by_name = {}
items_by_level = {0:[], 1:[], 2:[], 3:[], 4:[]}
items_by_category = {}

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

def main():
    load_all()
    load_mapped_items()
    map_items()
    str = input('아이템을 입력하시오 :')
    
    print_item_tree(str)

if __name__ == "__main__":
    main()