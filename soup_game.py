# soup_game.py

import json
import random
from datetime import datetime

class SoupGame:
    def __init__(self):
        self.turn = 0
        self.hp = 100
        self.max_turns = 40
        self.status = "alive"

        # Основные показатели
        self.resources = {"белки": 5, "жиры": 5, "углеводы": 5}
        self.tech = []
        self.events_log = []
        self.structures = []

        # Фракции и репутация
        self.factions = {
            "Грибной Ковен": 0,
            "Картофельный Фронт": 0,
            "Орден Бульона": 0,
            "Слизистая Демократия": 0
        }

        # Загрузка апгрейдов и событий
        self.upgrades = self.load_json("data/upgrades.json")
        self.events = self.load_json("data/events.json")

    def load_json(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []

    def next_turn(self):
        if self.status != "alive":
            return

        self.turn += 1
        self.hp -= random.randint(1, 4)

        # Прирост ресурсов (связан с постройками и технологиями)
        for key in self.resources:
            base = random.randint(0, 2)
            if "Ферментатор" in self.structures:
                base += 1
            self.resources[key] = max(0, self.resources[key] + base)

        # Рандом-событие
        if random.random() < 0.4:
            self.trigger_random_event()

        # Проверка условий проигрыша
        if self.turn >= self.max_turns or self.hp <= 0:
            self.status = "flushed"

        # Условие победы: 3 фракции уважают тебя + 1 мегапроект
        if (
            all(v >= 5 for v in self.factions.values()) and
            "Супознание" in s
