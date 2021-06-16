import json
import enum
import codecs

locations = {}
categories = {}
animals = {}
abilities = {}


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
    def __init__(self, location, amount):
        self.location = location
        self.amount = amount

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"[{self.location.name} - {self.amount}개]"


class Animal:
    def __init__(self, name, code):
        self.name = name
        self.code = code

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"<({self.code}){self.name}>"


class Ability:
    def __init__(self, typ, effect):
        self.typ = typ
        self.effect = effect


class Item:
    def __init__(self, item_code="", item=""):
        if item_code == "":
            return
        self.name = item[0][0]
        self.name_english = item[0][1]

        self.code = int(item_code)
        self.category = categories[self.code // 1000]
        self.level = item[1]

        self.is_makable = False
        self.receipe_code = []

        if type(item[2]) == list:
            self.is_makable = True
            self.receipe_code = item[2]

        description = self.parse_description(item[3])
        self.description = description[1]
        self.abilities = self.parse_ability(description[0])
        self.locations = []
        self.hunts = []

        for i in item[4]:
            if i[0] >= 0:
                self.locations.append(LocationDrop(locations[i[0]], i[1]))
            else:
                self.hunts = animal_index(self.code, i[1])
        self.init_dict()

    def parse_description(self, text):
        v = text.split('|', maxsplit=1)
        return v if len(v) > 1 else v + ['']

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
            "name": self.name,
            "name_english": self.name_english,
            "code": self.code,
            "category": self.category,
            "level": self.level,
            "is_makable": self.is_makable,
            "receipe_code": self.receipe_code,
            "locations": droppable_locations,
            "animals": droppable_animals,
            "abilities": abilities,
            "description": self.description,
        }

    @staticmethod
    def load(item_dict):
        self = Item()
        self.name = item_dict["name"]
        self.name_english = item_dict["name_english"]
        self.code = item_dict["code"]
        self.category = item_dict["category"]
        self.level = item_dict["level"]
        self.is_makable = item_dict["is_makable"]
        self.receipe_code = item_dict["receipe_code"]
        self.abilities = item_dict["abilities"]
        self.description = item_dict["description"]

        self.locations = []
        for l in item_dict["locations"]:
            self.locations.append(LocationDrop(locations[l["code"]], l["amount"]))
            # self.locations.append(LocationDrop(locations[l["code"]], self, l["amount"]))

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


def load_locations():
    global locations
    buffer = codecs.open("locations.json", "r", "utf-8").read()
    location_names = json.loads(buffer)

    for index, name in enumerate(location_names):
        locations[index + 1] = Location(name, index + 1)


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


def load_items():
    items = []
    buffer = codecs.open("items.json", "r", "utf-8").read()
    item_datas = json.loads(buffer)

    for key, item in item_datas.items():
        items.append(Item(key, item))

    return items


def load_all():
    load_locations()
    load_animals()
    load_categories()
    load_abilities()
