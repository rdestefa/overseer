# overseer.helpers.json_helpers

import json

# TODO: Make these writes atomic.
# TODO: Enable dynamic folder structure.


def add_user_to_blacklist(user_id: int):
    with open("lists/blacklist.json", "r+") as file:
        file_data = json.load(file)
        file_data["ids"].append(user_id)
        file.seek(0)
        json.dump(file_data, file, indent=2)


def remove_user_from_blacklist(user_id: int):
    with open("lists/blacklist.json", "r+") as file:
        file_data = json.load(file)
        file_data["ids"].remove(user_id)
        file.seek(0)
        json.dump(file_data, file, indent=2)
