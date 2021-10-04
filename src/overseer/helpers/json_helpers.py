# overseer.helpers.json_helpers

import json

# TODO: Make these writes atomic.
# TODO: Enable dynamic folder structure.


def add_user_to_blacklist(user_id: int):
    with open("lists/blacklist.json", "r") as file:
        blacklist = json.load(file)

    blacklist["ids"].append(user_id)

    with open("lists/blacklist.json", "w") as file:
        json.dump(blacklist, file, indent=2)


def remove_user_from_blacklist(user_id: int):
    with open("lists/blacklist.json", "r") as file:
        blacklist = json.load(file)

    blacklist["ids"].remove(user_id)

    with open("lists/blacklist.json", "w") as file:
        json.dump(blacklist, file, indent=2)
