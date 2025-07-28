import json
import random

class SoupGame:
    def __init__(self, dlc_enabled=True):
        self.turn = 0
        self.hp = 100
        self.max_turns = 50
        self.status = "alive"

        self.resources = {
            "белки": 5,       # восстановление и рост
            "жиры": 5,        # теплоизоляция, броня
            "углеводы": 5,    # энергия
            "минералы": 5     # катализатор технологий и дипломатии
        }
        self.metabolism_rate = 3
        self.temp_stability = 0

        self.tech = []
        self.structures = []
        self.events_log = []
        self.quest_progress = {}
        self.flags = {}

        self.factions = {
            "Сливочные Пельмешки": 0,
            "Горошковое Веселье": 0,
            "Орден Хрустящих Сухариков": 0,
            "Мармеладные Мыслители": 0
        }

        self.current_choice = None
        self.resolved_choices = set()
        self.unlocked_themes = ["Классика"]
        self.active_crisis = None

        self.upgrades = self.load_json("data/upgrades.json")
        self.tech_tree = self.load_json("data/tech_tree.json")
        self.events = self.load_json("data/events.json")
        self.choices = self.load_json("data/choices.json")
        self.quests = self.load_json("data/quests.json")

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
        if self.status != "alive": return
        self.turn += 1

        # Энергетика и метаболизм
        if self.resources["углеводы"] < self.metabolism_rate:
            deficit = self.metabolism_rate - self.resources["углеводы"]
            self.hp -= deficit * 3
            self.temp_stability += deficit
            self.resources["углеводы"] = 0
            self.events_log.append(f"⚡ Энергетический дефицит: −{deficit * 3} HP")
        else:
            self.resources["углеводы"] -= self.metabolism_rate

        # Температурная стабильность (зависит от жиров)
        if self.temp_stability > 3:
            self.hp -= 2
            self.events_log.append("🥵 Перегрев супа: HP −2")
        elif self.temp_stability < -3:
            self.hp -= 2
            self.events_log.append("🥶 Замерзание супа: HP −2")

        # Прирост ресурсов (учитывает технологии)
        for k in self.resources:
            gain = 1
            if k == "белки" and "Аминогенез" in self.tech:
                gain += 1
            if k == "минералы" and self.factions["Мармеладные Мыслители"] >= 3:
                gain += 1
            self.resources[k] += gain

        # Фракции — атаки / помощь
        for f, rep in self.factions.items():
            if rep <= -3 and random.random() < 0.3:
                self.hp -= 3
                self.events_log.append(f"⚔️ {f} атакуют! HP −3")
            if rep >= 4 and random.random() < 0.3:
                boost = random.choice(list(self.resources))
                self.resources[boost] += 2
                self.events_log.append(f"🎁 {f} помогли: {boost} +2")

        # Кризис фракции
        if self.turn % 6 == 0 and not self.active_crisis:
            hostile = [f for f, r in self.factions.items() if r <= -4]
            if hostile:
                self.active_crisis = random.choice(hostile)
                self.events_log.append(f"💢 {self.active_crisis} требуют минералы!")

        if random.random() < 0.4:
            self.trigger_random_event()

        self.update_quests()
        self.maybe_trigger_choice()

        if self.hp <= 0 or self.turn >= self.max_turns:
            self.status = "flushed"
        if all(r >= 6 for r in self.factions.values()) and "Супознание" in self.tech:
            self.status = "ascended"

    def resolve_crisis(self, accept):
        if not self.active_crisis: return
        if accept:
            self.resources["минералы"] = max(0, self.resources["минералы"] - 3)
            self.factions[self.active_crisis] += 2
            self.events_log.append(f"🤝 {self.active_crisis}: выдали минералы −3")
        else:
            self.hp -= 5
            self.factions[self.active_crisis] -= 1
            self.events_log.append(f"🚫 {self.active_crisis}: отказ! HP −5")
        self.active_crisis = None

    def get_upgrade_choices(self):
        return random.sample(
            [u for u in self.upgrades if u["name"] not in self.tech and self.tech_requirements_met(u["name"])],
            min(3, len(self.upgrades))
        )

    def tech_requirements_met(self, upgrade_name):
        required = self.tech_tree.get(upgrade_name, [])
        return all(t in self.tech for t in required)

    def apply_upgrade(self, name):
        u = next((x for x in self.upgrades if x["name"] == name), None)
        if not u: return False
        for r, v in u.get("bonus", {}).items():
            if r in self.resources:
                self.resources[r] += v
        if "structure" in u:
            self.structures.append(u["structure"])
        for f, shift in u.get("factions", {}).items():
            if f in self.factions:
                self.factions[f] += shift
        self.tech.append(u["name"])
        if u.get("win"): self.status = "ascended"
        return True

    def trigger_tech_effects(self, name):
        if name == "Супознание":
            self.flags["awakened"] = True
            self.events_log.append("🔬 Суп обрел сознание!")
        if name == "Ферментатор 2.0":
            self.structures.append("Брожение++")
            self.events_log.append("🧪 Установлен Ферментатор 2.0")

    def choice_impact(self, cid, answer):
        if cid == "invite_pelmeshki" and answer == "no":
            self.flags["pelmeshki_ignored"] = True
            self.factions["Сливочные Пельмешки"] -= 1
            self.events_log.append("⚠️ Пельмешки обиделись.")
        if cid == "toast_fight" and answer == "yes":
            self.flags["toast_war"] = True
            self.events_log.append("🔥 Объявлена война сухарикам.")

    def resolve_choice(self, answer):
        if not self.current_choice: return
        block = self.current_choice.get(answer, {})
        for r, v in block.get("resources", {}).items():
            if r in self.resources: self.resources[r] += v
        for f, d in block.get("factions", {}).items():
            if f in self.factions: self.factions[f] += d
        if "hp" in block: self.hp += block["hp"]
        self.resolved_choices.add(self.current_choice["id"])
        self.current_choice = None
        if self.hp <= 0: self.status = "flushed"

    def maybe_trigger_choice(self):
        if self.turn % 5 == 0 and not self.current_choice:
            available = [c for c in self.choices if c["id"] not in self.resolved_choices]
            if available:
                self.current_choice = random.choice(available)

    def trigger_random_event(self):
        if not self.events: return
        e = random.choice(self.events)
        self.events_log.append(e["text"])
        for r, v in e.get("effect", {}).get("resources", {}).items():
            if r in self.resources: self.resources[r] += v
        for f, d in e.get("effect", {}).get("factions", {}).items():
            if f in self.factions: self.factions[f] += d
        if "hp" in e.get("effect", {}): self.hp += e["effect"]["hp"]
        if e.get("effect", {}).get("death"): self.status = "flushed"

    def update_quests(self):
        for q in self.quests:
            qid = q["id"]
            stage = self.quest_progress.get(qid, 0)
            if stage < len(q["stages"]):
                req = q["stages"][stage]["require"]
                if all(self.resources.get(k, 0) >= v for k, v in req.get("resources", {}).items()):
                    self.quest_progress[qid] = stage + 1
                    self.events_log.append(f"🌟 Квест {q['name']}: Этап {stage+1} выполнен!")
                    for k, v in q["stages"][stage].get("reward", {}).get("resources", {}).items():
                        self.resources[k] += v

    def get_state(self):
        return {
            "turn": self.turn,
            "resources": self.resources,
            "tech": self.tech,
            "hp": self.hp,
            "status": self.status,
            "factions": self.factions,
            "structures": self.structures,
            "events_log": self.events_log[-6:],
            "current_choice": self.current_choice,
            "unlocked_themes": self.unlocked_themes,
            "quest_progress": self.quest_progress,
            "active_crisis": self.active_crisis
        }
