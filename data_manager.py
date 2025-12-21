import json
import os
import atexit
from constants import *

def load_high_score():
    global global_high_score

    if not os.path.exists(HIGH_SCORE_FILE):
        global_high_score = 0
        return 0

    file = open(HIGH_SCORE_FILE, 'r', encoding='utf-8')
    content = file.read()
    file.close()

    if not content.strip():
        global_high_score = 0
        return 0

    data = json.loads(content)

    if isinstance(data, dict) and "high_score" in data:
        global_high_score = data["high_score"]
        return global_high_score

    global_high_score = 0
    return 0

def load_money_score():
    global global_money_score
    if not os.path.exists(MONEY_SCORE_FILE):
        global_money_score = 0
        return 0
    file = open(MONEY_SCORE_FILE, 'r', encoding='utf-8')
    content = file.read()
    file.close()

    if not content.strip():
        global_money_score = 0
        return 0
    data = json.loads(content)

    if isinstance(data, dict) and "money_score" in data:
        global_money_score = data["money_score"]
        return global_money_score

    global_money_score = 0
    return 0

def save_high_score():
    global global_high_score, score_updated

    if not score_updated:
        return

    data = {"high_score": int(global_high_score)}
    file = open(HIGH_SCORE_FILE, 'w', encoding='utf-8')
    json.dump(data, file, ensure_ascii=False, indent=4)
    file.close()

    score_updated = False

def save_money_score():
    global global_money_score, money_updated

    if not money_updated:
        return
    data = {"money_score": int(global_money_score)}
    file = open(MONEY_SCORE_FILE, 'w', encoding='utf-8')
    json.dump(data, file, ensure_ascii=False, indent=4)
    file.close()

    money_updated = False

def update_high_score(new_score):
    global global_high_score, score_updated, new_record_achieved

    if new_score > global_high_score:
        global_high_score = int(new_score)
        score_updated = True
        new_record_achieved = True
        save_high_score()

    return global_high_score

def update_money_score(new_money_score):
    global global_money_score, money_updated

    global_money_score = int(new_money_score)
    money_updated = True
    save_money_score()

    return global_money_score

def load_shop_data():
    if not os.path.exists(SHOP_DATA_FILE):
        initial_data = {
            "purchased_items": [],
            "coins": 0,
            "selected_accessory": 0
        }
        save_shop_data(initial_data)
        return initial_data

    file = open(SHOP_DATA_FILE, 'r', encoding='utf-8')
    content = file.read()
    file.close()

    if not content.strip():
        data = {
            "purchased_items": [],
            "coins": 0,
            "selected_accessory": 0
        }
        return data

    data = json.loads(content)

    if not isinstance(data, dict):
        data = {
            "purchased_items": [],
            "coins": 0,
            "selected_accessory": 0
        }
    else:
        if "purchased_items" not in data:
            data["purchased_items"] = []
        if "coins" not in data:
            data["coins"] = 0
        if "selected_accessory" not in data:
            data["selected_accessory"] = 0

    return data

def save_shop_data(data):
    file = open(SHOP_DATA_FILE, 'w', encoding='utf-8')
    json.dump(data, file, ensure_ascii=False, indent=4)
    file.close()
    return True

def save_game_state(menu, selected_accessory):
    shop_data = {
        "purchased_items": list(menu.purchased_items),
        "coins": menu.coins,
        "selected_accessory": selected_accessory
    }
    save_shop_data(shop_data)
    save_high_score()
    save_money_score()

atexit.register(save_high_score)
atexit.register(save_money_score)