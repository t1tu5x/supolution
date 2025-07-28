# soup_game.py

import json
import random
from datetime import datetime

class SoupGame:
    def __init__(self):
        self.start_time = datetime.now()
        self.turn = 0
        self.resources = {"белки": 5, "жиры": 5, "углеводы": 5}
        self.tech = []
        self.hp = 100
        self.max_turns = 30
        self.status = "alive"
        self.upgrades = []
        self.load_upgrades()

    def load_upgrades(self):
        try:
            with open("data/upgrades.json", "r", encoding="utf-8") as f:
                self.upgrades = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.upgrades = [{
                "name": "Ошибка загрузки",
                "desc": "Проверь файл data/upgrades.json",
                "bonus": {"белки": 0}
            }]

    def next_turn(self):
        if self.status != "alive":
            return

        self.turn += 1
        self.hp -= random.randint(1, 5)

        for k in self.resources:
            прирост = random.randint(1, 3)
            self.resources[k] = max(0, self.resources[k] + прирост)

        if self.turn >= self.max_turns or self.hp <= 0:
            self.status = "flushed"

    def get_upgrade_choices(self):
        доступные = [u for u in self.upgrades if u["name"] not in self.tech]
        if not доступные:
            return []
        return random.sample(доступные, min(3, len(доступные)))

    def apply_upgrade(self, upgrade_name):
        найденный = next((u for u in self.upgrades if u["name"] == upgrade_name), None)
        if not найденный:
            return False

        for k, v in найденный.get("bonus", {}).items():
            if k in self.resources:
                self.resources[k] += v

        self.tech.append(найденный["name"])

        if найденный.get("win"):
            self.status = "ascended"

        return True

    def get_state(self):
        return {
            "turn": self.turn,
            "resources": dict(self.resources),
            "tech": list(self.tech),
            "hp": self.hp,
            "status": self.status
        }
