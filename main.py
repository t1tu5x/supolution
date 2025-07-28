# main.py с квестами и прогрессбаром

import streamlit as st
from soup_game import SoupGame

st.set_page_config(page_title="🥣 Суполюция", page_icon="🥄", layout="centered")

if "game_data" in st.session_state:
    game = SoupGame()
    game.load_state(st.session_state["game_data"])
else:
    game = SoupGame()

state = game.get_state()
st.session_state.game_data = game.to_dict()

st.title("🥣 Суполюция")
st.markdown("Разумный суп. Микроцивилизация. Научный бой за выживание.")

# 💬 Ресурсы
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"🧪 **Ход:** `{state['turn']}` / `{game.max_turns}`")
    st.markdown(f"❤️ **Здоровье:** `{state['hp']}`")
with col2:
    for k, v in state["resources"].items():
        st.markdown(f"- {k.capitalize()}: `{v}`")

# 🔥 Квесты
st.markdown("### 📖 Квесты:")
if state["quest_progress"]:
    for qid, stage in state["quest_progress"].items():
        st.markdown(f"- 📘 `{qid}` — этап {stage}")
        pct = min(100, (stage / 3) * 100)
        st.progress(pct, text=f"{int(pct)}% завершено")
else:
    st.markdown("Нет активных квестов")

# 🧪 Технологии
st.markdown("### 🔬 Исследования:")
choices = game.get_upgrade_choices()
if not choices:
    st.info("Все технологии изучены.")
    if st.button("➡ Следующий ход"):
        game.next_turn()
        st.session_state.game_data = game.to_dict()
        st.rerun()
else:
    for tech in choices:
        with st.expander(f"🔹 {tech['name']}"):
            st.markdown(tech["desc"])
            deps = game.tech_tree.get(tech["name"], [])
            if deps:
                st.markdown(f"🔗 Требует: {', '.join(deps)}")
            st.markdown("🧠 Возможные последствия: фракции, квесты, сюжет")
            if st.button(f"🔬 Изучить: {tech['name']}"):
                game.apply_upgrade(tech["name"])
                game.trigger_tech_effects(tech["name"])
                game.next_turn()
                st.session_state.game_data = game.to_dict()
                st.rerun()

# ⚖️ Выборы
if state.get("current_choice"):
    ch = state["current_choice"]
    st.markdown(f"### ❓ {ch['text']}")
    cola, colb = st.columns(2)
    if cola.button("✅ Да"):
        game.resolve_choice("yes")
        game.choice_impact(ch["id"], "yes")
        game.next_turn()
        st.session_state.game_data = game.to_dict()
        st.rerun()
    if colb.button("❌ Нет"):
        game.resolve_choice("no")
        game.choice_impact(ch["id"], "no")
        game.next_turn()
        st.session_state.game_data = game.to_dict()
        st.rerun()

# 🏛️ Фракции
st.markdown("### 🏛️ Фракции:")
for name, rep in state["factions"].items():
    status = "👑 альянс" if rep >= 6 else "🟢 союз" if rep >= 4 else "🔴 враг" if rep <= -4 else "⚪ нейтрал"
    st.markdown(f"{status} **{name}** — `{rep}`")

# 📜 События
st.markdown("### 📜 Хроника:")
for log in reversed(state["events_log"]):
    icon = "🔬" if "техн" in log.lower() else "⚔️" if "атак" in log.lower() else "🎁" if "помощ" in log.lower() else "📍"
    st.markdown(f"- {icon} {log}")

# 🏗️ Постройки
with st.expander("🏗️ Постройки"):
    for s in state["structures"]:
        st.markdown(f"- 🧱 {s}")
    if not state["structures"]:
        st.markdown("_Ничего не построено._")

# 📘 Изученные технологии
with st.expander("📘 Изученные технологии"):
    for t in state["tech"]:
        st.markdown(f"- {t}")
    if not state["tech"]:
        st.markdown("_Пока пусто._")
