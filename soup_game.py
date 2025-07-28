# ✅ soup_game.py — редизайн ядра: ресурсы, фракции, взаимосвязи, логика

import json
import random
import math

class SoupGame:
    def __init__(self, dlc_enabled=True):
        self.turn = 0
        self.hp = 100
        self.max_turns = 50
        self.status = "alive"

        # 🎯 Ресурсы с чёткой функцией и физикой
        self.resources = {
            "белки": 5,     # Рост тканей, восстановление HP
            "жиры": 5,      # Теплоизоляция, защита от урона
            "углеводы": 5,  # Энергия, расходуется каждый ход
            "минералы": 5   # Катализаторы для технологий и дипломатии
        }

        self.metabolism_rate = 3  # сколько углеводов нужно в ход для поддержания стабильности
        self.temp_stability = 0   # показатель перегрева или охлаждения

        self.tech = []
        self.structures = []
        self.events_log = []
        self.quest_progress = {}

        self.upgrades = self.load_json("data/upgrades.json")
        self.tech_tree = self.load_json("data/tech_tree.json")
        self.events = self.load_json("data/events.json")
        self.choices = self.load_json("data/choices.json")
        self.quests = self.load_json("data/quests.json")

        # 🤝 Фракции с лояльностью и стратегией
        self.factions = {
            "Сливочные Пельмешки": 0,
            "Горошковое Веселье": 0,
            "Орден Хрустящих Сухариков": 0,
            "Мармеладные Мыслители": 0
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

        # 📉 Энергозатраты: если углеводов не хватает — штраф
        if self.resources["углеводы"] < self.metabolism_rate:
            deficit = self.metabolism_rate - self.resources["углеводы"]
            self.hp -= deficit * 3
            self.temp_stability += deficit
            self.events_log.append(f"⚡ Энергетическое истощение: нехватка углеводов на {deficit} → HP −{deficit * 3}")
            self.resources["углеводы"] = 0
        else:
            self.resources["углеводы"] -= self.metabolism_rate

        # 🔥 Нестабильность температуры влияет на жиры и HP
        if self.temp_stability > 3:
            damage = self.temp_stability - 2
            self.hp -= damage
            self.events_log.append(f"🥵 Перегрев! Потеряно HP −{damage}")
        elif self.temp_stability < -3:
            self.hp -= 2
            self.events_log.append("🥶 Переохлаждение супа: HP −2")

        # 📈 Прирост ресурсов зависит от технологий и фракций
        for res in self.resources:
            gain = 1
            if res == "белки" and "Аминогенез" in self.tech:
                gain += 1
            if res == "углеводы" and "Ферментация" in self.structures:
                gain += 1
            if res == "минералы" and self.factions["Мармеладные Мыслители"] >= 3:
                gain += 1
            self.resources[res] += gain

        # 🏛️ Влияние фракций
        for name, rep in self.factions.items():
            if rep <= -3 and random.random() < 0.3:
                self.hp -= 3
                self.events_log.append(f"⚔️ {name} атаковали суп! HP −3")
            if rep >= 4 and random.random() < 0.3:
                self.resources[random.choice(list(self.resources))] += 2
                self.events_log.append(f"🎁 {name} прислали помощь!")

        if random.random() < 0.4:
            self.trigger_random_event()

        self.update_quests()
        self.maybe_trigger_choice()

        if self.hp <= 0 or self.turn >= self.max_turns:
            self.status = "flushed"

        if all(v >= 6 for v in self.factions.values()) and "Супознание" in self.tech:
            self.status = "ascended"

    def tech_requirements_met(self, upgrade_name):
        required = self.tech_tree.get(upgrade_name, [])
        return all(t in self.tech for t in required)

    def get_upgrade_choices(self):
        доступные = [u for u in self.upgrades if u["name"] not in self.tech and self.tech_requirements_met(u["name"])]
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
        if self.turn % 4 == 0 and self.current_choice is None:
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
                    self.events_log.append(f"🌟 Квест " + q['name'] + f" — этап {stage+1} пройден!")
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
