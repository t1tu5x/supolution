 ✅ soup_game.py — с поддержкой DLC-фракций, тем, сохранения и квестов

import json
import random
from datetime import datetime

class SoupGame:
    def __init__(self, dlc_enabled=True):
        self.turn = 0
        self.hp = 100
        self.max_turns = 40
        self.status = "alive"

        self.resources = {"белки": 5, "жиры": 5, "углеводы": 5}
        self.tech = []
        self.structures = []
        self.events_log = []
        self.upgrades = self.load_json("data/upgrades.json")
        self.events = self.load_json("data/events.json")
        self.choices = self.load_json("data/choices.json")
        self.quests = self.load_json("data/quests.json")
        self.quest_progress = {}

        self.factions = {
            "Грибной Ковен": 0,
            "Картофельный Фронт": 0,
            "Орден Бульона": 0,
            "Слизистая Демократия": 0
        }

        self.current_choice = None
        self.resolved_choices = set()
        self.unlocked_themes = ["Классика"]

        if dlc_enabled:
            for dlc in self.load_json("data/factions_dlc.json"):
                self.factions[dlc["name"]] = dlc.get("starting_reputation", 0)

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

        for key in self.resources:
            прирост = random.randint(0, 2)
            if "Ферментатор" in self.structures:
                прирост += 1
            self.resources[key] = max(0, self.resources[key] + прирост)

        if random.random() < 0.4:
            self.trigger_random_event()

        self.update_quests()

        if self.turn >= self.max_turns or self.hp <= 0:
            self.status = "flushed"

        if (
            all(v >= 5 for v in self.factions.values()) and
            "Супознание" in self.tech and
            "Храм Ложки" in self.structures
        ):
            self.status = "ascended"

        self.maybe_trigger_choice()

    def get_upgrade_choices(self):
        доступные = [u for u in self.upgrades if u["name"] not in self.tech]
        return random.sample(доступные, min(3, len(доступные)))

    def apply_upgrade(self, upgrade_name):
        найден = next((u for u in self.upgrades if u["name"] == upgrade_name), None)
        if not найден:
            return False

        for k, v in найден.get("bonus", {}).items():
            if k in self.resources:
                self.resources[k] += v

        if "structure" in найден:
            self.structures.append(найден["structure"])

        for faction, shift in найден.get("factions", {}).items():
            if faction in self.factions:
                self.factions[faction] += shift

        self.tech.append(найден["name"])

        if найден.get("win"):
            self.status = "ascended"

        if upgrade_name == "Супознание" and "Томатный апокалипсис" not in self.unlocked_themes:
            self.unlocked_themes.append("Томатный апокалипсис")

        return True

    def trigger_random_event(self):
        if not self.events:
            return
        event = random.choice(self.events)
        self.events_log.append(event["text"])

        effect = event.get("effect", {})
        for key, val in effect.get("resources", {}).items():
            if key in self.resources:
                self.resources[key] = max(0, self.resources[key] + val)

        for faction, shift in effect.get("factions", {}).items():
            if faction in self.factions:
                self.factions[faction] += shift

        if "hp" in effect:
            self.hp = max(0, self.hp + effect["hp"])

        if effect.get("death") is True:
            self.status = "flushed"

    def maybe_trigger_choice(self):
        if self.turn % 5 == 0 and self.current_choice is None:
            available = [c for c in self.choices if c["id"] not in self.resolved_choices]
            if available:
                self.current_choice = random.choice(available)

    def resolve_choice(self, answer: str):
        if not self.current_choice:
            return

        effects = self.current_choice.get(answer, {})

        for k, v in effects.get("resources", {}).items():
            if k in self.resources:
                self.resources[k] += v

        for f, delta in effects.get("factions", {}).items():
            if f in self.factions:
                self.factions[f] += delta

        if "hp" in effects:
            self.hp += effects["hp"]

        self.resolved_choices.add(self.current_choice["id"])
        self.current_choice = None

        if self.hp <= 0:
            self.status = "flushed"

    def update_quests(self):
        for q in self.quests:
            qid = q["id"]
            stage = self.quest_progress.get(qid, 0)
            if stage < len(q["stages"]):
                req = q["stages"][stage]["require"]
                if all(self.resources.get(k, 0) >= v for k, v in req.get("resources", {}).items()):
                    self.quest_progress[qid] = stage + 1
                    self.events_log.append(f"🧭 Квест продвинулся: {q['name']} — этап {stage+1}")
                    for key, val in q["stages"][stage].get("reward", {}).get("resources", {}).items():
                        self.resources[key] += val

    def get_state(self):
        return {
            "turn": self.turn,
            "resources": dict(self.resources),
            "tech": list(self.tech),
            "hp": self.hp,
            "status": self.status,
            "factions": dict(self.factions),
            "structures": list(self.structures),
            "events_log": list(self.events_log[-5:]),
            "current_choice": self.current_choice,
            "unlocked_themes": list(self.unlocked_themes),
            "quest_progress": self.quest_progress
        }

    def to_dict(self):
        return {
            "turn": self.turn,
            "hp": self.hp,
            "status": self.status,
            "resources": self.resources,
            "tech": self.tech,
            "structures": self.structures,
            "factions": self.factions,
            "events_log": self.events_log,
            "resolved_choices": list(self.resolved_choices),
            "current_choice_id": self.current_choice["id"] if self.current_choice else None,
            "unlocked_themes": list(self.unlocked_themes),
            "quest_progress": self.quest_progress
        }

    def load_state(self, data):
        self.turn = data["turn"]
        self.hp = data["hp"]
        self.status = data["status"]
        self.resources = data["resources"]
        self.tech = data["tech"]
        self.structures = data["structures"]
        self.factions = data["factions"]
        self.events_log = data["events_log"]
        self.resolved_choices = set(data.get("resolved_choices", []))
        self.unlocked_themes = list(data.get("unlocked_themes", ["Классика"]))
        self.quest_progress = data.get("quest_progress", {})

        if data.get("current_choice_id"):
            self.current_choice = next(
                (c for c in self.choices if c["id"] == data["current_choice_id"]),
                None
            )
        else:
            self.current_choice = None
