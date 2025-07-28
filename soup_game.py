import json
import random

class SoupGame:
    def __init__(self):
        self.turn = 0
        self.hp = 100
        self.max_turns = 50
        self.status = "alive"

        self.resources = {
            "белки": 5,
            "жиры": 5,
            "углеводы": 5,
            "минералы": 5,
            "жар": 5,
            "вода": 5
        }

        self.tech = []
        self.structures = []
        self.events_log = []
        self.quest_progress = {}
        self.flags = {}
        self.factions = {
            "Сливочные Пельмешки": 0,
            "Горошковое Веселье": 0,
            "Орден Хрустящих Сухариков": 0
        }

        self.upgrades = self.load_json("data/upgrades.json")
        self.tech_tree = self.load_json("data/tech_tree.json")
        self.choices = self.load_json("data/choices.json")
        self.quests = self.load_json("data/quests.json")
        self.current_choice = None
        self.resolved_choices = set()

    def load_json(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []

    def get_state(self):
        return {
            "turn": self.turn,
            "hp": self.hp,
            "status": self.status,
            "resources": self.resources,
            "tech": self.tech,
            "structures": self.structures,
            "events_log": self.events_log[-10:],
            "factions": self.factions,
            "quest_progress": self.quest_progress,
            "current_choice": self.current_choice
        }

    def to_dict(self):
        return self.__dict__

    def load_state(self, data):
        self.__dict__.update(data)

    def next_turn(self):
        self.turn += 1
        self.update_quests()

    def get_upgrade_choices(self):
        return random.sample(
            [u for u in self.upgrades if u["name"] not in self.tech],
            min(3, len(self.upgrades))
        )

    def apply_upgrade(self, name):
        tech = next((u for u in self.upgrades if u["name"] == name), None)
        if not tech:
            return
        self.tech.append(name)
        for k, v in tech.get("bonus", {}).items():
            if k in self.resources:
                self.resources[k] += v
        for f, d in tech.get("factions", {}).items():
            if f in self.factions:
                self.factions[f] += d
        if "structure" in tech:
            self.structures.append(tech["structure"])
        self.events_log.append(f"🔬 Исследована технология: {name}")

    def trigger_tech_effects(self, name):
        if name == "Сердце Супознания":
            self.flags["awakened"] = True
            self.events_log.append("✨ Суп достиг сознания!")

    def choice_impact(self, cid, answer):
        if cid == "pea_fight" and answer == "no":
            self.factions["Горошковое Веселье"] -= 5
            self.events_log.append("⚠️ Горошек обиделся.")
        if cid == "lid_melody" and answer == "yes":
            self.flags["lid_opened"] = True
            self.events_log.append("🎵 Крышка открылась от звука!")

    def resolve_choice(self, answer):
        if not self.current_choice:
            return
        effects = self.current_choice.get(answer, {})
        for r, v in effects.get("resources", {}).items():
            if r in self.resources:
                self.resources[r] += v
        for f, d in effects.get("factions", {}).items():
            if f in self.factions:
                self.factions[f] += d
        self.resolved_choices.add(self.current_choice["id"])
        self.current_choice = None

    def update_quests(self):
        for quest in self.quests:
            qid = quest["id"]
            stage = self.quest_progress.get(qid, 0)
            if stage >= len(quest["stages"]):
                continue
            req = quest["stages"][stage].get("require", {})
            if self._requirements_met(req):
                self.quest_progress[qid] = stage + 1
                self._apply_reward(quest["stages"][stage].get("reward", {}))
                self.events_log.append(f"📖 Квест '{quest['name']}': этап {stage + 1} завершён!")

    def _requirements_met(self, req):
        for r, v in req.items():
            if r == "tech":
                if v not in self.tech:
                    return False
            elif r in self.resources:
                if self.resources[r] < v:
                    return False
        return True

    def _apply_reward(self, reward):
        for r, v in reward.get("resources", {}).items():
            if r in self.resources:
                self.resources[r] += v
        for f, d in reward.get("factions", {}).items():
            if f == "Все":
                for fac in self.factions:
                    self.factions[fac] += d
            elif f in self.factions:
                self.factions[f] += d
        if "tech" in reward and reward["tech"] not in self.tech:
            self.tech.append(reward["tech"])
            self.events_log.append(f"🧠 Открыта технология: {reward['tech']}")
