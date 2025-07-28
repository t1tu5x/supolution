# soup_game.py — с жертвами и синергией технологий

import json

class SoupGame:
    def __init__(self):
        self.turn = 1
        self.hp = 100
        self.max_turns = 100
        self.resources = {"вода": 100, "жар": 50, "жир": 75, "нутриенты": 120, "белки": 0, "углеводы": 0}
        self.factions = {"овощи": 0, "специи": 0, "мясо": 0, "Грибной Ковен": 0, "Картофельный Фронт": 0, "Орден Бульона": 0, "Слизистая Демократия": 0}
        self.structures = []
        self.tech = []
        self.quest_progress = {}
        self.events_log = []
        self.current_choice = None

        with open("data/tech_tree.json", "r", encoding="utf-8") as f:
            self.tech_tree = json.load(f)
        try:
            with open("data/tech_synergies.json", "r", encoding="utf-8") as f:
                self.tech_synergies = json.load(f)
        except:
            self.tech_synergies = []
        try:
            with open("data/upgrades.json", "r", encoding="utf-8") as f:
                self.upgrades_data = {u["name"]: u for u in json.load(f)}
        except:
            self.upgrades_data = {}

    def get_state(self):
        return {
            "turn": self.turn,
            "hp": self.hp,
            "resources": self.resources,
            "factions": self.factions,
            "structures": self.structures,
            "tech": self.tech,
            "quest_progress": self.quest_progress,
            "events_log": self.events_log,
            "current_choice": self.current_choice
        }

    def to_dict(self):
        return self.get_state()

    def load_state(self, data):
        self.__dict__.update(data)

    def get_upgrade_choices(self):
        available = []
        for tech, deps in self.tech_tree.items():
            if tech not in self.tech and all(d in self.tech for d in deps):
                entry = {"name": tech, "desc": self.upgrades_data.get(tech, {}).get("desc", "")}
                entry["cost"] = self.upgrades_data.get(tech, {}).get("cost", [])
                available.append(entry)
        return available

    def can_afford(self, tech_name):
        data = self.upgrades_data.get(tech_name, {})
        for c in data.get("cost", []):
            if c["type"] in self.resources:
                if self.resources.get(c["type"], 0) < c["amount"]:
                    return False
            elif c["type"] == "faction":
                if self.factions.get(c["target"], 0) < abs(c["amount"]):
                    return False
        return True

    def apply_upgrade_cost(self, tech_name):
        data = self.upgrades_data.get(tech_name, {})
        for c in data.get("cost", []):
            if c["type"] in self.resources:
                self.resources[c["type"]] -= c["amount"]
            elif c["type"] == "faction":
                self.factions[c["target"]] += c["amount"]
        self.events_log.append(f"🎯 Потрачено на {tech_name}")

    def apply_upgrade(self, tech_name):
        if not self.can_afford(tech_name):
            self.events_log.append(f"❌ Недостаточно ресурсов для {tech_name}")
            return
        self.apply_upgrade_cost(tech_name)
        self.tech.append(tech_name)
        self.events_log.append(f"🔬 Изучена технология: {tech_name}")

        # применить бонус
        data = self.upgrades_data.get(tech_name, {})
        for k, v in data.get("bonus", {}).items():
            self.resources[k] += v
        for f, v in data.get("factions", {}).items():
            self.factions[f] += v
        if data.get("win"):
            self.events_log.append("🏆 Победа: суп достиг осознания!")

    def trigger_tech_effects(self, tech_name):
        pass

    def check_synergies(self):
        active = set(self.tech)
        for entry in self.tech_synergies:
            combo = set(entry["combo"])
            if combo.issubset(active):
                effect = entry["effect"]
                label = effect["name"]
                self.events_log.append(f"🧪 Активирована синергия: {label}")
                for key, val in effect.get("bonus", {}).items():
                    if key in self.resources:
                        self.resources[key] += int(self.resources[key] * val)
                for fac, delta in effect.get("factions", {}).items():
                    if fac in self.factions:
                        self.factions[fac] += delta

    def next_turn(self):
        self.turn += 1
        if self.turn >= self.max_turns:
            self.events_log.append("🏁 Игра завершена по времени.")
