import json
import codecs
import sys
import os
from item import load_all, load_items

def __main__():
    load_all()
    items = load_items()

    item_dicts = []
    for item in items:
        item_dicts.append(item.__dict__)
    
    data = json.dumps(item_dicts, ensure_ascii=False)

    codecs.open(os.path.join(sys.path[0], "data/mapped_items.json"), "w", "utf-8").write(data)

if __name__ == "__main__":
    __main__()